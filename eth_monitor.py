import os
import time
import requests
from pymongo import MongoClient
from telegram import Bot
from web3 import Web3

# Load environment variables
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
ETHERSCAN_API_KEY = os.getenv("ETHERSCAN_API_KEY")
MONGO_URI = os.getenv("MONGO_URI")
CHANNEL_ID = int(os.getenv("PREMIUM_CHANNEL_ID"))  # e.g. -1001234567890
REQUIRED_AMOUNT = 0.01  # ETH amount required for access

# Initialize services
client = MongoClient(MONGO_URI)
db = client["argento"]
users = db["users"]
bot = Bot(token=BOT_TOKEN)

w3 = Web3(Web3.HTTPProvider(os.getenv("INFURA_URL")))

def eth_paid_to_address(address: str) -> bool:
    """Check Etherscan if a payment was made to the address."""
    url = (
        f"https://api.etherscan.io/api"
        f"?module=account&action=txlist&address={address}"
        f"&sort=desc&apikey={ETHERSCAN_API_KEY}"
    )
    try:
        res = requests.get(url).json()
        if res["status"] != "1":
            return False

        for tx in res["result"]:
            if tx["to"].lower() == address.lower():
                eth_value = float(w3.fromWei(int(tx["value"]), 'ether'))
                if eth_value >= REQUIRED_AMOUNT:
                    return True
    except Exception as e:
        print(f"ETH Check error: {e}")
    return False

def check_and_approve_users():
    pending_users = users.find({"status": "waiting_payment", "eth_address": {"$exists": True}})
    for user in pending_users:
        tg_id = user["telegram_id"]
        address = user["eth_address"]

        print(f"🔍 Checking {tg_id} | {address}")
        if eth_paid_to_address(address):
            print(f"✅ Payment confirmed for {tg_id}")
            users.update_one({"telegram_id": tg_id}, {"$set": {"status": "approved"}})

            try:
                bot.send_message(chat_id=tg_id, text=(
                    "✅ התשלום התקבל בהצלחה!\n"
                    "ברוך הבא לערוץ הפרימיום של Argento X 🎯"
                ))
                bot.add_chat_members(chat_id=CHANNEL_ID, user_ids=[tg_id])
            except Exception as e:
                print(f"❌ Error adding {tg_id} to channel: {e}")
        else:
            print(f"❌ No payment for {tg_id} yet.")

# Main loop
if __name__ == "__main__":
    while True:
        print("⏱️ Running ETH monitor cycle...")
        check_and_approve_users()
        time.sleep(60)
