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

# App Config
st.set_page_config(page_title="LangChain: Chat with SQL DB", page_icon="🦜")
st.title("🦜 LangChain: Chat with SQLite Database")

# Get Groq API Key
api_key = st.sidebar.text_input("Enter Groq API Key", type="password")

if not api_key:
    st.warning("Please enter your Groq API Key to continue.")
    st.stop()

# Initialize LLM
llm = ChatGroq(groq_api_key=api_key, model_name="Llama3-8b-8192", streaming=True)

@st.cache_resource(ttl="2h")
def get_sqlite_db():
    db_file_path = (Path(__file__).parent / "call_center.db").absolute()
    creator = lambda: sqlite3.connect(f"file:{db_file_path}?mode=ro", uri=True)
    return SQLDatabase(create_engine("sqlite:///", creator=creator))

# Connect to SQLite DB
db = get_sqlite_db()

# SQL Agent Setup
toolkit = SQLDatabaseToolkit(db=db, llm=llm)
agent = create_sql_agent(
    llm=llm,
    toolkit=toolkit,
    verbose=True,
    agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
)

# Chat Session Setup
if "messages" not in st.session_state or st.sidebar.button("Clear chat history"):
    st.session_state["messages"] = [{"role": "assistant", "content": "Ask me anything about the call center data 📊"}]

for msg in st.session_state["messages"]:
    st.chat_message(msg["role"]).write(msg["content"])

user_input = st.chat_input("Ask a question about the database...")

if user_input:
    st.session_state["messages"].append({"role": "user", "content": user_input})
    st.chat_message("user").write(user_input)

    with st.chat_message("assistant"):
        stream_handler = StreamlitCallbackHandler(st.container())
        try:
            response = agent.run(user_input, callbacks=[stream_handler])
        except Exception as e:
            response = f"⚠️ Error: {str(e)}"
        st.session_state["messages"].append({"role": "assistant", "content": response})
        st.write(response)
