import os
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler

# משתנה זמני לזיהוי יוזרים (בשלב הבא יעבור ל-MongoDB)
users = {}

# /start – הודעת פתיחה
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    users[user.id] = {"name": user.first_name, "status": "new"}

    await update.message.reply_text(f"👋 שלום {user.first_name}, ברוך הבא לבוט של Argento X!")
    await send_terms(update, context)

# שלב תנאי שימוש
async def send_terms(update: Update, context: ContextTypes.DEFAULT_TYPE):
    terms = (
        "📜 *תנאי שימוש*\n\n"
        "השירות נועד למטרות חינוכיות בלבד ואינו מהווה ייעוץ פיננסי.\n"
        "בהמשך השימוש בבוט, אתה מאשר את התנאים.\n\n"
        "המשך לשלב הבא:"
    )
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ אני מאשר את התנאים", callback_data="accept_terms")]
    ])
    await update.message.reply_text(terms, parse_mode="Markdown", reply_markup=keyboard)

# טיפול בלחיצה על הכפתור
async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id

    if query.data == "accept_terms":
        users[user_id]["status"] = "terms_accepted"
        await query.answer()
        await query.edit_message_text("✅ תנאים אושרו. ממשיכים לשלב התשלום...")
        await query.message.reply_text("💳 קישור לתשלום יופיע בקרוב...")

# בניית הבוט
def build_app():
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    app = ApplicationBuilder().token(token).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_callback))
    return app

if __name__ == "__main__":
    app = build_app()
    app.run_polling()
