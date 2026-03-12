import streamlit as st
import os
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from agent import graph

# Load environment variables (e.g., GOOGLE_API_KEY from .env)
load_dotenv()

# Streamlit config
st.set_page_config(page_title="Data Analyst Deep Agent", page_icon="🤖", layout="wide")

st.title("Data Analyst Deep Agent 🤖")
st.markdown("Ask me about company revenues and growth. I have access to tools!")

# Sidebar for configuration
with st.sidebar:
    st.header("Configuration")
    
    # Pre-fill API key from environment if it exists
    env_api_key = os.getenv("GOOGLE_API_KEY", "")
    
    # Input for Google API Key
    api_key = st.text_input("Google API Key", type="password", value=env_api_key)
    
    if api_key:
        os.environ["GOOGLE_API_KEY"] = api_key
        st.success("API Key successfully set!")
    else:
        st.warning("Please enter your Google API Key to continue.")
        st.markdown("[Get a Gemini API Key](https://aistudio.google.com/app/apikey)")

# Initialize session state for chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

def display_chat_message(msg):
    """Helper to display a single message appropriately."""
    if isinstance(msg, HumanMessage):
        with st.chat_message("user"):
            st.write(msg.content)
            
    elif isinstance(msg, AIMessage):
        with st.chat_message("assistant"):
            if msg.content:
                st.write(msg.content)
            
            # Show tool calls nicely
            if hasattr(msg, "tool_calls") and msg.tool_calls:
                for tc in msg.tool_calls:
                    with st.expander(f"🛠️ Calling Tool: `{tc['name']}`"):
                        st.json(tc['args'])
                        
    elif isinstance(msg, ToolMessage):
        # We don't make a new chat_message for ToolMessage because it visually
        # clutters the interface as a separate persona. Instead, we can show it 
        # as a small detail or expander, or rely on the AI message's tool_call expander.
        with st.chat_message("assistant", avatar="⚙️"):
            with st.expander(f"📥 Tool Result ({msg.name})"):
                st.write(msg.content)

# Display chat history from session state
for msg in st.session_state.messages:
    display_chat_message(msg)

# Handle user input
if prompt := st.chat_input("E.g. What is the revenue of Acme Corp?"):
    if not os.environ.get("GOOGLE_API_KEY"):
        st.error("Please enter your Google API Key in the sidebar.")
        st.stop()
        
    # Append user message and display it immediately
    user_msg = HumanMessage(content=prompt)
    st.session_state.messages.append(user_msg)
    display_chat_message(user_msg)
    
    with st.chat_message("assistant"):
        with st.spinner("Agent is thinking..."):
            try:
                # Run the LangGraph agent
                # We use stream_mode="values" to get the full state back at each step
                final_state = None
                
                # Create a placeholder to stream UI updates if desired
                # But typically LangGraph stream yields complete states per node execution
                for event in graph.stream({"messages": st.session_state.messages}, stream_mode="values"):
                    final_state = event
                    # We could render intermediate steps dynamically here
                
                if final_state and "messages" in final_state:
                    # Update session state with ALL messages including tool calls and responses
                    # This ensures the agent remembers context
                    st.session_state.messages = final_state["messages"]
                    
                    # Rerender to show the newly generated messages properly
                    # Streamlit will re-run the script from top to bottom
                    st.rerun()
                    
            except Exception as e:
                st.error(f"Error executing agent: {e}")
