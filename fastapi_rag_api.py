from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
import logging
from fastapi.middleware.cors import CORSMiddleware

# =========================
# Logging setup
# =========================
from log_file_Setup import setup_application_logging
setup_application_logging("RAG_API")
logger = logging.getLogger(__name__)

# =========================
# Import RAG pipeline modules
# =========================
from processing_n_text_splitting import load_and_split_pdfs
from embedding_manager import EmbeddingManager
from vector import VectorStore
from rag_retriever import RAGRetriever
from llm_manager import LLMManager
from rag_pipeline import RAGPipeline

# =========================
# FastAPI app setup
# =========================
app = FastAPI(title="PDF RAG API")

# Allow CORS for .NET frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or restrict to your .NET domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================
# Request models
# =========================
class QueryRequest(BaseModel):
    query: str
    top_k: Optional[int] = 3
    min_score: Optional[float] = 0.1
    return_context: Optional[bool] = False

class AdminRefreshRequest(BaseModel):
    secret_key: str  # simple admin authentication

# =========================
# Global RAG pipeline variables
# =========================
VECTOR_STORE_PATH = "../data/vector_store"
PDF_DIR = "pdf"

embedding_manager = EmbeddingManager()
vector_store = VectorStore(persist_directory=VECTOR_STORE_PATH)

# Initialize retriever and LLM
retriever = RAGRetriever(vector_store, embedding_manager)
llm_manager = LLMManager()
rag_pipeline = RAGPipeline(retriever, llm_manager)

# =========================
# Public endpoint: Query RAG
# =========================
@app.post("/query")
def query_rag(request: QueryRequest):
    logger.info(f"Query received: {request.query}")
    try:
        result = rag_pipeline.rag_advanced(
        query=request.query,
        top_k=request.top_k,
        min_score=request.min_score,
        return_context=request.return_context
        )

        # Log the full result
        logger.info(f"Query result (full): {result}")

        # Only return the answer in the API response
        return {"answer": result.get("answer", "No answer found")}
    
        #result = rag_pipeline.rag_advanced(
        #    query=request.query,
        #    top_k=request.top_k,
        #    min_score=request.min_score,
        #    return_context=request.return_context
        #)
        #return result
    except Exception as e:
        logger.error(f"Error processing query: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Error processing query.")

# =========================
# Admin endpoint: Refresh Vector Store
# =========================
ADMIN_SECRET = "YOUR_SECURE_ADMIN_KEY"  # change this

@app.post("/admin/refresh")
def refresh_vector_store(request: AdminRefreshRequest):
    if request.secret_key != ADMIN_SECRET:
        logger.warning("Unauthorized vector store refresh attempt")
        raise HTTPException(status_code=403, detail="Unauthorized")

    try:
        logger.info("Admin requested vector store refresh")
        # Reprocess PDFs and update embeddings
        chunks = load_and_split_pdfs(PDF_DIR)
        texts = [doc.page_content for doc in chunks]
        embeddings = embedding_manager.generate_embeddings(texts)
        vector_store.add_documents(chunks, embeddings)
        logger.info("Vector store refreshed successfully")
        return {"status": "success", "message": "Vector store refreshed successfully."}
    except Exception as e:
        logger.error(f"Error refreshing vector store: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to refresh vector store.")
    
# =========================
# Health check endpoint
# =========================
@app.get("/health")
def health_check():
    """
    Simple health check endpoint for RAG API.
    Returns 200 if the service is alive.
    """
    try:
        # Optionally, you could do a lightweight operation here
        if rag_pipeline:
            return {"status": "ok"}
    except Exception as e:
        logger.error(f"Health check failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="RAG service unavailable")

