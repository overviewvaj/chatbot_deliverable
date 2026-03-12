from pathlib import Path
from datetime import datetime
import logging

def setup_application_logging(app_name: str = "RAG_System") -> None:
    """
    Application-level logging setup.
    Call this ONCE at application startup.
    """

    base_dir = Path(__file__).parent
    log_dir = base_dir / "log_file"
    log_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file_path = log_dir / f"{app_name}_{timestamp}.log"

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        handlers=[
            logging.FileHandler(log_file_path, encoding="utf-8"),
            logging.StreamHandler()
        ]
    )

    logging.getLogger(__name__).info(
        f"Application logging initialized. Log file: {log_file_path}"
    )
