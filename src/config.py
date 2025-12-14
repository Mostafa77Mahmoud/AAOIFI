import os
from pathlib import Path

PDF_INPUT_DIR = Path("AAOIFI_Standards_Complete")
JSON_OUTPUT_DIR = Path("json_standards")
LOGS_DIR = Path("logs")
PROGRESS_FILE = Path("processing_progress.json")

PDF_INPUT_DIR.mkdir(exist_ok=True)
JSON_OUTPUT_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
GEMINI_MODEL = "gemini-2.5-flash"

MAX_INLINE_SIZE_MB = 10
MAX_RETRIES = 3
RETRY_DELAY_SECONDS = 5

STANDARD_ID_PREFIX = "SS"
TOTAL_STANDARDS = 61
