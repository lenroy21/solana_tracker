import os
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# Telegram bot credentials
TELEGRAM_BOT_TOKEN = '7798971915:AAE1Y2U9gIOlveBcHU8Na4bwoRzNyc885IY'
TELEGRAM_CHAT_ID = '8169255160'

def send_telegram_alert(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message
    }
    response = requests.post(url, json=payload)
    return response.json()

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    event_type = data.get('event_type')
    
    if event_type == 'TOKEN_CREATION':
        token_info = data.get('token_info', {})
        message = f"🚀 New Token Created!\n\n"
        message += f"Name: {token_info.get('name', 'N/A')}\n"
        message += f"Symbol: {token_info.get('symbol', 'N/A')}\n"
        message += f"Address: {token_info.get('address', 'N/A')}\n"
        message += f"Creator: {token_info.get('creator', 'N/A')}\n"
        message += f"Supply: {token_info.get('supply', 'N/A')}\n"
        send_telegram_alert(message)
    
    return jsonify({"status": "success"}), 200

@app.route('/')
def home():
    return "Solana Token Tracker is running!"

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))  # Render provides a PORT environment variable
    app.run(host="0.0.0.0", port=port)
