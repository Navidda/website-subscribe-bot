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
       echo "ADMIN_PASSWORD=YourAdminPassword" >> .env # This is used to authenticate admin commands
       echo "NO_APPOINTMENT_TEXT=No appointment available" >> .env
       echo "APPOINTMENT_TEXT=Appointment available" >> .env


3. Run the bot

       ./run.sh