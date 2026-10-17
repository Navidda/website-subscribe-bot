# Website Subscribe Bot
A telegram bot for monitoring updates to a particular website, and send updates to subscribers based in a FIFO queue.

This is implemented to monitor Aachen immigration office. 

## Installation

1. Create and setup python environment

       python3 -m venv .venv
       source .venv/bin/activate # Windows: source .venv/Scripts/activate
       pip install -r requirements.txt

2. Get your bot's api token from botfather and save it to `.env` file.


       echo "BOT_TOKEN=Your Token Here" > .env

   Optional settings (see `config.py` for defaults):

       echo "MAX_WAIT_DAYS=30" >> .env  # alert when a slot within this many days appears
       echo "PERIOD=60" >> .env         # seconds between checks
       echo "CONCERN=341" >> .env       # TEVIS concern id (341 = Beratungs- und Antragsservice)
       echo "LOCATION=49" >> .env       # TEVIS location id (49 = Aachen Arkaden)

   The bot walks the booking flow on https://termine.staedteregion-aachen.de/auslaenderamt
   itself and reads the free slots from step 4 ("Terminvorschläge - Auswahl der Zeit").
   Subscribers are notified when a slot within `MAX_WAIT_DAYS` appears or an even earlier one shows up.


3. Run the bot

       ./run.sh

## DM from your own account (no bot)

`notify_user.py` uses the Telegram user API (Telethon) to message a person from your own account
when a slot within `MAX_WAIT_DAYS` appears, and again whenever that earliest slot changes
(an earlier one shows up, or the sent one gets booked).

1. Create an app at https://my.telegram.org → API development tools and add to `.env`:

       echo "TG_API_ID=..." >> .env
       echo "TG_API_HASH=..." >> .env
       echo "TG_RECIPIENT=@username" >> .env
       echo "TG_RECIPIENT_NAME=Name" >> .env  # used in the greeting

2. Log in once (phone number + login code), then run it, e.g. in tmux on a server:

       set -a; source .env; set +a
       python notify_user.py --login
       python notify_user.py
