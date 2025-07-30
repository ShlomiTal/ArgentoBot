import os
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler

# בסיס נתונים זמני לזיהוי משתמשים (לשלב הבא אפשר להעביר ל-MongoDB)
users = {}

# /start – הודעת פתיחה
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    users[user.id] = {"name": user.first_name, "status": "new"}

    await update.message.reply_text(f"👋 שלום {user.first_name}, ברוך הבא לבוט של Argento X!")
    await send_terms(update, context)

# תנאי שימוש מלאים בעברית
async def send_terms(update: Update, context: ContextTypes.DEFAULT_TYPE):
    terms = (
        "📜 *תנאי שימוש – Argento X*\n\n"
        "בשימושך בשירותי Argento X (כולל בוט הטלגרם, הממשק הדיגיטלי, וכל פלטפורמה אחרת), "
        "אתה מאשר כי קראת, הבנת, והסכמת לתנאי השימוש המפורטים במסמך זה.\n\n"
        "🔒 *אין ייעוץ השקעות*\n"
        "כל המידע, הניתוחים, ההתרעות והתכנים המוצגים במערכת הם *למטרות מידע כללי ולמידה בלבד* "
        "ואינם מהווים בשום אופן ייעוץ פיננסי, השקעה או מסחר.\n"
        "*שימושך במידע זה נעשה על אחריותך בלבד.*\n\n"
        "⚠️ Argento X אינה רואה עצמה אחראית להחלטות מסחר, הפסדים או רווחים שייגרמו "
        "כתוצאה מהסתמכות על המידע המוצג.\n\n"
        "על ידי אישור תנאים אלה, אתה מצהיר כי אתה מעל גיל 18 ומבין את הסיכון הכרוך במסחר.\n\n"
        "המשך לשלב הבא:"
    )

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ אני מאשר את התנאים", callback_data="accept_terms")]
    ])
    await update.message.reply_text(terms, parse_mode="Markdown", reply_markup=keyboard)

# טיפול בלחיצה על כפתור אישור תנאים
async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id

    if query.data == "accept_terms":
        users[user_id]["status"] = "terms_accepted"
        await query.answer()
        await query.edit_message_text("✅ תנאים אושרו. ממשיכים לשלב התשלום...")
        await query.message.reply_text("💳 קישור לתשלום יופיע בקרוב...")

# בניית אפליקציית הבוט
def build_app():
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    app = ApplicationBuilder().token(token).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_callback))
    return app

# הפעלת הבוט
if __name__ == "__main__":
    app = build_app()
    app.run_polling()
