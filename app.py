from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# Telegram bot credentials (Ensure these are kept secure)
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
    # Get the data sent by Helius
    data = request.json
    print("Received data:", data)  # For debugging

    # Extract relevant information
    event_type = data.get('event_type')
    token_info = data.get('token_info', {})

    # Check if the event is a token creation
    if event_type == 'TOKEN_CREATION':
        message = f"🚀 New Token Created!\n\n"
        message += f"Name: {token_info.get('name')}\n"
        message += f"Symbol: {token_info.get('symbol')}\n"
        message += f"Address: {token_info.get('address')}\n"
        send_telegram_alert(message)
    
    return jsonify({"status": "success"}), 200

@app.route('/')
def home():
    return "Solana Token Tracker is running!"

if __name__ == '__main__':
    app.run(debug=True)
