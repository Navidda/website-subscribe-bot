import logging
import os

from utils import PersistableDict


TOKEN = os.getenv("BOT_TOKEN")

DEFAULT_COOKIES = {
    "cookie_accept": "1",
    "TVWebSession": "k08eg9ntk7pcki3hd293b0ucj0",
}

COOKIES = PersistableDict("data/cookies.json", DEFAULT_COOKIES)

HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "Accept-Language": "en-US,en-GB;q=0.9,en;q=0.8,fa;q=0.7",
    "Cache-Control": "max-age=0",
    "Connection": "keep-alive",
    "DNT": "1",
    "If-Modified-Since": "Sat, 29 Oct 2022 18:45:23 GMT",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36",
    "sec-ch-ua": '"Chromium";v="106", "Google Chrome";v="106", "Not;A=Brand";v="99"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
}

PARAMS = {
    "cnc-191": "1",
    "loc": "28",
}

PERIOD = 10  # seconds

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
