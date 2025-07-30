import os
from flask import Flask, request
from telegram import Bot, Update
from telegram.ext import Dispatcher, CommandHandler, MessageHandler, Filters

app = Flask(__name__)

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
bot = Bot(token=TELEGRAM_BOT_TOKEN)
dispatcher = Dispatcher(bot, None, workers=0)

def start(update, context):
    update.message.reply_text("Përshëndetje! Unë jam Aria Blaze, boti yt erotik AI. Shkruaj /chat për të biseduar me mua.")

start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)

@app.route('/webhook', methods=['POST'])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return 'ok'

if __name__ == '__main__':
    app.run(port=5000)
