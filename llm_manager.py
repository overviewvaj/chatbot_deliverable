import os
import logging
from typing import Optional
from dotenv import load_dotenv
from langchain_groq import ChatGroq

# Load environment variables
load_dotenv()

# Use the logger configured via setup_application_logging()
logger = logging.getLogger(__name__)

# ==========================================================
# LLM MANAGER
# ==========================================================
class LLMManager:
    """
    Manages initialization and access to the Groq LLM.
    """

    def __init__(
        self,
        model_name: str = "llama-3.1-8b-instant",
        temperature: float = 0.0,
        max_tokens: Optional[int] = None
    ):
        self.model_name = model_name
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.llm: Optional[ChatGroq] = None

        self._initialize_llm()

    # ------------------------------------------------------
    # Initialize Groq LLM
    # ------------------------------------------------------
    def _initialize_llm(self):
        groq_api_key = os.getenv("GROQ_API_KEY")

        if not groq_api_key:
            raise EnvironmentError("GROQ_API_KEY not found in environment variables.")

        try:
            self.llm = ChatGroq(
                groq_api_key=groq_api_key,
                model_name=self.model_name,
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            logger.info(
                f"Groq LLM initialized successfully | "
                f"Model: {self.model_name}, Temperature: {self.temperature}"
            )
        except Exception as e:
            logger.error("Failed to initialize Groq LLM", exc_info=True)
            raise

    # ------------------------------------------------------
    # Get LLM Instance
    # ------------------------------------------------------
    def get_llm(self) -> ChatGroq:
        """
        Returns the initialized LLM instance.
        """
        if not self.llm:
            raise RuntimeError("LLM not initialized.")
        return self.llm
