'''import os
import uuid
from typing import List, Dict, Any
import numpy as np
import chromadb
from chromadb.config import Settings
import logging

logger = logging.getLogger(__name__)

# ==========================================================
# VECTOR STORE
# ==========================================================
class VectorStore:
    """
    Handles persistent vector storage using ChromaDB.
    """

    def __init__(self, collection_name: str = "pdf_documents", persist_directory: str = "../data/vector_store"):
        self.collection_name = collection_name
        self.persist_directory = persist_directory
        self.client = None
        self.collection = None
        self._initialize_store()

    def _initialize_store(self):
        """
        Initializes the ChromaDB client and collection.
        """
        try:
            os.makedirs(self.persist_directory, exist_ok=True)
            self.client = chromadb.PersistentClient(path=self.persist_directory)
            self.collection = self.client.get_or_create_collection(
                name=self.collection_name,
                metadata={"description": "PDF Document Embeddings for RAG"}
            )
            logger.info(
                f"Vector store initialized: {self.collection_name}. Existing docs: {self.collection.count()}"
            )
        except Exception as e:
            logger.error(f"Error initializing vector store: {e}", exc_info=True)
            raise

    def add_documents(self, documents: List[Dict[str, Any]], embeddings: np.ndarray):
        """
        Adds documents and their embeddings to the vector store.
        """
        if len(documents) != len(embeddings):
            raise ValueError("Document count must match embeddings count.")

        ids, metadatas, documents_text, embeddings_list = [], [], [], []

        for i, (doc, emb) in enumerate(zip(documents, embeddings)):
            doc_id = f"doc_{uuid.uuid4().hex[:8]}_{i}"
            ids.append(doc_id)

            metadata = dict(doc.metadata)
            metadata['doc_index'] = i
            metadata['content_length'] = len(doc.page_content)
            metadatas.append(metadata)

            documents_text.append(doc.page_content)
            embeddings_list.append(emb.tolist())

        try:
            self.collection.add(
                ids=ids,
                embeddings=embeddings_list,
                metadatas=metadatas,
                documents=documents_text
            )
            logger.info(
                f"Added {len(documents)} documents to vector store. Total now: {self.collection.count()}"
            )
        except Exception as e:
            logger.error(f"Error adding documents to vector store: {e}", exc_info=True)
            raise
'''

# vector.py
'''import os
import uuid
import hashlib
from typing import List, Dict, Any
import numpy as np
import chromadb
from chromadb.config import Settings
import logging

logger = logging.getLogger(__name__)

class VectorStore:
    """
    Handles persistent vector storage using ChromaDB.
    Supports reset / deduplication.
    """

    def __init__(self, collection_name: str = "pdf_documents", persist_directory: str = "../data/vector_store", reset: bool = False):
        self.collection_name = collection_name
        self.persist_directory = persist_directory
        self.client = None
        self.collection = None
        self._initialize_store(reset)

    def _initialize_store(self, reset: bool):
        os.makedirs(self.persist_directory, exist_ok=True)
        self.client = chromadb.PersistentClient(path=self.persist_directory)

        if reset:
            try:
                self.client.delete_collection(self.collection_name)
                logger.info(f"Vector store reset: {self.collection_name}")
            except Exception:
                pass  # ignore if collection doesn't exist

        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"description": "PDF Document Embeddings for RAG"}
        )
        logger.info(f"Vector store initialized: {self.collection_name}. Existing docs: {self.collection.count()}")

    @staticmethod
    def _doc_hash(text: str) -> str:
        return hashlib.md5(text.encode("utf-8")).hexdigest()

    def add_documents(self, documents: List[Dict[str, Any]], embeddings: np.ndarray):
        ids, metadatas, documents_text, embeddings_list = [], [], [], []

        for i, (doc, emb) in enumerate(zip(documents, embeddings)):
            doc_text = doc.page_content
            doc_id = f"{self._doc_hash(doc_text)}_{i}"
            ids.append(doc_id)

            metadata = dict(doc.metadata)
            metadata['doc_index'] = i
            metadata['content_length'] = len(doc_text)
            metadatas.append(metadata)

            documents_text.append(doc_text)
            embeddings_list.append(emb.tolist())

        try:
            self.collection.add(
                ids=ids,
                embeddings=embeddings_list,
                metadatas=metadatas,
                documents=documents_text
            )
            logger.info(f"Added {len(documents)} documents to vector store. Total now: {self.collection.count()}")
        except Exception as e:
            logger.error(f"Error adding documents to vector store: {e}", exc_info=True)
            raise
'''
import os
import uuid
from typing import List, Dict, Any
import chromadb
from chromadb.config import Settings
import logging

logger = logging.getLogger(__name__)

# ==========================================================
# VECTOR STORE
# ==========================================================
class VectorStore:
    """
    Handles persistent vector storage using ChromaDB.
    """

    def __init__(self, collection_name: str = "pdf_documents", persist_directory: str = "../data/vector_store"):
        self.collection_name = collection_name
        self.persist_directory = persist_directory
        self.client = None
        self.collection = None
        self._initialize_store()

    def _initialize_store(self):
        try:
            os.makedirs(self.persist_directory, exist_ok=True)
            self.client = chromadb.PersistentClient(path=self.persist_directory)
            self.collection = self.client.get_or_create_collection(
                name=self.collection_name,
                metadata={"description": "PDF Document Embeddings for RAG"}
            )
            logger.info(
                f"Vector store initialized: {self.collection_name}. Existing docs: {self.collection.count()}"
            )
        except Exception as e:
            logger.error(f"Error initializing vector store: {e}", exc_info=True)
            raise

    def add_documents(self, documents: List[Dict[str, Any]], embeddings):
        if len(documents) != len(embeddings):
            raise ValueError("Document count must match embeddings count.")

        ids, metadatas, documents_text, embeddings_list = [], [], [], []

        for i, (doc, emb) in enumerate(zip(documents, embeddings)):
            doc_id = f"doc_{uuid.uuid4().hex[:8]}_{i}"
            ids.append(doc_id)
            metadata = dict(doc.metadata)
            metadata['doc_index'] = i
            metadata['content_length'] = len(doc.page_content)
            metadatas.append(metadata)
            documents_text.append(doc.page_content)
            embeddings_list.append(emb.tolist())

        try:
            self.collection.add(
                ids=ids,
                embeddings=embeddings_list,
                metadatas=metadatas,
                documents=documents_text
            )
            logger.info(f"Added {len(documents)} documents. Total now: {self.collection.count()}")
        except Exception as e:
            logger.error(f"Error adding documents to vector store: {e}", exc_info=True)
            raise
