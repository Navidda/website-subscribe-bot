import asyncio
import logging
from datetime import datetime, timedelta
from enum import Enum, auto
from typing import List, Optional

import pytz
import requests
from telegram import Message, error
from telegram.ext import Application
from telegram.ext._utils.types import BD, BT, CCT, CD, JQ, UD

import aachen
import config
from queuing import QueueManager
from utils import PersistedList


class Path(str):
    pass


class State(Enum):
    NO_APPOINTMENT = auto()
    PENDING = auto()
    FREE_APPOINTMENT = auto()


STATE_TO_MSG = {
    State.FREE_APPOINTMENT: (
        "Appointment available on {earliest:%a %d.%m.%Y at %H:%M}!"
        " Book it quickly before someone else does:\n" + config.BOOKING_URL
    ),
    State.NO_APPOINTMENT: (
        "There are no free appointments in the next "
        f"{config.MAX_WAIT_DAYS} days anymore."
    ),
    State.PENDING: "Request Error! Contact Admin!",
}


class Requestor:
    def __init__(self):
        self.response: str = ""
        self.state: State = State.NO_APPOINTMENT
        self.pending: bool = False
        self.last_request_time: Optional[datetime] = None
        self.last_response_time: Optional[datetime] = None
        self.application: Application[BT, CCT, UD, CD, BD, JQ] = None
        self.queue_manager = QueueManager(send_message_callback=self.send_message)
        self.admin_ids = PersistedList("data/admin_ids.json")
        self.status_msgs: List[Message] = []
        self.debug: bool = False
        self.earliest: Optional[datetime] = None
        self.notified_earliest: Optional[datetime] = None

        self.logger = logging.getLogger(__name__)

    async def add_subscriber(self, chat_id: int):
        await self.queue_manager.join_queue(chat_id)

    def save_response(self, page: str):
        self.response = page
        with open("data/response.html", "w") as f:
            f.write(page)

    def perform_request_real(self):
        tz = pytz.timezone("Europe/Berlin")
        self.last_request_time = datetime.now(tz)

        try:
            earliest, self.response = aachen.earliest_slot(timeout=20)
        except requests.exceptions.RequestException as e:
            self.logger.info(f"Request Error: {e}")
            return State.PENDING
        except aachen.FlowError as e:
            self.logger.info(f"Flow Error: {e}")
            self.save_response(e.page)
            return State.PENDING
        except Exception as e:
            self.logger.exception(f"Unknown Error: {e}")
            return State.PENDING

        self.save_response(self.response)
        self.last_response_time = self.last_request_time
        self.earliest = earliest
        self.logger.info(f"Earliest slot: {earliest}")

        if earliest is None:
            return State.NO_APPOINTMENT
        deadline = datetime.now() + timedelta(days=config.MAX_WAIT_DAYS)
        return State.FREE_APPOINTMENT if earliest <= deadline else State.NO_APPOINTMENT

    def perform_request(self):
        return (
            State.FREE_APPOINTMENT
            if self.state == State.NO_APPOINTMENT
            else State.NO_APPOINTMENT
        )

    async def send_message(self, chat_id: int, text: str):
        times = 3
        exc = None
        for time in range(times):
            if time:
                print("times:", time + 1)
            try:
                if isinstance(text, Path):
                    with open(text, "rb") as f:
                        await self.application.bot.send_document(chat_id, f)
                else:
                    await self.application.bot.send_message(chat_id, text)
                return
            except error.Forbidden:
                self.queue_manager.quit_queue(chat_id)
                self.logger.info(f"Removed chat_id {chat_id} from chat_ids.json")
                return
            except Exception as e:
                exc = e
        self.logger.info(f"Error sending to user: {exc}")

    async def send_message_to_admins(self, text):
        for id in self.admin_ids.items:
            asyncio.create_task(self.send_message(id, text))

    async def update_status_messages(self, state):
        text = STATE_TO_MSG[state].format(earliest=self.earliest)
        for id in self.queue_manager.serving_list.items:
            asyncio.create_task(self.send_message(id, text))

    async def execute(self):
        state = await asyncio.to_thread(self.perform_request_real)
        if state == State.PENDING:
            if not self.pending:
                await self.send_message_to_admins(
                    f"Request Error! Last successful request: {self.last_response_time}"
                )
                if self.response:
                    await self.send_message_to_admins(Path("data/response.html"))
                self.pending = True
        else:
            self.pending = False
            # Notify on a state change, or when an even earlier slot shows up.
            earlier = (
                state == State.FREE_APPOINTMENT
                and self.notified_earliest is not None
                and self.earliest < self.notified_earliest
            )
            if state != self.state or earlier:
                if state == State.FREE_APPOINTMENT:
                    await self.send_message_to_admins(
                        f"Admin, new slot: {self.earliest}"
                    )
                await self.update_status_messages(state)
            self.notified_earliest = (
                self.earliest if state == State.FREE_APPOINTMENT else None
            )
            self.state = state

        await asyncio.sleep(config.PERIOD)
        asyncio.create_task(self.execute())
