import asyncio
import logging
from datetime import datetime
from enum import Enum, auto
from http import HTTPStatus
from typing import Coroutine, List

import pytz
import requests
from telegram import Message, error
from telegram.ext import Application
from telegram.ext._utils.types import BD, BT, CCT, CD, JQ, UD

import config
from utils import PersistedList


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
        self.response = requests.Response
        self.state: State = State.NO_APPOINTMENT
        self.last_request: datetime = None
        self.send_message_callback: Coroutine = None
        self.application: Application[BT, CCT, UD, CD, BD, JQ] = None
        self.chat_ids = PersistedList("chat_ids.json")
        self.chat_ids.load()
        self.admin_ids = PersistedList("admin_ids.json")
        self.admin_ids.load()
        self.status_msgs: List[Message] = []

        self.logger = logging.getLogger(__name__)

    async def add_subscriber(self, chat_id: int):
        if len(self.chat_ids.items) < 300:
            self.chat_ids.append(chat_id)
            return True
        else:
            await self.send_message_to_admins("Overflow error")
        # msg = await self.application.bot.send_message(chat_id, self.state.name)
        # self.status_msgs.append(msg)

    def perform_request_real(self):
        state = State.PENDING

        # timeout 5 seconds
        try:
            self.response = requests.get(
                "https://termine.staedteregion-aachen.de/auslaenderamt/suggest",
                params=config.params,
                cookies=config.cookies,
                headers=config.headers,
                timeout=config.PERIOD / 2.0,
            )
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
            self.logger.info(f"Unknown Error: {e}")
            return State.PENDING

        with open("response.html", "w") as f:
            f.write(self.response.text)

        no_appointment_text = "Kein freier Termin verfügbar"
        error_text = "Es ist ein Fehler aufgetreten"

        if no_appointment_text in self.response.text:
            state = State.NO_APPOINTMENT
        elif (
            self.response.status_code == HTTPStatus.OK
            and error_text not in self.response.text
        ):
            state = State.FREE_APPOINTMENT
        else:
            state = State.PENDING

        return state

    def perform_request(self):
        return (
            State.FREE_APPOINTMENT
            if self.state == State.NO_APPOINTMENT
            else State.NO_APPOINTMENT
        )

    async def send_message(self, chat_id, text):
        times = 3
        exc = None
        for time in range(times):
            if time:
                print("times:", time + 1)
            try:
                await self.application.bot.send_message(chat_id, text)
                return
            except error.Forbidden:
                self.chat_ids.remove(chat_id)
                self.logger.info(f"Removed chat_id {chat_id} from chat_ids.json")
                return
            except Exception as e:
                exc = e
        self.logger.info(f"Error sending to user: {exc}")

    async def send_message_to_admins(self, text):
        for id in self.admin_ids.items:
            asyncio.create_task(self.send_message(id, text))

    async def update_status_messages(self, state):
        # for msg in self.status_msgs:
        #     asyncio.create_task(msg.edit_text(self.state.name))
        for id in self.chat_ids.items:
            asyncio.create_task(self.send_message(id, STATE_TO_MSG[state]))

    async def execute(self):
        state = self.perform_request_real()

        tz = pytz.timezone("Europe/Berlin")
        self.last_request = datetime.now(tz)

        if state == State.PENDING:
            await self.send_message_to_admins(
                f"Request Error! Last Request: {self.last_request}"
            )
        elif state != self.state:
            await self.update_status_messages(state)
            self.state = state

        await asyncio.sleep(config.PERIOD)
        asyncio.create_task(self.execute())
