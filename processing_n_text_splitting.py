'''from pathlib import Path
from typing import List
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
import logging   # standard Python logging

logger = logging.getLogger(__name__)   # uses log_file_Setup config

# ==========================================================
# PDF PROCESSOR
# ==========================================================
class PDFProcessor:
    """
    Responsible for:
    - Discovering PDF files
    - Loading PDFs into LangChain Document objects
    - Attaching metadata
    """

    def __init__(self, pdf_directory: str):
        self.pdf_directory = pdf_directory
        self.base_path = Path(__file__).resolve().parent

    def load_pdfs(self) -> List:
        all_documents = []
        pdf_dir = self.base_path / self.pdf_directory

        logger.info(f"Resolved PDF directory: {pdf_dir.resolve()}")

        if not pdf_dir.exists():
            logger.error(f"PDF directory does not exist: {pdf_dir}")
            return []

        pdf_files = list(pdf_dir.glob("**/*.pdf"))
        logger.info(f"Found {len(pdf_files)} PDF files")

        for pdf_file in pdf_files:
            logger.info(f"Processing PDF: {pdf_file.name}")
            try:
                loader = PyMuPDFLoader(str(pdf_file))
                documents = loader.load()

                for doc in documents:
                    doc.metadata["source_file"] = pdf_file.name
                    doc.metadata["file_type"] = "pdf"

                all_documents.extend(documents)
                logger.info(f"Loaded {len(documents)} pages from {pdf_file.name}")

            except Exception as e:
                logger.error(f"Failed to process {pdf_file.name}", exc_info=True)

        logger.info(f"Total PDF pages loaded: {len(all_documents)}")
        return all_documents

# ==========================================================
# TEXT SPLITTER
# ==========================================================
class TextSplitter:
    """
    Responsible for:
    - Splitting documents into chunks
    - Controlling chunk size & overlap
    """

    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            separators=["\n\n", "\n", " ", ""]
        )

    def split(self, documents: List) -> List:
        if not documents:
            logger.warning("No documents provided for splitting.")
            return []

        split_docs = self.splitter.split_documents(documents)
        logger.info(f"Split {len(documents)} documents into {len(split_docs)} chunks")

        if split_docs:
            logger.info(f"Example chunk preview: {split_docs[0].page_content[:200]}")
            logger.info(f"Example chunk metadata: {split_docs[0].metadata}")

        return split_docs

# ==========================================================
# PIPELINE HELPER
# ==========================================================
def load_and_split_pdfs(pdf_directory: str, chunk_size: int = 1000, chunk_overlap: int = 200) -> List:
    """
    Convenience helper function for the RAG pipeline
    """
    processor = PDFProcessor(pdf_directory)
    documents = processor.load_pdfs()

    splitter = TextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    return splitter.split(documents)
'''

from pathlib import Path
from typing import List
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
import logging

logger = logging.getLogger(__name__)

# ==========================================================
# PDF PROCESSOR
# ==========================================================
class PDFProcessor:
    """
    Discover PDFs, load into LangChain documents, attach metadata.
    """

    def __init__(self, pdf_directory: str):
        self.pdf_directory = pdf_directory
        self.base_path = Path(__file__).resolve().parent

    def load_pdfs(self) -> List:
        all_documents = []
        pdf_dir = self.base_path / self.pdf_directory

        logger.info(f"Resolved PDF directory: {pdf_dir.resolve()}")
        if not pdf_dir.exists():
            logger.error(f"PDF directory does not exist: {pdf_dir}")
            return []

        pdf_files = list(pdf_dir.glob("**/*.pdf"))
        logger.info(f"Found {len(pdf_files)} PDF files")

        for pdf_file in pdf_files:
            logger.info(f"Processing PDF: {pdf_file.name}")
            try:
                loader = PyMuPDFLoader(str(pdf_file))
                documents = loader.load()

                for doc in documents:
                    doc.metadata["source_file"] = pdf_file.name
                    doc.metadata["file_type"] = "pdf"

                all_documents.extend(documents)
                logger.info(f"Loaded {len(documents)} pages from {pdf_file.name}")

            except Exception as e:
                logger.error(f"Failed to process {pdf_file.name}", exc_info=True)

        logger.info(f"Total PDF pages loaded: {len(all_documents)}")
        return all_documents


# ==========================================================
# TEXT SPLITTER
# ==========================================================
class TextSplitter:
    """
    Split documents into chunks for embeddings.
    """

    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            separators=["\n\n", "\n", " ", ""]
        )

    def split(self, documents: List) -> List:
        if not documents:
            logger.warning("No documents provided for splitting.")
            return []

        split_docs = self.splitter.split_documents(documents)
        logger.info(f"Split {len(documents)} documents into {len(split_docs)} chunks")

        if split_docs:
            logger.info(f"Example chunk preview: {split_docs[0].page_content[:200]}")
            logger.info(f"Example chunk metadata: {split_docs[0].metadata}")

        return split_docs


# ==========================================================
# CONVENIENCE HELPER
# ==========================================================
def load_and_split_pdfs(pdf_directory: str, chunk_size: int = 1000, chunk_overlap: int = 200) -> List:
    processor = PDFProcessor(pdf_directory)
    documents = processor.load_pdfs()

    splitter = TextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    return splitter.split(documents)
