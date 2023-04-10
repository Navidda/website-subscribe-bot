import asyncio
import json
import logging
from datetime import datetime
from enum import Enum, auto
from http import HTTPStatus
from typing import Coroutine, List

import pytz
import requests
import telegram as t
import telegram.ext as tt
from telegram import Message, Update, error
from telegram.ext import (
    Application,
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
)
from telegram.ext._utils.types import BD, BT, CCT, CD, JQ, UD

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

logger = logging.getLogger(__name__)


# token = "1988829719:AAHDD4JkFjaO6-UZYHZ_Jd1B-9ahD1TGoqk"
token = "5455024630:AAG89D8OmG758ZFTxIma_qtRAqRivKwvTNM"

cookies = {
    "cookie_accept": "1",
    "TVWebSession": "k08eg9ntk7pcki3hd293b0ucj0",
}

headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "Accept-Language": "en-US,en-GB;q=0.9,en;q=0.8,fa;q=0.7",
    "Cache-Control": "max-age=0",
    "Connection": "keep-alive",
    # Requests sorts cookies= alphabetically
    # 'Cookie': 'cookie_accept=1; TVWebSession=r99l43fm0tds17nr1tqtl4v7f1',
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

params = {
    "cnc-191": "1",
    "loc": "28",
}

PERIOD = 10


class PersistedList:
    def __init__(self, filename):
        self.filename = filename
        self.items = []

    def __repr__(self):
        return f"PersistableList(items={self.items})"

    def save(self):
        with open(self.filename, "w") as f:
            json.dump(self.items, f)

    def load(self):
        try:
            with open(self.filename, "r") as f:
                self.items = json.load(f)
        except FileNotFoundError:
            pass

    def append(self, item):
        if item not in self.items:
            self.items.append(item)
            self.save()

    def remove(self, item):
        try:
            self.items.remove(item)
            self.save()
        except ValueError:
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

    async def add_subscriber(self, chat_id: int):
        if len(self.chat_ids.items) < 300:
            self.chat_ids.append(chat_id)
        else:
            await self.application.bot.send_message("Overflow Error! Contact Admin!")
        # msg = await self.application.bot.send_message(chat_id, self.state.name)
        # self.status_msgs.append(msg)

    def perform_request_real(self):
        state = State.PENDING

        # timeout 5 seconds
        try:
            self.response = requests.get(
                "https://termine.staedteregion-aachen.de/auslaenderamt/suggest",
                params=params,
                cookies=cookies,
                headers=headers,
                timeout=PERIOD / 2.0,
            )
        except requests.exceptions.Timeout:
            logger.info("Request Timeout!")
            return State.PENDING
        except requests.exceptions.ConnectionError:
            logger.info("Connection Error!")
            self.state = State.PENDING
            return State.PENDING
        except requests.exceptions.RequestException as e:
            logger.info(f"Request Error: {e}")
            return State.PENDING
        except Exception as e:
            logger.info(f"Unknown Error: {e}")
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
        for time in range(times):
            if time:
                print("times:", time + 1)
            try:
                await self.application.bot.send_message(chat_id, text)
                return
            except error.Forbidden:
                self.chat_ids.remove(chat_id)
                logger.info(f"Removed chat_id {chat_id} from chat_ids.json")
                return
            except Exception as exc:
                pass
        logger.info(f"Error sending to user: {exc}")

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

        await asyncio.sleep(PERIOD)
        asyncio.create_task(self.execute())


REQUESTOR = Requestor()
subscribe_button = t.KeyboardButton("Subscribe")
donate_button = t.KeyboardButton("Donate")
unsubscribe_button = t.KeyboardButton("Unsubscribe")
welcome_message = """
Welcome to auslander bot!
I will check every 30 seconds and if I find a new appointment I will tell you!
"""
donate_text = """
Buy me a coffee! paypal.me/navidda
"""


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[subscribe_button, donate_button, unsubscribe_button]]
    reply_markup = t.ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(welcome_message, reply_markup=reply_markup)
    await REQUESTOR.add_subscriber(update.effective_chat.id)


async def get_last(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id, text=REQUESTOR.last_request.strftime("%c")
    )


async def new_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message.text == subscribe_button.text:
        await context.bot.send_message(
            chat_id=update.effective_chat.id, text="You were subscribed!"
        )
        await REQUESTOR.add_subscriber(update.effective_chat.id)
    elif update.message.text == donate_button.text:
        await context.bot.send_message(
            chat_id=update.effective_chat.id, text=donate_text
        )
    elif update.message.text == unsubscribe_button.text:
        REQUESTOR.chat_ids.remove(update.effective_chat.id)
        await context.bot.send_message(
            chat_id=update.effective_chat.id, text="You were unsubscribed!"
        )
    elif update.message.text == "Admin":
        await context.bot.send_message(
            chat_id=update.effective_chat.id, text="Hey admin!"
        )
        REQUESTOR.admin_ids.append(update.effective_chat.id)
        with open("response.html", "rb") as f:
            await context.bot.send_document(update.effective_chat.id, f)
    elif update.message.text.startswith("cookie"):
        session = update.message.text.split()[1]
        cookies["TVWebSession"] = session
        await context.bot.send_message(
            chat_id=update.effective_chat.id, text=f"Cookie set! {session}"
        )


if __name__ == "__main__":
    application = ApplicationBuilder().token(token).build()
    REQUESTOR.application = application
    start_handler = CommandHandler("start", start)
    last_handler = CommandHandler("last", get_last)
    msg_handler = MessageHandler(tt.filters.TEXT, new_message)
    application.add_handler(start_handler)
    application.add_handler(last_handler)
    application.add_handler(msg_handler)
    loop = asyncio.get_event_loop()
    loop.create_task(REQUESTOR.execute())
    application.run_polling()
