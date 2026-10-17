import logging
import os

TOKEN = os.getenv("BOT_TOKEN")

PERIOD = int(os.getenv("PERIOD", "60"))  # seconds between checks

# TEVIS booking flow for StädteRegion Aachen, Ausländeramt Aachen Arkaden,
# "Beratungs- und Antragsservice".
BASE_URL = os.getenv("BASE_URL", "https://termine.staedteregion-aachen.de/auslaenderamt")
BOOKING_URL = f"{BASE_URL}/select2?md=1"
MANDATOR = os.getenv("MANDATOR", "95")
CONCERN = os.getenv("CONCERN", "341")
LOCATION = os.getenv("LOCATION", "49")

# A slot counts as "free" if it is within this many days from now.
MAX_WAIT_DAYS = int(os.getenv("MAX_WAIT_DAYS", "30"))

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
