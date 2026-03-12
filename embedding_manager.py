'''from typing import List
import numpy as np
from sentence_transformers import SentenceTransformer
import logging  # standard Python logging

logger = logging.getLogger(__name__)  # uses log_file_Setup config

class EmbeddingManager:
    """
    Handles loading a SentenceTransformer model and generating embeddings.
    """

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model_name = model_name
        self.model = None
        self._load_model()

    def _load_model(self):
        try:
            logger.info(f"Loading SentenceTransformer model: {self.model_name}")
            self.model = SentenceTransformer(self.model_name)
            logger.info(
                f"Model loaded successfully. Embedding dimensions: {self.model.get_sentence_embedding_dimension()}"
            )
        except Exception as e:
            logger.error(f"Error loading embedding model: {e}", exc_info=True)
            raise

    def generate_embeddings(self, texts: List[str]) -> np.ndarray:
        if not self.model:
            raise ValueError("Embedding model not loaded.")

        logger.info(f"Generating embeddings for {len(texts)} texts...")
        embeddings = self.model.encode(texts, show_progress_bar=True)
        logger.info(f"Generated embeddings with shape {embeddings.shape}")
        return embeddings
'''

from typing import List
import numpy as np
from sentence_transformers import SentenceTransformer
import logging

logger = logging.getLogger(__name__)

class EmbeddingManager:
    """
    Handles SentenceTransformer embeddings.
    """

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model_name = model_name
        self.model = None
        self._load_model()

    def _load_model(self):
        try:
            logger.info(f"Loading SentenceTransformer model: {self.model_name}")
            self.model = SentenceTransformer(self.model_name)
            logger.info(
                f"Model loaded successfully. Embedding dimensions: {self.model.get_sentence_embedding_dimension()}"
            )
        except Exception as e:
            logger.error(f"Error loading embedding model: {e}", exc_info=True)
            raise

    def generate_embeddings(self, texts: List[str]) -> np.ndarray:
        if not self.model:
            raise ValueError("Embedding model not loaded.")

        logger.info(f"Generating embeddings for {len(texts)} texts...")
        embeddings = self.model.encode(texts, show_progress_bar=True)
        logger.info(f"Generated embeddings with shape {embeddings.shape}")
        return embeddings
