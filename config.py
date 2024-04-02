import logging
import os

from utils import PersistableDict

TOKEN = os.getenv("BOT_TOKEN")

PERIOD = 10  # seconds

default_raw_requests = {
    "url": [
        """curl 'https://termine.staedteregion-aachen.de/auslaenderamt/location?mdt=85&select_cnc=1&cnc-275=1&cnc-276=0' -X POST -H 'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0' -H 'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8' -H 'Accept-Language: en-US,en;q=0.5' -H 'Accept-Encoding: gzip, deflate, br' -H 'Content-Type: application/x-www-form-urlencoded' -H 'Origin: https://termine.staedteregion-aachen.de' -H 'DNT: 1' -H 'Sec-GPC: 1' -H 'Connection: keep-alive' -H 'Referer: https://termine.staedteregion-aachen.de/auslaenderamt/location?mdt=85&select_cnc=1&cnc-275=1&cnc-276=0' -H 'Cookie: tvo_session=ous27f64j5f3ac28mvbuleqn5d; tvo_cookie_accept=1' -H 'Upgrade-Insecure-Requests: 1' -H 'Sec-Fetch-Dest: document' -H 'Sec-Fetch-Mode: navigate' -H 'Sec-Fetch-Site: same-origin' -H 'Sec-Fetch-User: ?1' -H 'Pragma: no-cache' -H 'Cache-Control: no-cache' --data-raw 'loc=34&gps_lat=50.770786&gps_long=6.118778&select_location=Ausl%C3%A4nderamt+Aachen+-+Aachen+Arkaden%2C+Trierer+Stra%C3%9Fe+1%2C+Aachen+ausw%C3%A4hlen'""",
        """curl 'https://termine.staedteregion-aachen.de/auslaenderamt/suggest' -H 'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0' -H 'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8' -H 'Accept-Language: en-US,en;q=0.5' -H 'Accept-Encoding: gzip, deflate, br' -H 'Referer: https://termine.staedteregion-aachen.de/auslaenderamt/location?mdt=85&select_cnc=1&cnc-275=1&cnc-276=0' -H 'DNT: 1' -H 'Sec-GPC: 1' -H 'Connection: keep-alive' -H 'Cookie: tvo_session=ous27f64j5f3ac28mvbuleqn5d; tvo_cookie_accept=1' -H 'Upgrade-Insecure-Requests: 1' -H 'Sec-Fetch-Dest: document' -H 'Sec-Fetch-Mode: navigate' -H 'Sec-Fetch-Site: same-origin' -H 'Sec-Fetch-User: ?1' -H 'Pragma: no-cache' -H 'Cache-Control: no-cache'"""
    ]
}

RAW_REQUESTS = PersistableDict("data/raw_requests.json", default_raw_requests)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
