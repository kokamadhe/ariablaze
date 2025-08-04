import os
import sqlite3
import json
import requests
from flask import Flask, request
from telegram import Bot, Update
from telegram.ext import Dispatcher, CommandHandler, MessageHandler, Filters
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
MODEL_LAB_API_KEY = os.getenv("MODEL_LAB_API_KEY")
NOWPAYMENTS_API_KEY = os.getenv("NOWPAYMENTS_API_KEY")

app = Flask(__name__)
bot = Bot(token=TOKEN)

# SQLite setup
conn = sqlite3.connect("users.db", check_same_thread=False)
c = conn.cursor()
c.execute("CREATE TABLE IF NOT EXISTS premium_users (user_id INTEGER PRIMARY KEY)")
conn.commit()

# Flask route
@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    dp.process_update(update)
    return "OK"

# Check if user is premium
def is_premium(user_id):
    c.execute("SELECT * FROM premium_users WHERE user_id=?", (user_id,))
    return c.fetchone() is not None

# /pay command
def pay(update, context):
    user_id = update.effective_user.id
    payload = {
        "price_amount": 15,
        "price_currency": "USD",
        "pay_currency": "USDTTRC20",
        "ipn_callback_url": "https://nowpayments.io",
        "order_id": str(user_id),
        "order_description": "Qasje Premium në SpicyBot",
        "success_url": "https://t.me/your_bot_username",
        "cancel_url": "https://t.me/your_bot_username"
    }
    headers = {
        "x-api-key": NOWPAYMENTS_API_KEY,
        "Content-Type": "application/json"
    }
    res = requests.post("https://api.nowpayments.io/v1/invoice", headers=headers, json=payload)
    link = res.json().get("invoice_url", "Gabim gjatë krijimit të pagesës.")
    update.message.reply_text(f"💸 Paguaj këtu për të zhbllokuar Premium:\n{link}")

# /image command
def image(update, context):
    user_id = update.effective_user.id
    if not is_premium(user_id):
        update.message.reply_text("🔒 Kjo veçori është vetëm për përdoruesit premium.")
        return

    prompt = " ".join(context.args)
    if not prompt:
        update.message.reply_text("❗ Ju lutem jepni një përshkrim. Shembull: /image vajzë me flokë të kuqe")
        return

    response = requests.post(
        "https://api.modellab.dev/api/v1/generate",
        headers={"Authorization": f"Bearer {MODEL_LAB_API_KEY}"},
        json={"prompt": prompt}
    )

    data = response.json()
    image_url = data.get("output", [""])[0]
    if image_url:
        bot.send_photo(chat_id=update.effective_chat.id, photo=image_url)
    else:
        update.message.reply_text("⚠️ Dështoi gjenerimi i imazhit.")

# Chat handler
def handle_message(update, context):
    user_id = update.effective_user.id
    text = update.message.text

    if not is_premium(user_id):
        update.message.reply_text("🔒 Vetëm për përdorues Premium. Përdor /pay për të zhbllokuar.")
        return

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "nousresearch/nous-hermes-2-mixtral-8x7b-dpo",
        "messages": [{"role": "user", "content": text}]
    }
    res = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload)
    reply = res.json()["choices"][0]["message"]["content"]
    update.message.reply_text(reply)

# Komanda për të shtuar një përdorues si premium (vetëm për zhvilluesit)
def add_premium(update, context):
    user_id = update.effective_user.id
    c.execute("INSERT OR IGNORE INTO premium_users (user_id) VALUES (?)", (user_id,))
    conn.commit()
    update.message.reply_text("✅ Tani ke akses Premium!")

# Dispatcher setup
dp = Dispatcher(bot, None, workers=0, use_context=True)
dp.add_handler(CommandHandler("pay", pay))
dp.add_handler(CommandHandler("image", image))
dp.add_handler(CommandHandler("addpremium", add_premium))  # opsional
dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

# Run server
if __name__ == "__main__":
    app.run()
