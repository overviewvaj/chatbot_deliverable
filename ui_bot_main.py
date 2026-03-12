import streamlit as st
from pathlib import Path
from datetime import datetime
import logging

# =========================
# APPLICATION LOGGING
# =========================
from log_file_Setup import setup_application_logging
setup_application_logging("RAG_UI_Bot")
logger = logging.getLogger(__name__)
logger.info("Streamlit PDF RAG Chatbot application started.")

# =========================
# IMPORT MODULAR RAG PIPELINE COMPONENTS
# =========================
from processing_n_text_splitting import load_and_split_pdfs
from embedding_manager import EmbeddingManager
from vector import VectorStore
from rag_retriever import RAGRetriever
from llm_manager import LLMManager
from rag_pipeline import RAGPipeline

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
# SESSION STATE INIT
# =========================
if "messages" not in st.session_state:
    st.session_state.messages = []
    logger.info("Initialized empty chat history in session state.")

# =========================
# DISPLAY CHAT HISTORY
# =========================
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# =========================
# RAG PIPELINE INITIALIZATION
# =========================
@st.cache_resource
def initialize_rag_pipeline(pdf_dir="pdf"):
    # Load and split PDFs
    chunks = load_and_split_pdfs(pdf_dir)

    # Initialize embedding manager and vector store
    embedding_manager = EmbeddingManager()
    vector_store = VectorStore()
    texts = [doc.page_content for doc in chunks]
    embeddings = embedding_manager.generate_embeddings(texts)
    vector_store.add_documents(chunks, embeddings)

    # Create retriever and LLM
    retriever = RAGRetriever(vector_store, embedding_manager)
    llm_manager = LLMManager()

    # Initialize RAG pipeline
    pipeline = RAGPipeline(retriever, llm_manager)
    return pipeline

# Initialize pipeline once
rag_pipeline = initialize_rag_pipeline()

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
                result = rag_pipeline.ask(user_input)
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
