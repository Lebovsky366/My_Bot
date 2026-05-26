import telebot
import datetime

TOKEN = '8810806202:AAFnTdSPyDBbhZwIjx40Y-YJJ94OH_Xz0pg'

bot = telebot.TeleBot(TOKEN)

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

print("Бот запущен...")
bot.infinity_polling()