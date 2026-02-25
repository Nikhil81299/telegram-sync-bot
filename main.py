import os
import json
import asyncio
from aiohttp import web
from pyrogram import Client, filters
from pyrogram.errors import FloodWait
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# =========================
# 🔐 ENV VARIABLES
# =========================

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Google credentials from environment variable
google_credentials_json = os.getenv("GOOGLE_CREDENTIALS")
google_credentials = json.loads(google_credentials_json)

# =========================
# 📊 GOOGLE SHEETS SETUP
# =========================

scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

creds = ServiceAccountCredentials.from_json_keyfile_dict(
    google_credentials, scope
)

client_sheet = gspread.authorize(creds)

# Replace with your sheet name
SHEET_NAME = "TelegramSyncData"
sheet = client_sheet.open(SHEET_NAME).sheet1

# =========================
# 🤖 PYROGRAM CLIENT
# =========================

app = Client(
    "telegram_sync_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# =========================
# 🚀 MESSAGE HANDLER
# =========================

@app.on_message(filters.channel)
async def forward_handler(client, message):
    try:
        # Example: Log message ID to Google Sheet
        sheet.append_row([str(message.chat.id), message.id])
        print(f"Saved message {message.id}")

    except FloodWait as e:
        await asyncio.sleep(e.value)

    except Exception as e:
        print("Error:", e)

# =========================
# 🌐 KEEP RENDER ALIVE
# =========================

async def handle(request):
    return web.Response(text="Bot is running!")

async def start_webserver():
    app_web = web.Application()
    app_web.router.add_get("/", handle)

    port = int(os.environ.get("PORT", 10000))
    runner = web.AppRunner(app_web)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()

# =========================
# ▶️ MAIN START
# =========================

async def main():
    await app.start()
    print("Bot Started Successfully!")

    await start_webserver()

    while True:
        await asyncio.sleep(3600)

if __name__ == "__main__":
    asyncio.run(main())
