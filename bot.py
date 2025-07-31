import os
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
from pymongo import MongoClient
from eth_wallet import generate_eth_address

# Load environment variables
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
MONGO_URI = os.getenv("MONGO_URI")
REQUIRED_AMOUNT = 0.01
PREMIUM_CHANNEL_ID = os.getenv("PREMIUM_CHANNEL_ID")  # for info only
PREMIUM_GROUP_LINK = os.getenv("PREMIUM_GROUP_LINK")  # optional (if not adding directly)

# Connect to MongoDB
client = MongoClient(MONGO_URI)
db = client["argento"]
users = db["users"]

# /start command handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tg_id = update.effective_user.id
    name = update.effective_user.first_name
    user = users.find_one({"telegram_id": tg_id})

    if user:
        status = user.get("status")
        if status == "approved":
            await update.message.reply_text(
                "✅ החשבון שלך כבר מאושר!\n"
                "אם טרם נכנסת לקבוצת הפרימיום – הנה הקישור:\n"
                f"{PREMIUM_GROUP_LINK or '🔐 המתן שהבוט יצרף אותך אוטומטית.'}"
            )
        elif status == "waiting_payment":
            await update.message.reply_text(
                "💡 כבר אישרת את התנאים.\n"
                "💰 שלח **0.01 ETH** לכתובת האישית שלך:\n\n"
                f"`{user['eth_address']}`\n\n"
                "_לאחר התשלום תתווסף אוטומטית לערוץ הפרימיום._",
                parse_mode="Markdown"
            )
        else:
            await send_terms(update)
    else:
        # First time user
        users.insert_one({
            "telegram_id": tg_id,
            "name": name,
            "status": "new"
        })
        await update.message.reply_text(
            f"👋 שלום {name}, ברוך הבא לבוט של Argento X!\n"
            "אנא אשר את תנאי השימוש כדי להמשיך."
        )
        await send_terms(update)

# Send terms of use message
async def send_terms(update: Update):
    terms_text = (
        "📜 *תנאי שימוש*\n\n"
        "השירות ניתן לצרכים חינוכיים בלבד ואינו מהווה ייעוץ פיננסי.\n"
        "באישור תנאי השימוש תוכל לעבור לשלב התשלום."
    )
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ אני מאשר את התנאים", callback_data="accept_terms")]
    ])
    await update.message.reply_text(terms_text, parse_mode="Markdown", reply_markup=keyboard)

# Handle inline button (terms confirmation)
async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    tg_id = query.from_user.id
    user = users.find_one({"telegram_id": tg_id})
    await query.answer()

    if query.data == "accept_terms":
        if not user.get("eth_address"):
            user_index = users.count_documents({})
            wallet = generate_eth_address(user_index)
            users.update_one(
                {"telegram_id": tg_id},
                {"$set": {
                    "eth_address": wallet["address"],
                    "status": "waiting_payment"
                }}
            )
        else:
            wallet = {"address": user["eth_address"]}

        await query.edit_message_text("✅ תנאים אושרו. ממשיכים לתשלום...")
        await context.bot.send_message(
            chat_id=tg_id,
            text=(
                "💰 לתשלום, שלח בדיוק **0.01 ETH** לכתובת האישית שלך:\n\n"
                f"`{wallet['address']}`\n\n"
                "_לאחר התשלום, החשבון שלך יאושר אוטומטית._"
            ),
            parse_mode="Markdown"
        )

# Main runner
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_callback))
    app.run_polling()

if __name__ == "__main__":
    main()
