import streamlit as st
from ingestion.clone import clone_repo
from ingestion.parser import parse_repo
from ingestion.chunker import chunk_units
from ingestion.embedder import embed_chunks
from ingestion.graph_builder import build_call_graph
from retrieval.vector_search import store_chunks
from agent.orchestrator import run_agent

st.set_page_config(page_title="AI Codebase Agent", layout="wide")
st.title("🤖 AI Codebase Agent")
st.caption("Ask questions about a Python GitHub repository in plain English.")

if "graph" not in st.session_state:
    st.session_state.graph = None
if "indexed_repo" not in st.session_state:
    st.session_state.indexed_repo = None

with st.sidebar:
    st.header("Index a Repository")
    repo_url = st.text_input("GitHub repo URL", placeholder="https://github.com/user/repo.git")
    index_button = st.button("Index Repo")

    if index_button and repo_url:
        try:
            with st.spinner("Cloning repository..."):
                local_path = clone_repo(repo_url)

            with st.spinner("Parsing codebase..."):
                units = parse_repo(local_path)
                st.write(f"Found {len(units)} functions/classes.")

            with st.spinner("Building call graph..."):
                graph = build_call_graph(units)

            with st.spinner("Chunking and embedding (this may take a few minutes)..."):
                chunked = chunk_units(units)
                embedded = embed_chunks(chunked)
                store_chunks(embedded)

            st.session_state.graph = graph
            st.session_state.indexed_repo = repo_url
            st.success("Repo indexed! You can now ask questions.")
        except Exception as e:
            st.error(f"Indexing failed: {e}")

    if st.session_state.indexed_repo:
        st.info(f"Currently indexed:\n{st.session_state.indexed_repo}")

st.header("Ask a Question")

if st.session_state.graph is None:
    st.warning("Index a repo first using the sidebar, or reuse an already-indexed one below.")

    if st.button("Use already-indexed SimpleLogin repo"):
        try:
            with st.spinner("Loading existing index..."):
                units = parse_repo(r"storage/cloned_repos/app")
                st.session_state.graph = build_call_graph(units)
                st.session_state.indexed_repo = "https://github.com/simple-login/app.git"
            st.rerun()
        except Exception as e:
            st.error(f"Failed to load existing index: {e}")

question = st.text_input("Your question", placeholder="How does the app authenticate API requests?")
ask_button = st.button("Ask")

if ask_button and question:
    if st.session_state.graph is None:
        st.error("Please index a repo first.")
    else:
        try:
            with st.spinner("Thinking..."):
                answer = run_agent(question, st.session_state.graph)
            st.markdown("### Answer")
            st.markdown(answer)
        except Exception as e:
            st.error(f"Something went wrong: {e}")