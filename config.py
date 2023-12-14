import logging
import os

from utils import PersistableDict


TOKEN = os.getenv("BOT_TOKEN")

DEFAULT_COOKIES = {
    "tvo_cookie_accept": "1",
    "tvo_session": "k08eg9ntk7pcki3hd293b0ucj0",
}

COOKIES = PersistableDict("data/cookies.json", DEFAULT_COOKIES)

HEADERS = {
    "Accept": 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    "Accept-Encoding": 'gzip, deflate, br',
    "Accept-Language": 'en-US,en;q=0.9,en-GB;q=0.8,de;q=0.7,de-DE;q=0.6',
    "Cache-Control": 'no-cache',
    "Connection": 'keep-alive',
    "Cookie": 'tvo_session=pja7ni9rfkhg9n7d8gc4jtpph0',
    "DNT": '1',
    "Host": 'termine.staedteregion-aachen.de',
    "Pragma": 'no-cache',
    "Referer": 'https://termine.staedteregion-aachen.de/auslaenderamt/location?mdt=78&select_cnc=1&cnc-204=0&cnc-205=0&cnc-198=0&cnc-201=0&cnc-202=0&cnc-227=0&cnc-232=0&cnc-203=0&cnc-196=0&cnc-190=0&cnc-185=0&cnc-187=0&cnc-188=0&cnc-186=0&cnc-192=0&cnc-191=1&cnc-194=0&cnc-197=0&cnc-193=0&cnc-183=0&cnc-184=0&cnc-195=0&cnc-200=0&cnc-228=0',
    "Sec-Fetch-Dest": 'document',
    "Sec-Fetch-Mode": 'navigate',
    "Sec-Fetch-Site": 'same-origin',
    "Sec-Fetch-User": '?1',
    "Upgrade-Insecure-Requests": '1',
    "User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0',
    "sec-ch-ua": '"Not_A Brand";v="8", "Chromium";v="120", "Microsoft Edge";v="120"',
    "sec-ch-ua-mobile": '?0',
    "sec-ch-ua-platform": '"Windows"',
}

PERIOD = 10  # seconds

URL = "https://termine.staedteregion-aachen.de/auslaenderamt/suggest"

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
