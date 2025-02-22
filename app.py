import websocket
import json
import requests
import telegram
from telegram.ext import Updater, CommandHandler
from flask import Flask, request, jsonify
import threading

# Constants
BIRDEYE_API_KEY = "YOUR_API_KEY"
TELEGRAM_BOT_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"
TELEGRAM_CHAT_ID = "YOUR_CHAT_ID"
BIRDEYE_WS_URL = f"wss://public-api.birdeye.so/socket/solana?x-api-key={BIRDEYE_API_KEY}"

# Initialize Flask app
app = Flask(__name__)
bot = telegram.Bot(token=TELEGRAM_BOT_TOKEN)

def start(update, context):
    """Start command for Telegram bot."""
    update.message.reply_text("Solana Token Tracker is running!")

# Telegram Bot Setup
updater = Updater(TELEGRAM_BOT_TOKEN, use_context=True)
dp = updater.dispatcher
dp.add_handler(CommandHandler("start", start))

def on_message(ws, message):
    """Handles incoming WebSocket messages."""
    data = json.loads(message)
    print("Received WebSocket Data:", data)

    # Process and send to Telegram
    try:
        msg = f"New Token Update:\n{data}"
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=msg)
    except Exception as e:
        print(f"Error sending to Telegram: {e}")

def on_error(ws, error):
    """Handles WebSocket errors."""
    print(f"WebSocket Error: {error}")

def on_close(ws, close_status_code, close_msg):
    """Handles WebSocket closure."""
    print("WebSocket Closed")

def on_open(ws):
    """Handles WebSocket connection opening."""
    print("WebSocket Connection Opened")

def start_websocket():
    """Starts WebSocket connection with authentication."""
    headers = {
        "Authorization": f"Bearer {BIRDEYE_API_KEY}",
        "User-Agent": "Mozilla/5.0"
    }

    ws = websocket.WebSocketApp(
        BIRDEYE_WS_URL,
        header=headers,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close,
        on_open=on_open
    )
    ws.run_forever()

@app.route('/webhook', methods=['POST'])
def webhook():
    """Receives data from external sources and processes it."""
    data = request.json
    print("Received Webhook Data:", data)
    return jsonify({"status": "success"}), 200

if __name__ == "__main__":
    # Start WebSocket in a separate thread
    websocket_thread = threading.Thread(target=start_websocket)
    websocket_thread.start()

    # Start Telegram bot
    updater.start_polling()

    # Start Flask server
    app.run(host="0.0.0.0", port=5000, debug=True)
