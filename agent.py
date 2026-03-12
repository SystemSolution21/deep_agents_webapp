# Import built-in libraries
import operator
import os
from typing import Annotated, Literal, Sequence, TypedDict

# Import langchain libraries
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI

# Import langgraph libraries
from langgraph.graph import END, START, StateGraph
from langgraph.prebuilt import ToolNode


# 1. Define State
class AgentState(TypedDict):
    # The 'messages' key is annotated with operator.add, so updates append to the list
    messages: Annotated[Sequence[BaseMessage], operator.add]


# 2. Define Tools
@tool
def fetch_revenue(company: str) -> str:
    """Fetches the annual revenue for a given company using a web search."""
    search = DuckDuckGoSearchRun()
    query = f"{company} annual revenue"
    try:
        return search.invoke(query)
    except Exception as e:
        return f"Could not fetch revenue data for {company}. Error: {str(e)}"


@tool
def calculate_growth(past_revenue: float, current_revenue: float) -> str:
    """Calculates the percentage growth rate given past and current revenue."""
    if past_revenue == 0:
        return "Cannot divide by zero (past revenue is 0)."
    growth = ((current_revenue - past_revenue) / past_revenue) * 100
    return f"{growth:.2f}%"


tools = [fetch_revenue, calculate_growth]
tool_node = ToolNode(tools)


# 3. Define LLM Model
def get_model():
    # Model will be instantiated inside the node so it uses the env variable lazily
    # fallback to gemini-2.5-flash as it is standard and fast
    model = os.getenv(key="LLM_MODEL", default="gemini-2.5-flash")
    llm = ChatGoogleGenerativeAI(model=model, temperature=0)
    return llm.bind_tools(tools)


# 4. Define Nodes
def call_model(state: AgentState):
    messages = state["messages"]
    model = get_model()
    response = model.invoke(messages)

    # If the model returns a list of blocks (common with newer Gemini versions), extract the text
    if isinstance(response.content, list):
        text_parts = []
        for part in response.content:
            if isinstance(part, dict) and "text" in part:
                text_parts.append(part["text"])
            elif isinstance(part, str):
                text_parts.append(part)
        if text_parts:
            response.content = "".join(text_parts)

    # Return a dict containing the state update
    return {"messages": [response]}


def should_continue(state: AgentState) -> Literal["tools", "__end__"]:
    messages = state["messages"]
    last_message = messages[-1]

    # If there are no tool calls, then we finish
    if getattr(last_message, "tool_calls", None):
        return "tools"

    return "__end__"


# 5. Build Graph
workflow = StateGraph(AgentState)

# Add nodes
workflow.add_node("agent", call_model)
workflow.add_node("tools", tool_node)

# Add edges
workflow.add_edge(START, "agent")
workflow.add_conditional_edges("agent", should_continue, ["tools", END])
workflow.add_edge("tools", "agent")

# Compile graph
graph = workflow.compile()

if __name__ == "__main__":
    # Test block
    from dotenv import load_dotenv

    load_dotenv()

    if os.getenv("GOOGLE_API_KEY"):
        inputs: AgentState = {
            "messages": [HumanMessage(content="What is the revenue of TechNova?")]
        }
        print("Testing agent...")
        for event in graph.stream(inputs, stream_mode="values"):
            message = event["messages"][-1]
            message.pretty_print()
    else:
        print("GOOGLE_API_KEY not set. Cannot run test.")
