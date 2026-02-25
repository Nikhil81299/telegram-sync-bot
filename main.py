import asyncio
import json
from flask import Flask
from threading import Thread
from pyrogram import Client, filters
import gspread
from google.oauth2.service_account import Credentials

# ==============================
# 🔐 TELEGRAM CREDENTIALS
# ==============================

API_ID = 31253274  # 🔁 replace with your api id (number)
API_HASH = "a030168a85a5cdb750c0557b684491e3"
BOT_TOKEN = "8611044130:AAE_MJjr9ZPd115mLp9XPMoI09sLM9SEb9I"

# ==============================
# 🔐 GOOGLE SERVICE ACCOUNT JSON
# ==============================

google_credentials_info = {
  "type": "service_account",
  "project_id": "telegramsync-488519",
  "private_key_id": "d08772ae5ff697ce3b51193014d9e559425fa390",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQC9iRlnq2kZK+J0\n5c5Y1ltTw7sHz+RUI0uLV7OGBfcblPzKIhnLoCtkQECh1Djf6e3ttf+FAVs8+w/o\nD7aVO76zd2/iOvR7J7S9mCOkBV8Ulm3HWllTVvjAlYDjJoJLnU+o217M0X3b+pxw\nAacrGdUmMyJDmeVrTgL5AnIY89fquCfblyRueQRhUbkknW81GcWslghQaXXjZE5Q\n2KCJD4Zy4qwhlhRrb407Zn2+7KCGqzCcKrQsUGpJWxcODAcMX+x0SXXO2jN2zW3+\nRbH0opS/zdGpHpg0M1nylQVdlz0VNQDcsfEFYUeM4sEqTT80YTXcDAF4Q7+h3dbp\nErwtTcmRAgMBAAECggEAAMEvYvnheJOE0hoQIf5qoImNO1mH4bs1+jBzVd2rrlUZ\nZI/V7exrmWhRJlxUwE5pMqLTzXuh5kwfeDkydZIu7Nv/8ixglZ16MHrKuYkfrDBg\n3z/KCnUr7F/WrUQNDUni67VS0qMCW88PO1N3bOxfaDepgHZV3cWBnDC7PF1lxxSG\nVgePD+sxDC+8ipk1z4RBF3scm8VRTMu/puIA1AiPIT1RgO9lYo8u4x8Yxy5Oc7C9\n3B4qqAazsz8RNH0nOH0zQEXkWEwS7JRKd6PnLChd5Qnfc2GUQnG80GC7IAnvrCRU\n9BtEhvFXCnJVqJ3rdgCJph7cyyNS3Lam30gJnFoIeQKBgQDjd1F2/SYhVkOEc/8n\nV0lAbDdaVNlED8CFD1gHyo1xqjcBcFiFWjiM4WOv6VhmsG+KIVhyNFZ40fSff9D2\nyWW53ySYsiCt8lHa5qUmnZD8scx61BulZ0Yn8sNAiAv20g0Tzi1OngwUNbY7agBE\nuVbutzMoK78xpb/mlWrZ7v5JswKBgQDVT7T5bxzUN62bLgytcuCJb4Y6ZPCZcx4u\nBBjiWwmjkSil/vngWHk2VwSaagid6VaEBIp3ix2pcH/LUZMfp/GwJ/iyaZ+7CHUv\nOBkClN8uBqVr1wKEHDOlZLrXTvF17qWbyNbypZlet82Ug+LxqXrbflgl9F20A8nX\nJT2S2c21qwKBgQCnL2bABzaEYCwF6WALYVtkr2VLzntWTCGbaviv2U920L3XH+Tg\nNrzDx1GG1QJ1j46bvwCMCC3aZa7foIlNKh/LqtfyJ1Jfp3BEbSvLoxoSsPfy+31K\naAqniAW8o4HvqtmTygGA/Ccyn3vOVY3W9UaQ9DP0fZrseb//UakUf1WFgwKBgCic\nRSsb0VRByWZ6zOUUstTXi6mAYCIGvZ8rHoWxqVMfpqp7sZzZmzISPQkc2MkfjF4T\n8zyxGpOQnHPb8vOa6LON2JY277cO9ChqOLC6IQdFMqcmRw9Zwydg1wV4vRWjupm/\nEdUeW+Whfp0gwssZZg91rViEfnZwJjQ0ndVga/6DAoGBAINXxwisJKp8caT/7GNZ\nW7xUMsCTKxTHuxdI4KpsD+gXkIqGKLGuW+zASfPc6NrzHARtmPxtQ/UKtEV0Mlzt\nX5GLThvLEDbey81Fnh2Mrz6o46mZy+leR0ecYUJqKqEaUr43+khZjuC53E4vX4we\nNhKAg5nkgzwb4pkm02uR2/jw\n-----END PRIVATE KEY-----\n",
  "client_email": "telegram-sync@telegramsync-488519.iam.gserviceaccount.com",
  "client_id": "110021298754371137690",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/telegram-sync%40telegramsync-488519.iam.gserviceaccount.com",
  "universe_domain": "googleapis.com"
}


# ==============================
# 📊 GOOGLE SHEETS SETUP
# ==============================

scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

creds = Credentials.from_service_account_info(
    google_credentials_info,
    scopes=scope
)

gc = gspread.authorize(creds)

# 🔁 Replace with your Google Sheet name
sheet = gc.open("YourSheetName").sheet1

# ==============================
# 🤖 TELEGRAM BOT SETUP
# ==============================

app = Client(
    "my_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# ==============================
# 👋 START COMMAND
# ==============================

@app.on_message(filters.command("start"))
async def start(client, message):
    await message.reply_text("👋 Welcome to Channel Forward Bot!")

# ==============================
# 💬 SAVE USER TO SHEET
# ==============================

@app.on_message(filters.private & filters.text)
async def save_user(client, message):
    user_id = message.from_user.id
    username = message.from_user.username

    try:
        sheet.append_row([str(user_id), str(username)])
    except:
        pass

# ==============================
# 🌐 FLASK SERVER FOR RENDER
# ==============================

web_app = Flask(__name__)

@web_app.route("/")
def home():
    return "Bot is running!"

def run_flask():
    web_app.run(host="0.0.0.0", port=10000)

# ==============================
# 🚀 START EVERYTHING
# ==============================

if __name__ == "__main__":
    Thread(target=run_flask).start()
    app.run()