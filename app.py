import os
import requests
import time
from flask import Flask
from apscheduler.schedulers.background import BackgroundScheduler
import pytz  # Import pytz for timezone support

app = Flask(__name__)

# Replace these with your Telegram bot token and chat ID
TELEGRAM_BOT_TOKEN = "7798971915:AAE1Y2U9gIOlveBcHU8Na4bwoRzNyc885IY"
TELEGRAM_CHAT_ID = "8169255160"

# ✅ Correct Dexscreener API URL
DEXSCREENER_API_URL = "https://api.dexscreener.com/latest/dex/search"

# Set to store seen token addresses
seen_tokens = set()

def send_telegram_alert(message):
    """Sends alert message to Telegram bot."""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
    response = requests.post(url, json=payload)
    return response.json()

def fetch_new_tokens():
    """Fetches new tokens from Dexscreener API and processes them."""
    try:
        params = {"q": "solana"}  # ✅ Correct API parameter
        response = requests.get(DEXSCREENER_API_URL, params=params)
        
        # Debugging: Print full response if the request fails
        if response.status_code != 200:
            print(f"Failed to fetch data: {response.status_code}")
            print(f"Response Text: {response.text}")
            return
        
        data = response.json()
        process_tokens(data)
    
    except Exception as e:
        print(f"Error fetching data: {e}")

def process_tokens(data):
    """Processes new token pairs and sends alerts if they meet criteria."""
    current_time = time.time()  # Current timestamp in seconds
    
    for pair in data.get("pairs", []):
        token = pair.get("baseToken", {})
        token_address = token.get("address")
        liquidity = pair.get("liquidity", {}).get("usd", 0)
        volume = pair.get("volume", {}).get("h24", 0)
        price = pair.get("priceUsd", 0)
        created_at = pair.get("createdAt", 0) / 1000  # Convert milliseconds to seconds
        
        # ✅ Only allow tokens created in the last 24 hours (86400 seconds)
        if current_time - created_at > 86400:
            continue  # Skip old tokens
        
        # ✅ Skip if token address is missing
        if not token_address:
            continue
        
        # ✅ Ensure token is new (not seen before)
        if token_address in seen_tokens:
            continue
        
        seen_tokens.add(token_address)  # Mark token as seen

        # ✅ Filter tokens based on liquidity and volume
        if liquidity > 1000 and volume > 10000:  # Example thresholds
            message = (
                f"🚀 New Token Detected!\n\n"
                f"Name: {token.get('name', 'N/A')}\n"
                f"Symbol: {token.get('symbol', 'N/A')}\n"
                f"Address: {token_address}\n"
                f"Price: ${price}\n"
                f"Liquidity: ${liquidity}\n"
                f"Volume (24h): ${volume}\n"
            )
            send_telegram_alert(message)

# Set the timezone for the scheduler
timezone = pytz.timezone("UTC")  # Use UTC or your preferred timezone

# Schedule the fetch_new_tokens function to run every 60 seconds
scheduler = BackgroundScheduler(timezone=timezone)
scheduler.add_job(fetch_new_tokens, 'interval', seconds=60)  # Fixed timezone issue
scheduler.start()

@app.route('/')
def home():
    return "Solana Token Tracker is running!"

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
