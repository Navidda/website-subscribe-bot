import asyncio
import logging


import telegram as t
import telegram.ext as tt
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
)

import config
from requestor import Requestor

logger = logging.getLogger(__name__)


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


async def new_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message.text == subscribe_button.text:
        success = await REQUESTOR.add_subscriber(update.effective_chat.id)
        if success:
            await context.bot.send_message(
                chat_id=update.effective_chat.id, text="You were subscribed!"
            )
    elif update.message.text == donate_button.text:
        await context.bot.send_message(
            chat_id=update.effective_chat.id, text=donate_text
        )
    elif update.message.text == unsubscribe_button.text:
        REQUESTOR.queue_manager.quit_queue(update.effective_chat.id)
        await context.bot.send_message(
            chat_id=update.effective_chat.id, text="You were unsubscribed!"
        )
    elif update.message.text == "Admin":
        await context.bot.send_message(
            chat_id=update.effective_chat.id, text="Hey admin!"
        )
        REQUESTOR.admin_ids.append(update.effective_chat.id)
        with open("data/response.html", "rb") as f:
            await context.bot.send_document(update.effective_chat.id, f)
        await context.bot.send_message(
            chat_id=update.effective_chat.id, text=REQUESTOR.last_request.strftime("%c")
        )
    elif update.message.text.lower().startswith("cookie"):
        session = update.message.text.split()[1]
        config.COOKIES.data["TVWebSession"] = session
        config.COOKIES.save()
        await context.bot.send_message(
            chat_id=update.effective_chat.id, text=f"Cookie set! {session}"
        )


async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info(f"Update {update} caused error {context}")


if __name__ == "__main__":
    application = ApplicationBuilder().token(config.TOKEN).build()
    # application.add_error_handler(error_handler)
    REQUESTOR.application = application
    start_handler = CommandHandler("start", start)
    msg_handler = MessageHandler(tt.filters.TEXT, new_message)
    application.add_handler(start_handler)
    application.add_handler(msg_handler)
    loop = asyncio.get_event_loop()
    loop.create_task(REQUESTOR.queue_manager.process_queue())
    loop.create_task(REQUESTOR.execute())
    application.run_polling()
