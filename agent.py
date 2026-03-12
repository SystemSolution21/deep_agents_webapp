import os
import operator
from typing import TypedDict, Annotated, Sequence, Literal
from pydantic import BaseModel, Field

from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, ToolMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, END, START
from langgraph.prebuilt import ToolNode
from langchain_core.tools import tool

# 1. Define State
class AgentState(TypedDict):
    # The 'messages' key is annotated with operator.add, so updates append to the list
    messages: Annotated[Sequence[BaseMessage], operator.add]


# 2. Define Tools
@tool
def fetch_revenue(company: str) -> str:
    """Fetches the annual revenue for a given company."""
    data = {
        "Acme Corp": "$100M",
        "TechNova": "$500M",
        "Globex": "$250M",
        "Stark Industries": "$1.5B",
        "Wayne Enterprises": "$2.3B"
    }
    # Simulate DB lookup
    return data.get(company, f"Revenue data for {company} not found.")

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
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)
    return llm.bind_tools(tools)


# 4. Define Nodes
def call_model(state: AgentState):
    messages = state["messages"]
    model = get_model()
    response = model.invoke(messages)
    # Return a dict containing the state update
    return {"messages": [response]}


def should_continue(state: AgentState) -> Literal["tools", END]:
    messages = state["messages"]
    last_message = messages[-1]
    
    # If there are no tool calls, then we finish
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "tools"
    
    return END


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
        inputs = {"messages": [HumanMessage(content="What is the revenue of TechNova?")]}
        print("Testing agent...")
        for event in graph.stream(inputs, stream_mode="values"):
            message = event["messages"][-1]
            message.pretty_print()
    else:
        print("GOOGLE_API_KEY not set. Cannot run test.")
