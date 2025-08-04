import os
import requests
from flask import Flask, request
from telegram import Bot, Update
from telegram.ext import Dispatcher, CommandHandler, MessageHandler, Filters
from dotenv import load_dotenv

load_dotenv()

# Konfigurimi
BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
STABILITY_API_KEY = os.getenv("STABILITY_API_KEY")

bot = Bot(token=BOT_TOKEN)
app = Flask(__name__)

# AI Chat me OpenRouter
def generate_ai_reply(prompt):
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "nous-hermes2",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.9
    }
    response = requests.post("https://openrouter.ai/api/v1/chat/completions", json=data, headers=headers)
    if response.ok:
        return response.json()["choices"][0]["message"]["content"]
    else:
        return "⛔️ Ndodhi një gabim me AI-në."

# Gjenerim imazhi me Stable Diffusion
def generate_image(prompt):
    headers = {
        "Authorization": f"Bearer {STABILITY_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "text_prompts": [{"text": prompt}],
        "cfg_scale": 10,
        "clip_guidance_preset": "FAST_BLUE",
        "height": 512,
        "width": 512,
        "samples": 1,
        "steps": 30
    }
    res = requests.post("https://api.stability.ai/v1/generation/stable-diffusion-v1-5/text-to-image", headers=headers, json=data)
    if res.ok:
        img_data = res.json()["artifacts"][0]["base64"]
        return img_data
    else:
        return None

# Komanda Start
def start(update, context):
    update.message.reply_text("👋 Përshëndetje! Unë jam SpicyChatBot, një asistente virtuale erotike. Dërgo një mesazh për të filluar.")

# Komanda Help
def help_command(update, context):
    update.message.reply_text("📋 Komandat e disponueshme:\n/start – Fillimi\n/help – Ndihmë\n/image – Gjenero imazh\n/pay – Paguaj për Premium")

# Komanda Image
def image(update, context):
    prompt = " ".join(context.args)
    if not prompt:
        update.message.reply_text("✍️ Të lutem shkruaj një përshkrim për imazhin: /image një vajzë misterioze në plazh")
        return

    update.message.reply_text("🎨 Duke gjeneruar imazhin...")
    image_base64 = generate_image(prompt)
    if image_base64:
        update.message.reply_photo(photo=bytes.fromhex(image_base64.encode().hex()))
    else:
        update.message.reply_text("⛔️ Nuk u gjenerua dot imazhi.")

# Komanda Pay
def pay(update, context):
    update.message.reply_text("💸 Për të aktivizuar premium, na shkruaj ose vizito linkun në bio.")

# AI Chat
def handle_message(update, context):
    user_input = update.message.text
    reply = generate_ai_reply(user_input)
    update.message.reply_text(reply)

# Webhook
@app.route('/webhook', methods=['POST'])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return 'ok'

# Konfiguro dispatcher
dispatcher = Dispatcher(bot, None, workers=0)
dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(CommandHandler("help", help_command))
dispatcher.add_handler(CommandHandler("image", image))
dispatcher.add_handler(CommandHandler("pay", pay))
dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

# Home page
@app.route('/')
def home():
    return 'SpicyChatBot është aktiv 🟢'

if __name__ == '__main__':
    app.run(debug=False)

