import os
import json
import requests
import websocket
from flask import Flask, request, jsonify
import threading

app = Flask(__name__)

# Telegram bot credentials
TELEGRAM_BOT_TOKEN = "7798971915:AAE1Y2U9gIOlveBcHU8Na4bwoRzNyc885IY"
TELEGRAM_CHAT_ID = "8169255160"

def send_telegram_alert(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
    requests.post(url, json=payload)

@app.route('/webhook', methods=['POST'])
def webhook():
    """Receives token creation events and sends alerts to Telegram."""
    data = request.json
    event_type = data.get("event_type")

    if event_type == "TOKEN_CREATION":
        token_info = data.get("token_info", {})
        message = f"🚀 New Token Created!\n"
        message += f"🔹 Name: {token_info.get('name', 'N/A')}\n"
        message += f"🔹 Symbol: {token_info.get('symbol', 'N/A')}\n"
        message += f"🔹 Address: {token_info.get('address', 'N/A')}\n"
        message += f"🔹 Creator: {token_info.get('creator', 'N/A')}\n"
        message += f"🔹 Supply: {token_info.get('supply', 'N/A')}\n"

        send_telegram_alert(message)

    return jsonify({"status": "success"}), 200

@app.route('/')
def home():
    return "Solana Token Tracker is running!"

# WebSocket tracking for Birdeye
def on_message(ws, message):
    """Processes WebSocket messages and sends them to Flask webhook."""
    try:
        data = json.loads(message)
        requests.post("http://127.0.0.1:5000/webhook", json=data)
    except Exception as e:
        print(f"Error processing message: {e}")

def on_error(ws, error):
    print(f"WebSocket Error: {error}")

def on_close(ws, close_status_code, close_msg):
    print("WebSocket Closed")

def on_open(ws):
    print("WebSocket Connection Established")

def start_websocket():
    
    """Starts WebSocket connection with Birdeye API Key."""
    ws_url = "wss://public-api.birdeye.so/socket/solana?x-api-key=ab4bafdbf9ab4f499b32f25c8a29ddb7"  # Replace with actual Birdeye WebSocket URL

    headers = {
        "Authorization": "Bearer ab4bafdbf9ab4f499b32f25c8a29ddb7"  # Add your API key here
    }

    ws = websocket.WebSocketApp(
        ws_url,
        header=headers,  # Include API key in headers
        on_message=on_message,
        on_error=on_error,
        on_close=on_close
    )
    ws.on_open = on_open
    ws.run_forever()


if __name__ == "__main__":
    # Start Flask in one thread
    threading.Thread(target=lambda: app.run(host="0.0.0.0", port=5000)).start()
    
    # Start WebSocket in another thread
    start_websocket()
