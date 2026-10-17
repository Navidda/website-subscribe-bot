"""Watch the Aachen Ausländeramt and DM a Telegram user from your own account.

Uses the Telegram user API (Telethon), not a bot. Needs TG_API_ID and TG_API_HASH
from https://my.telegram.org -> API development tools.

    python notify_user.py --login   # once, interactive: phone number + login code
    python notify_user.py           # watch forever

When the earliest slot is within MAX_WAIT_DAYS, TG_RECIPIENT gets the date and the
booking link. Another message is sent whenever the earliest slot within
MAX_WAIT_DAYS changes (an earlier one appears, or the sent one gets booked).
"""
import asyncio
import logging
import os
import sys
from datetime import datetime, timedelta

from telethon import TelegramClient

import aachen
import config

API_ID = int(os.environ["TG_API_ID"])
API_HASH = os.environ["TG_API_HASH"]
RECIPIENT = os.environ["TG_RECIPIENT"]  # e.g. @username
RECIPIENT_NAME = os.getenv("TG_RECIPIENT_NAME", "")
SESSION = "data/telegram_user"

logger = logging.getLogger("notify_user")


def message(slot: datetime) -> str:
    return (
        f"Hi {RECIPIENT_NAME}! The earliest appointment at the Ausländeramt Aachen "
        "(Beratungs- und Antragsservice, Aachen Arkaden, Trierer Straße 1) is "
        f"{slot:%A %d.%m.%Y at %H:%M}. You can book it here: {config.BOOKING_URL}"
    )


def first_in_window(slots):
    deadline = datetime.now() + timedelta(days=config.MAX_WAIT_DAYS)
    return slots[0] if slots and slots[0] <= deadline else None


async def watch(client: TelegramClient):
    notified = None
    while True:
        try:
            slots, _ = await asyncio.to_thread(aachen.fetch_slots, 20)
            logger.info(f"Earliest slot: {slots[0] if slots else None}")
            slot = first_in_window(slots)
            if slot and slot != notified:
                text = message(slot)
                if notified and notified not in slots:
                    text = "The previous appointment is already taken. " + text
                await client.send_message(RECIPIENT, text)
                await client.send_message("me", f"Sent to {RECIPIENT}: {slot}")
                logger.info(f"Notified {RECIPIENT}")
            notified = slot
        except Exception:
            logger.exception("Check failed")
        await asyncio.sleep(config.PERIOD)


async def main():
    client = TelegramClient(SESSION, API_ID, API_HASH)
    if "--login" in sys.argv:
        await client.start()  # prompts for phone and code
        me = await client.get_me()
        target = await client.get_entity(RECIPIENT)
        print(f"Logged in as {me.first_name}. Will notify {target.first_name} ({RECIPIENT}).")
        return
    await client.connect()
    if not await client.is_user_authorized():
        sys.exit("Not logged in. Run: python notify_user.py --login")
    async with client:
        await watch(client)


if __name__ == "__main__":
    asyncio.run(main())
