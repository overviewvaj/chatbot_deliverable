import logging
from typing import Dict, Any, List

from rag_retriever import RAGRetriever
from llm_manager import LLMManager

logger = logging.getLogger(__name__)

# ==========================================================
# RAG PIPELINE
# ==========================================================
class RAGPipeline:
    """
    Combines a retriever and LLM to answer questions using RAG.
    """

    def __init__(self, retriever: RAGRetriever, llm_manager: LLMManager):
        self.retriever = retriever
        self.llm = llm_manager.get_llm()

    # ------------------------------------------------------
    # Core RAG method
    # ------------------------------------------------------
    def rag_advanced(
        self,
        query: str,
        top_k: int = 5,
        min_score: float = 0.2,
        return_context: bool = False
    ) -> Dict[str, Any]:
        """
        Run RAG query and return structured results.
        """
        results = self.retriever.retrieve(query, top_k=top_k, score_threshold=min_score)

        if not results:
            logger.info("No relevant documents found for query.")
            return {
                "answer": "No relevant information found.",
                "sources": [],
                "confidence": 0.0,
                "context": "" if return_context else None
            }

        context = "\n\n".join([doc['content'] for doc in results])
        sources = [
            {
                'source': doc['metadata'].get('source_file', 'unknown'),
                'page': doc['metadata'].get('page', 'unknown'),
                'score': doc['similarity_score'],
                'preview': doc['content'][:300] + '...'
            }
            for doc in results
        ]
        confidence = max([doc['similarity_score'] for doc in results])

        prompt = f"Use the following context to answer the question concisely.\nContext: {context}\n\nQuestion: {query}\nAnswer:"

        try:
            response = self.llm.invoke([prompt])
            answer_text = response.content
            logger.info(f"RAG query answered. Query: {query}")
            logger.debug(f"Full answer: {answer_text}")
        except Exception as e:
            answer_text = "Error generating answer."
            logger.error(f"Error invoking LLM: {e}", exc_info=True)

        output = {
            "answer": answer_text,
            "sources": sources,
            "confidence": confidence
        }
        if return_context:
            output['context'] = context

        return output

    # ------------------------------------------------------
    # Public method for UI / API
    # ------------------------------------------------------
    def ask(self, query: str) -> Dict[str, Any]:
        """
        Public function to query the RAG system.
        """
        return self.rag_advanced(
            query=query,
            top_k=3,
            min_score=0.1,
            return_context=False
        )
