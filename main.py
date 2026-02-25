import os
import asyncio
import gspread
from flask import Flask
from threading import Thread
from telethon import TelegramClient
from telethon.errors.rpcerrorlist import FloodWaitError
from oauth2client.service_account import ServiceAccountCredentials

# =====================
# CONFIG
# =====================
# 👉 For LOCAL testing, put your real values directly:
API_ID = 31253274   # ← your real api id
API_HASH = "a030168a85a5cdb750c0557b684491e3"

# 👉 For Render later, change to:
# API_ID = int(os.getenv("API_ID"))
# API_HASH = os.getenv("API_HASH")

BATCH_SIZE = 50
WAIT_TIME = 8
CHANNEL_DELAY = 15

# =====================
# GOOGLE SHEETS SETUP
# =====================
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive",
]

creds = ServiceAccountCredentials.from_json_keyfile_name(
    "google_credentials.json", scope
)

sheet_client = gspread.authorize(creds)
sheet = sheet_client.open("TelegramSync").sheet1  # Must match your sheet name

# =====================
# KEEP ALIVE SERVER (for Render)
# =====================
app = Flask("")

@app.route("/")
def home():
    return "Bot Running!"

def run():
    app.run(host="0.0.0.0", port=10000)

def keep_alive():
    t = Thread(target=run)
    t.start()

# =====================
# TELEGRAM CLIENT
# =====================
client = TelegramClient("session", API_ID, API_HASH)

# =====================
# STATUS UPDATE
# =====================
def update_status(row, status):
    sheet.update_cell(row, 4, status)
    print(f"Row {row} → {status}")

# =====================
# PROCESS CHANNEL
# =====================
async def process_channel(row, source, target):
    progress_file = f"last_id_{source}.txt"

    # Load last transferred message ID
    if not os.path.exists(progress_file):
        last_id = 0
        update_status(row, "WAITING")
    else:
        with open(progress_file, "r") as f:
            last_id = int(f.read())

    update_status(row, "TRANSFERRING")

    while True:
        messages = await client.get_messages(
            source,
            min_id=last_id,
            limit=BATCH_SIZE
        )

        if not messages:
            update_status(row, "DONE")
            break

        for msg in reversed(messages):
            try:
                # Send media
                if msg.media:
                    await client.send_file(
                        target,
                        msg.media,
                        caption=msg.text if msg.text else None
                    )

                # Send text
                elif msg.text:
                    await client.send_message(target, msg.text)

                # Skip empty/service messages
                else:
                    continue

                last_id = msg.id

                with open(progress_file, "w") as f:
                    f.write(str(last_id))

            except FloodWaitError as e:
                print(f"Flood wait: sleeping {e.seconds} seconds")
                await asyncio.sleep(e.seconds)

        print(f"{source} → Batch Completed")
        await asyncio.sleep(WAIT_TIME)

    await asyncio.sleep(CHANNEL_DELAY)

# =====================
# MAIN LOOP
# =====================
async def main():
    await client.start()

    while True:
        records = sheet.get_all_records()

        for i, row_data in enumerate(records):
            row_number = i + 2  # Skip header row
            source = row_data["source_channel"]
            target = row_data["target_channel"]

            if source and target:
                await process_channel(row_number, source, target)

        print("Restarting full cycle...")
        await asyncio.sleep(30)

# =====================
# START
# =====================
keep_alive()

with client:
    client.loop.run_until_complete(main())