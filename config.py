import logging
import os

from utils import PersistableDict

TOKEN = os.getenv("BOT_TOKEN")

PERIOD = 10  # seconds

DEFAULT_RAW_REQUESTS = {"url": [""] * 10}
NO_APPOINTMENT_TEXT = os.getenv("NO_APPOINTMENT_TEXT")
APPOINTMENT_TEXT = os.getenv("APPOINTMENT_TEXT")
RAW_REQUESTS = PersistableDict("data/raw_requests.json", DEFAULT_RAW_REQUESTS)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
