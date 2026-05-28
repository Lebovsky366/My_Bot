import os
import threading
import datetime
from flask import Flask
import telebot

# --- Инициализация бота ---
TELEGRAM_TOKEN = os.environ.get('8810806202:AAFnTdSPyDBbhZwIjx40Y-YJJ94OH_Xz0pg')
if not TELEGRAM_TOKEN:
    raise ValueError("Переменная окружения TELEGRAM_TOKEN не установлена!")
bot = telebot.TeleBot(TELEGRAM_TOKEN)


app = Flask(__name__)


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message,
        "Привет! Я учебный бот.\n\n"
        "Доступные команды:\n"
        "/start — приветствие\n"
        "/help — эта справка\n"
        "/info — что я умею\n"
        "/time — текущее время\n"
        "А ещё просто напиши любой текст — я повторю."
    )

@bot.message_handler(commands=['info'])
def send_info(message):
    bot.reply_to(message,
        "Я простой Telegram-бот.\n"
        "Создан в учебных целях.\n"
        "Мой язык — Python, библиотека pyTelegramBotAPI."
    )

@bot.message_handler(commands=['time'])
def send_time(message):
    now = datetime.datetime.now().strftime("%H:%M:%S")
    bot.reply_to(message, f"Текущее время: {now}")

@bot.message_handler(func=lambda message: True)
def echo_all(message):
    bot.reply_to(message, message.text)


def run_bot():
    print("Telegram бот запущен!")
    bot.infinity_polling()


@app.route('/')
def hello():
    return "Telegram бот запущен и работает!"


if __name__ == '__main__':

    bot_thread = threading.Thread(target=run_bot)
    bot_thread.start()
    

    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
