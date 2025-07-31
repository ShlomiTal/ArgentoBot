import os
import time
from pymongo import MongoClient
from web3 import Web3
from telegram import Bot
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
INFURA_URL = os.getenv("INFURA_URL")
REQUIRED_AMOUNT = float(os.getenv("REQUIRED_AMOUNT", "0.01"))
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
PREMIUM_GROUP_LINK = os.getenv("PREMIUM_GROUP_LINK")

# Setup MongoDB
client = MongoClient(MONGO_URI)
db = client["argento"]
users = db["users"]

# Setup Web3
web3 = Web3(Web3.HTTPProvider(INFURA_URL))
bot = Bot(token=BOT_TOKEN)

# Helper: get ETH balance
def get_eth_balance(address):
    try:
        wei_balance = web3.eth.get_balance(Web3.to_checksum_address(address))
        return web3.from_wei(wei_balance, 'ether')
    except Exception as e:
        print(f"⚠️ Error getting balance for {address}: {e}")
        return 0

# Main loop
def run_monitor():
    print("⏱️ Running ETH monitor cycle...\n")
    for user in users.find({"status": "waiting_payment"}):
        tg_id = user["telegram_id"]
        address = user.get("eth_address")

        if not address:
            print(f"❌ No ETH address for {tg_id}")
            continue

        print(f"🔍 Checking {tg_id} | {address}")
        balance = get_eth_balance(address)

        if balance >= REQUIRED_AMOUNT:
            users.update_one(
                {"telegram_id": tg_id},
                {"$set": {"status": "approved", "paid": True, "approved_at": time.time()}}
            )
            try:
                bot.send_message(
                    chat_id=tg_id,
                    text=(
                        "✅ התשלום התקבל בהצלחה!\n"
                        "🎉 ברוך הבא לשירות הפרימיום של Argento X.\n"
                        f"📥 הצטרף עכשיו: {PREMIUM_GROUP_LINK}"
                    )
                )
                print(f"✅ Payment received from {tg_id}")
            except Exception as e:
                print(f"❌ Failed to notify {tg_id}: {e}")
        else:
            print(f"❌ No payment for {tg_id} yet.\n")

# Loop forever
if __name__ == "__main__":
    while True:
        run_monitor()
        time.sleep(60)  # Check every 60 seconds
