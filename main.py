import google.generativeai as genai
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
import os

BOT_TOKEN = os.getenv("8621985838:AAHXlCtA4JHoMKyp-MTM1loTI3sGv0WcXA4")
GEMINI_API_KEY = os.getenv("AIzaSyCeWnynL9L0TsUjxOKf3MF8hjqH6PdVtz8")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

async def ai_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text

    try:
        response = model.generate_content(user_text)
        await update.message.reply_text(response.text)
    except Exception as e:
        await update.message.reply_text("Error: " + str(e))

app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(MessageHandler(filters.TEXT, ai_reply))

print("Bot aktif...")
app.run_polling()
