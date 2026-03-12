# 🤖 Data Analyst Deep Agent WebApp

A production-ready AI agent web application built with **LangGraph**, **Google GenAI (Gemini)**, and **Streamlit**. 

This application implements a ReAct (Reasoning and Acting) agent acting as a Data Analyst. It can autonomously decide when to use custom tools to fetch company revenues and calculate year-over-year growth, providing a transparent, interactive chat interface where users can watch the agent "think" and execute tools in real-time.

## ✨ Key Features
* **LangGraph State Machine**: Robust, stateful agent workflows using LangGraph's `StateGraph`.
* **Google Gemini Integration**: Leverages `gemini-2.5-flash` for high-speed, accurate tool-calling and reasoning.
* **Interactive Streamlit UI**: A clean, responsive chat interface with session history.
* **Tool Visibility**: Expandable UI elements that show exactly which tools the agent is calling and the results it receives.
* **Dynamic Configuration**: Easily set and update your Google API key directly from the UI sidebar.

---

## 📋 Development Prerequisites

Before running the application, ensure you have the following installed:

1. **Python 3.13+**
2. **[uv](https://docs.astral.sh/uv/)**: An extremely fast Python package and project manager.
3. **Google API Key**: You will need a Gemini API key. You can get one from [Google AI Studio](https://aistudio.google.com/app/apikey).

---

## 🗂️ Project Structure

```text
deep_agents_webapp/
├── agent.py           # Defines the LangGraph ReAct agent, state schema, and custom tools
├── app.py             # The Streamlit web application and chat UI logic
├── main.py            # Simple application entrypoint (launches Streamlit)
├── pyproject.toml     # Project metadata and dependencies (managed by uv)
├── uv.lock            # Lockfile for reproducible builds
└── .env               # (Optional) Environment variables file for API keys
```

### Component Breakdown
* **`agent.py`**: Contains the core logic. It defines `AgentState` for message history, implements `@tool` decorated functions (`fetch_revenue`, `calculate_growth`), binds them to the Gemini model, and compiles the workflow using `StateGraph`.
* **`app.py`**: Handles the frontend. It manages Streamlit's `st.session_state` to keep track of the conversation, renders chat bubbles, and cleanly displays LangChain `ToolMessage` and `AIMessage` tool calls.

---

## 🚀 App Execution

To run the application, follow these steps:

1. **(Optional) Set up your environment file:**
   Create a `.env` file in the root directory and add your API key so it pre-fills in the UI. You can also hide the tool call UI for production by setting `SHOW_TOOL_CALLS`:
   ```env
   GOOGLE_API_KEY=your_api_key_here
   SHOW_TOOL_CALLS=false  # Set to false to hide tool calling expanders in UI
   ```

2. **Run the application:**
   You can start the app using the `main.py` entrypoint via `uv`:
   ```bash
   uv run python main.py
   ```
   *Alternatively, you can run Streamlit directly:*
   ```bash
   uv run streamlit run app.py
   ```

3. **Access the Web UI:**
   Once running, Streamlit will automatically open your default browser to `http://localhost:8501`.

---

## 🔄 Web UI Workflows

Here is how you interact with the application:

1. **Configuration**: Open the left sidebar. If you haven't set a `.env` file, paste your Google API Key into the input field. The app will immediately validate and securely store it in the environment session.
2. **Chatting**: Type a question into the chat input box at the bottom. Try a prompt like:
   * *"What is the revenue of TechNova?"*
   * *"Can you compare the growth between Acme Corp and Globex if Acme used to make $50M and Globex used to make $200M?"*
3. **Agent Execution**: The UI will display a spinner saying "Agent is thinking...". 
4. **Tool Inspection**: If the agent decides it needs to fetch external data or do math, it will trigger a tool call. You will see an expandable `🛠️ Calling Tool: <tool_name>` widget. Click it to see the exact arguments the agent passed!
5. **Final Response**: Once the agent has gathered enough information, it synthesizes a final natural language response and displays it in the chat.