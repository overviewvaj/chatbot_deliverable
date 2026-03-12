import streamlit as st
from pathlib import Path
from datetime import datetime
import logging

# =========================
# LOGGING SETUP
# =========================
from log_file_Setup import setup_application_logging
setup_application_logging("RAG_UI_Bot")
logger = logging.getLogger(__name__)
logger.info("Streamlit PDF RAG Chatbot application started.")

# =========================
# STREAMLIT CONFIG
# =========================
st.set_page_config(
    page_title="PDF RAG Chatbot",
    page_icon="📄",
    layout="centered"
)

st.title("📄 PDF RAG Chatbot")
st.caption("Ask questions based only on the uploaded PDF documents")

# =========================
# IMPORT MODULAR COMPONENTS
# =========================
from processing_n_text_splitting import load_and_split_pdfs
from embedding_manager import EmbeddingManager
from vector import VectorStore
from rag_retriever import RAGRetriever
from llm_manager import LLMManager
from rag_pipeline import RAGPipeline

# =========================
# VECTOR STORE CONFIG
# =========================
VECTOR_STORE_PATH = "../data/vector_store"
PDF_DIR = "pdf"

# =========================
# SESSION STATE INIT
# =========================
if "messages" not in st.session_state:
    st.session_state.messages = []
if "rag_pipeline" not in st.session_state:
    st.session_state.rag_pipeline = None
if "vector_store" not in st.session_state:
    st.session_state.vector_store = None

# =========================
# REFRESH VECTOR STORE BUTTON
# =========================
refresh_clicked = st.button("🔄 Refresh Vector Store")

# =========================
# INITIALIZE RAG PIPELINE
# =========================
@st.cache_resource(show_spinner=False)
def initialize_rag_pipeline(refresh: bool = False):
    # Initialize embedding manager
    embedding_manager = EmbeddingManager()

    # Initialize persistent vector store
    vector_store = VectorStore(persist_directory=VECTOR_STORE_PATH)

    # Reprocess PDFs if refresh requested or vector store is empty
    if refresh or vector_store.collection.count() == 0:
        st.info("Processing PDFs and updating vector store...")
        logger.info("Refreshing vector store...")

        chunks = load_and_split_pdfs(PDF_DIR)
        texts = [doc.page_content for doc in chunks]
        embeddings = embedding_manager.generate_embeddings(texts)
        vector_store.add_documents(chunks, embeddings)
        st.success("Vector store updated successfully.")
        logger.info("Vector store refreshed successfully.")

    # Create retriever and LLM
    retriever = RAGRetriever(vector_store, embedding_manager)
    llm_manager = LLMManager()
    pipeline = RAGPipeline(retriever, llm_manager)

    return pipeline, vector_store

# Initialize pipeline
st.session_state.rag_pipeline, st.session_state.vector_store = initialize_rag_pipeline(refresh_clicked)

# =========================
# DISPLAY CHAT HISTORY
# =========================
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# =========================
# USER INPUT
# =========================
user_input = st.chat_input("Ask a question...")

if user_input:
    logger.info(f"User question received: {user_input}")

    # Show user message
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # =========================
    # RAG RESPONSE
    # =========================
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                result = st.session_state.rag_pipeline.ask(user_input)
                answer = result["answer"]

                st.markdown(answer)
                logger.info(f"Assistant answer generated successfully for question: {user_input}")
                logger.debug(f"Assistant full answer: {answer}")

            except Exception as e:
                error_message = "An error occurred while generating the response."
                st.error(error_message)
                logger.error("Error during RAG response generation", exc_info=True)
                answer = error_message

    # Save assistant message
    st.session_state.messages.append({"role": "assistant", "content": answer})
    logger.info(f"Assistant response saved to chat history. Question: {user_input} | Answer: {answer}")
