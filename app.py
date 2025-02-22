import os
from flask import Flask, request, jsonify
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

app = Flask(__name__)

# Replace these with your Telegram bot token and chat ID
TELEGRAM_BOT_TOKEN = os.environ.get("7743475589:AAFDjOj9IJ-lwXwVimOr_Vo8fr_uA5p2k6g")
TELEGRAM_CHAT_ID = os.environ.get("8169255160")

# Initialize the Telegram bot application
application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

def send_telegram_alert(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
    response = requests.post(url, json=payload)
    return response.json()

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    event_type = data.get('event_type')
    
    if event_type == 'TOKEN_CREATION':
        token_info = data.get('token_info', {})
        message = (
            f"🚀 New Token Created!\n\n"
            f"Name: {token_info.get('name', 'N/A')}\n"
            f"Symbol: {token_info.get('symbol', 'N/A')}\n"
            f"Address: {token_info.get('address', 'N/A')}\n"
            f"Creator: {token_info.get('creator', 'N/A')}\n"
            f"Supply: {token_info.get('supply', 'N/A')}\n"
        )
        send_telegram_alert(message)
    
    return jsonify({"status": "success"}), 200

@app.route('/')
def home():
    return "Solana Token Tracker is running!"

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
