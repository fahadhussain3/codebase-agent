import os
from dotenv import load_dotenv

load_dotenv()

try:
    import streamlit as st
    COHERE_API_KEY = st.secrets.get("COHERE_API_KEY", os.getenv("COHERE_API_KEY"))
except (ImportError, FileNotFoundError):
    COHERE_API_KEY = os.getenv("COHERE_API_KEY")

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

STORAGE_DIR = "storage"
VECTOR_DB_PATH = os.path.join(STORAGE_DIR, "vector_db")
REPO_CLONE_PATH = os.path.join(STORAGE_DIR, "cloned_repos")

EMBED_MODEL = "embed-english-v3.0"
RERANK_MODEL = "rerank-english-v3.0"
CHAT_MODEL = "command-r"