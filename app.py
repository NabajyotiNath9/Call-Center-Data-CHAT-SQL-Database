import streamlit as st
from pathlib import Path
from langchain.agents import create_sql_agent
from langchain.sql_database import SQLDatabase
from langchain.agents.agent_types import AgentType
from langchain.callbacks import StreamlitCallbackHandler
from langchain.agents.agent_toolkits import SQLDatabaseToolkit
from sqlalchemy import create_engine
import sqlite3
from langchain_groq import ChatGroq

# Page config
st.set_page_config(page_title="📊 Chat with Call Center Data", page_icon="🦜", layout="wide")
st.markdown("<h1 style='text-align: center;'>🦜 Chat with Call Center Data using LangChain + SQLite</h1>", unsafe_allow_html=True)
st.divider()

# Sidebar
with st.sidebar:
    st.markdown("### 🔑 Groq API Key")
    api_key = st.text_input("Enter your Groq API Key", type="password")

    st.markdown("### 📋 Options")
    show_table = st.checkbox("Preview Call Center Table")

    if st.button("🧹 Clear Chat History"):
        st.session_state["messages"] = []

# API Key guard
if not api_key:
    st.warning("⚠️ Please enter your Groq API Key in the sidebar to get started.")
    st.stop()

# Load LLM
llm = ChatGroq(groq_api_key=api_key, model_name="Llama3-8b-8192", streaming=True)

# DB Connection
@st.cache_resource(ttl="2h")
def get_sqlite_db():
    db_file_path = (Path(__file__).parent / "call_center.db").absolute()
    creator = lambda: sqlite3.connect(f"file:{db_file_path}?mode=ro", uri=True)
    return SQLDatabase(create_engine("sqlite:///", creator=creator))

db = get_sqlite_db()

# Show table preview
if show_table:
    try:
        with st.expander("📄 Preview of `CALL_CENTER` Table", expanded=True):
            preview_data = db.run("SELECT * FROM CALL_CENTER LIMIT 10")
            st.dataframe(preview_data, use_container_width=True)
    except Exception as e:
        st.error(f"Could not load table: {e}")

# Agent
toolkit = SQLDatabaseToolkit(db=db, llm=llm)
agent = create_sql_agent(
    llm=llm,
    toolkit=toolkit,
    verbose=True,
    agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
)

# Chat history
if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {"role": "assistant", "content": "👋 Hi! Ask me anything about the call center database 📞"}
    ]

# Display message history
for msg in st.session_state["messages"]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Chat input
user_input = st.chat_input("Ask something like: 'What's the average Answer Rate?'")

if user_input:
    st.session_state["messages"].append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        stream_handler = StreamlitCallbackHandler(st.container())
        try:
            response = agent.run(user_input, callbacks=[stream_handler])
        except Exception as e:
            response = f"⚠️ Something went wrong: `{e}`"

        st.session_state["messages"].append({"role": "assistant", "content": response})
        st.markdown(response)
