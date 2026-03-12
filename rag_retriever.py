'''from typing import List, Dict, Any
import logging

from vector import VectorStore
from embedding_manager import EmbeddingManager

logger = logging.getLogger(__name__)

# ==========================================================
# RAG RETRIEVER
# ==========================================================
class RAGRetriever:
    """
    Responsible for retrieving relevant documents from the vector store
    given a query using embeddings from EmbeddingManager.
    """

    def __init__(self, vector_store: VectorStore, embedding_manager: EmbeddingManager):
        self.vector_store = vector_store
        self.embedding_manager = embedding_manager

    def retrieve(self, query: str, top_k: int = 5, score_threshold: float = 0.0) -> List[Dict[str, Any]]:
        """
        Retrieve top-k relevant documents for a query.

        Returns a list of dictionaries with:
        - id
        - content
        - metadata
        - similarity_score
        - distance
        - rank
        """
        logger.info(f"Retrieving documents for query: {query}")

        try:
            # Generate embedding for the query
            query_emb = self.embedding_manager.generate_embeddings([query])[0]

            # Query the vector store
            results = self.vector_store.collection.query(
                query_embeddings=[query_emb.tolist()],
                n_results=top_k
            )

            retrieved_docs = []

            if results.get("documents") and results["documents"][0]:
                documents = results["documents"][0]
                metadatas = results["metadatas"][0]
                distances = results["distances"][0]
                ids = results["ids"][0]

                for i, (doc_id, doc_text, metadata, dist) in enumerate(zip(ids, documents, metadatas, distances)):
                    similarity = 1 - dist
                    if similarity >= score_threshold:
                        retrieved_docs.append({
                            "id": doc_id,
                            "content": doc_text,
                            "metadata": metadata,
                            "similarity_score": similarity,
                            "distance": dist,
                            "rank": i + 1
                        })

                logger.info(f"Retrieved {len(retrieved_docs)} documents after filtering.")
            else:
                logger.info("No documents found for query.")

            return retrieved_docs

        except Exception as e:
            logger.error(f"Error during query retrieval: {e}", exc_info=True)
            return []
'''

from typing import List, Dict, Any
import logging
import re
import string

from vector import VectorStore
from embedding_manager import EmbeddingManager

logger = logging.getLogger(__name__)

# ==========================================================
# RAG RETRIEVER (HYBRID: VECTOR + KEYWORD)
# ==========================================================
class RAGRetriever:
    """
    Hybrid retriever:
    - Vector similarity search for semantic queries
    - Keyword fallback for short codes / acronyms (e.g., FSA017, IRRBB)
    """

    def __init__(self, vector_store: VectorStore, embedding_manager: EmbeddingManager):
        self.vector_store = vector_store
        self.embedding_manager = embedding_manager

    # ------------------------------------------------------
    # Utility helpers
    # ------------------------------------------------------
    @staticmethod
    def _normalize_text(text: str) -> str:
        """
        Normalize text for keyword matching: lowercase + strip punctuation
        """
        return text.lower().translate(str.maketrans("", "", string.punctuation))

    @staticmethod
    def _is_code_like(query: str) -> bool:
        """
        Detect regulatory codes / acronyms automatically.
        Returns True for:
          - short alphanumeric codes (FSA017, PRA110)
          - short acronyms (IRRBB, LCR, NSFR, HQLA)
          - queries <= 3 words (likely code / acronym)
        """
        cleaned = query.upper()
        return bool(re.search(r"[A-Z]{2,}\d*", cleaned)) or len(cleaned.split()) <= 3

    # ------------------------------------------------------
    # Main retrieval
    # ------------------------------------------------------
    def retrieve(
        self,
        query: str,
        top_k: int = 5,
        score_threshold: float = 0.2
    ) -> List[Dict[str, Any]]:

        logger.info(f"Retrieving documents for query: {query}")
        retrieved_docs: List[Dict[str, Any]] = []

        try:
            # --------------------------
            # 1. VECTOR SEARCH
            # --------------------------
            query_embedding = self.embedding_manager.generate_embeddings([query])[0]

            results = self.vector_store.collection.query(
                query_embeddings=[query_embedding.tolist()],
                n_results=top_k
            )

            if results.get("documents") and results["documents"][0]:
                documents = results["documents"][0]
                metadatas = results["metadatas"][0]
                distances = results["distances"][0]
                ids = results["ids"][0]

                for rank, (doc_id, doc_text, metadata, dist) in enumerate(
                    zip(ids, documents, metadatas, distances), start=1
                ):
                    similarity = 1 - dist
                    if similarity >= score_threshold:
                        retrieved_docs.append({
                            "id": doc_id,
                            "content": doc_text,
                            "metadata": metadata,
                            "similarity_score": similarity,
                            "distance": dist,
                            "rank": rank,
                            "retrieval_type": "vector"
                        })

            logger.info(f"Vector search returned {len(retrieved_docs)} documents after filtering.")

            # --------------------------
            # 2. KEYWORD FALLBACK
            # --------------------------
            if not retrieved_docs or self._is_code_like(query):
                logger.info("Activating keyword fallback search.")
                keyword_docs = self._keyword_search(query, limit=top_k)

                # Deduplicate by content
                seen_contents = {doc["content"] for doc in retrieved_docs}
                for doc in keyword_docs:
                    if doc["content"] not in seen_contents:
                        retrieved_docs.append(doc)

            logger.info(f"Final retrieved document count: {len(retrieved_docs)}")
            return retrieved_docs

        except Exception:
            logger.error("Error during query retrieval", exc_info=True)
            return []

    # ------------------------------------------------------
    # Keyword (lexical) search using Chroma
    # ------------------------------------------------------
    def _keyword_search(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Perform exact or substring match over stored documents.
        Automatically picks up short codes / acronyms from query.
        """
        normalized_query = self._normalize_text(query)
        matches: List[Dict[str, Any]] = []

        # Chroma 'get' supports only certain include items
        data = self.vector_store.collection.get(include=["documents", "metadatas", "embeddings"])

        documents = data.get("documents", [])
        metadatas = data.get("metadatas", [])
        ids = [f"doc_{i}" for i in range(len(documents))]  # fallback IDs if Chroma does not provide

        for doc_id, doc_text, metadata in zip(ids, documents, metadatas):
            normalized_doc = self._normalize_text(doc_text)
            if normalized_query in normalized_doc:
                matches.append({
                    "id": doc_id,
                    "content": doc_text,
                    "metadata": metadata,
                    "similarity_score": 1.0,
                    "distance": 0.0,
                    "rank": len(matches) + 1,
                    "retrieval_type": "keyword"
                })

            if len(matches) >= limit:
                break

        logger.info(f"Keyword search found {len(matches)} documents.")
        return matches
