import asyncio
import logging
from datetime import datetime
from enum import Enum, auto
import re
import subprocess
from typing import List, Optional

import pytz
import requests
from telegram import Message, error
from telegram.ext import Application
from telegram.ext._utils.types import BD, BT, CCT, CD, JQ, UD

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
        "New appointment slots are available!"
        " Book them quickly before that they are booked by someone else!"
    ),
    State.NO_APPOINTMENT: "There is no free appointments anymore.",
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

        self.logger = logging.getLogger(__name__)

    async def add_subscriber(self, chat_id: int):
        await self.queue_manager.join_queue(chat_id)

    def perform_request_real(self):
        state = State.PENDING

        tz = pytz.timezone("Europe/Berlin")
        self.last_request_time = datetime.now(tz)

        try:
            for i in range(len(config.RAW_REQUESTS.data["url"])):
                if not config.RAW_REQUESTS.data["url"][i]:
                    continue
                self.completed_process = subprocess.run(
                    config.RAW_REQUESTS.data["url"][i],
                    shell=True,
                    check=True,
                    capture_output=True,
                    timeout=config.PERIOD / 2, # timeout 5 seconds
                )
                self.response = self.completed_process.stdout.decode("utf-8")
        except requests.exceptions.Timeout:
            self.logger.info("Request Timeout!")
            return State.PENDING
        except requests.exceptions.ConnectionError:
            self.logger.info("Connection Error!")
            return State.PENDING
        except requests.exceptions.RequestException as e:
            self.logger.info(f"Request Error: {e}")
            return State.PENDING
        except Exception as e:
            self.logger.exception(f"Unknown Error: {e}")
            return State.PENDING

        if not self.response:
            self.logger.info("Empty response!")
            return State.PENDING
        else:
            with open("data/response.html", "w") as f:
                f.write(self.response)
                self.last_response_time = self.last_request_time

        no_appointment_pattern = re.compile(config.NO_APPOINTMENT_TEXT, re.IGNORECASE)
        appointment_pattern = re.compile(config.APPOINTMENT_TEXT, re.IGNORECASE)

        if re.search(no_appointment_pattern, self.response):
            state = State.NO_APPOINTMENT
        # elif re.search(appointment_pattern, self.response):
        else:
            state = State.FREE_APPOINTMENT
            # state = State.PENDING

        return state

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
        for id in self.queue_manager.serving_list.items:
            asyncio.create_task(self.send_message(id, STATE_TO_MSG[state]))

    async def execute(self):
        state = self.perform_request_real()
        if state == State.PENDING and not self.pending:
            if self.last_request_time == self.last_response_time:
                await self.send_message_to_admins(
                    "Cannot parse response or error code!"
                )
                await self.send_message_to_admins(Path("data/response.html"))
            else:
                await self.send_message_to_admins(
                    f"Request Error! Last successful request: {self.last_response_time}"
                )
            self.pending = True
        elif state != self.state:
            if state == State.FREE_APPOINTMENT:
                await self.send_message_to_admins("Admin, new slots!")
                await self.send_message_to_admins(Path("data/response.html"))
            if state != State.PENDING:
                self.pending = False
                await self.update_status_messages(state)
            self.state = state

        await asyncio.sleep(config.PERIOD)
        asyncio.create_task(self.execute())
