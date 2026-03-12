import logging
from datetime import datetime
from pathlib import Path

def setup_logger(logger_name: str = "RAG_Logger") -> logging.Logger:
    """
    Sets up and returns a logger with timestamped file logging.
    """

    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.INFO)

    # Prevent duplicate handlers (important for Streamlit)
    if logger.handlers:
        return logger

    # Create log directory
    base_dir = Path(__file__).parent
    log_dir = base_dir / "log file"
    log_dir.mkdir(parents=True, exist_ok=True)

    # Timestamped log file name
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file_path = log_dir / f"RAG_Log_File_{timestamp}.log"

    # File handler
    file_handler = logging.FileHandler(log_file_path, encoding="utf-8")
    file_handler.setLevel(logging.INFO)

    # Console handler (optional but useful)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    # Formatter
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    logger.info("Logger initialized")
    logger.info(f"Log file created at: {log_file_path}")

    return logger
