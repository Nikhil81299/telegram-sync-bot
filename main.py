import os
import json
import asyncio
import threading
from flask import Flask
from pyrogram import Client
import gspread
from google.oauth2.service_account import Credentials

# ==============================
# 🔐 LOAD ENV VARIABLES
# ==============================

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Load Google credentials from ENV
google_credentials_json = os.getenv("GOOGLE_CREDENTIALS")

if not google_credentials_json:
    raise Exception("GOOGLE_CREDENTIALS environment variable not found!")

google_credentials_dict = json.loads(google_credentials_json)

# ==============================
# 📊 GOOGLE SHEET SETUP
# ==============================

scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

creds = Credentials.from_service_account_info(
    google_credentials_dict,
    scopes=scope
)

gc = gspread.authorize(creds)

# Replace with your sheet name
SHEET_NAME = "Telegram Sync Data"
sheet = gc.open(SHEET_NAME).sheet1

# ==============================
# 🤖 PYROGRAM CLIENT
# ==============================

app = Client(
    "telegram-sync-bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# ==============================
# 🌐 FLASK SERVER (FOR RENDER)
# ==============================

flask_app = Flask(__name__)

@flask_app.route("/")
def home():
    return "Bot is running!"

def run_flask():
    flask_app.run(host="0.0.0.0", port=10000)

# ==============================
# 🚀 MAIN BOT START
# ==============================

async def main():
    await app.start()
    print("✅ Bot Started Successfully!")
    await asyncio.Event().wait()

if __name__ == "__main__":
    # Start Flask in separate thread
    threading.Thread(target=run_flask).start()

    # Run bot
    asyncio.run(main())