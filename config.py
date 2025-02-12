import logging
import os

from utils import PersistableDict

TOKEN = os.getenv("BOT_TOKEN")

PERIOD = 10  # seconds

DEFAULT_RAW_REQUESTS = {"url": [""] * 10}
NO_APPOINTMENT_TEXT = os.environ["NO_APPOINTMENT_PATTERN"]
APPOINTMENT_TEXT = os.environ["APPOINTMENT_PATTERN"]
RAW_REQUESTS = PersistableDict("data/raw_requests.json", DEFAULT_RAW_REQUESTS)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
