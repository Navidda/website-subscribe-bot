"""Scraper for the StädteRegion Aachen TEVIS appointment system.

Walks the booking flow (concern -> location -> time suggestions) and returns
the free slots listed in step 4 ("Terminvorschläge - Auswahl der Zeit").
"""
import re
from datetime import datetime
from typing import List, Optional, Tuple

import requests

import config

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/128.0 Safari/537.36"
    )
}

DAY_PATTERN = re.compile(r'<h3 title="[^"]*?(\d{2}\.\d{2}\.\d{4})"')
# Bookable slots are submit buttons; taken slots are disabled type="button"s.
SLOT_PATTERN = re.compile(
    r'<button type="submit" class="suggest_btn[^"]*"[^>]*title="(\d{2}:\d{2})"'
)


class FlowError(Exception):
    """The site did not return the time-suggestion page."""

    def __init__(self, message: str, page: str):
        super().__init__(message)
        self.page = page


def fetch_slots(timeout: float) -> Tuple[List[datetime], str]:
    """Returns (sorted free slots, html of the suggestion page)."""
    base = config.BASE_URL
    concern = {"mdt": config.MANDATOR, "select_cnc": "1", f"cnc-{config.CONCERN}": "1"}
    location = {"loc": config.LOCATION, "select_location": "Weiter"}

    with requests.Session() as s:
        s.headers.update(HEADERS)
        s.get(f"{base}/select2", params={"md": "1"}, timeout=timeout).raise_for_status()
        s.get(f"{base}/location", params=concern, timeout=timeout).raise_for_status()
        # Redirects to /suggest (step 4).
        r = s.post(f"{base}/location", params=concern, data=location, timeout=timeout)
        r.raise_for_status()
        page = r.text

    if "Schritt 4" not in page:
        raise FlowError("Unexpected page (session error or site changed)", page)
    return parse_slots(page), page


def parse_slots(page: str) -> List[datetime]:
    slots = []
    days = list(DAY_PATTERN.finditer(page))
    for i, day in enumerate(days):
        end = days[i + 1].start() if i + 1 < len(days) else len(page)
        for time in SLOT_PATTERN.findall(page, day.end(), end):
            slots.append(datetime.strptime(f"{day.group(1)} {time}", "%d.%m.%Y %H:%M"))
    return sorted(slots)


def earliest_slot(timeout: float) -> Tuple[Optional[datetime], str]:
    slots, page = fetch_slots(timeout)
    return (slots[0] if slots else None), page
