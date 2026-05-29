import os
import threading
import datetime
import random
import logging
from flask import Flask
import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

# ========== 1. НАСТРОЙКА ЛОГИРОВАНИЯ ==========
if not os.path.exists('logs'):
    os.makedirs('logs')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/bot.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ========== 2. ИНИЦИАЛИЗАЦИЯ БОТА ==========
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
if not TELEGRAM_TOKEN:
    raise ValueError("Переменная окружения TELEGRAM_TOKEN не установлена!")
bot = telebot.TeleBot(TELEGRAM_TOKEN)

# ========== 3. КЛАВИАТУРЫ ==========
def main_menu_keyboard():
    """Главная клавиатура с кнопками"""
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    buttons = [
        KeyboardButton("ℹ️ Информация"),
        KeyboardButton("🕒 Время"),
        KeyboardButton("🎮 Игры"),
        KeyboardButton("📞 Помощь")
    ]
    keyboard.add(*buttons)
    return keyboard

def games_inline_keyboard():
    """Инлайн-клавиатура для игры 'Камень, ножницы, бумага'"""
    keyboard = InlineKeyboardMarkup(row_width=2)
    buttons = [
        InlineKeyboardButton("Камень 🪨", callback_data="rock"),
        InlineKeyboardButton("Ножницы ✂️", callback_data="scissors"),
        InlineKeyboardButton("Бумага 📄", callback_data="paper"),
        InlineKeyboardButton("❌ Закрыть меню", callback_data="close")
    ]
    keyboard.add(*buttons)
    return keyboard

# ========== 4. ЛОГИКА ИГРЫ ==========
game_choices = {
    "rock": "Камень 🪨",
    "scissors": "Ножницы ✂️",
    "paper": "Бумага 📄"
}

def determine_winner(player, bot_choice):
    if player == bot_choice:
        return "Ничья 🤝"
    if (player == "rock" and bot_choice == "scissors") or \
       (player == "scissors" and bot_choice == "paper") or \
       (player == "paper" and bot_choice == "rock"):
        return "Вы победили! 🎉"
    return "Победил бот 🤖"

# ========== 5. ОБРАБОТЧИКИ КОМАНД БОТА ==========
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    logger.info(f"Пользователь {message.from_user.id} вызвал /start или /help")
    bot.reply_to(message,
        "Привет! Я учебный бот.\n\n"
        "Доступные команды:\n"
        "/start — приветствие\n"
        "/help — эта справка\n"
        "/info — что я умею\n"
        "/time — текущее время\n"
        "/menu — показать кнопки\n"
        "/game — сыграть в игру\n"
        "А ещё просто напиши любой текст — я повторю."
    )

@bot.message_handler(commands=['info'])
def send_info(message):
    logger.info(f"Пользователь {message.from_user.id} запросил /info")
    bot.reply_to(message,
        "Я простой Telegram-бот.\n"
        "Создан в учебных целях.\n"
        "Мой язык — Python, библиотека pyTelegramBotAPI."
    )

@bot.message_handler(commands=['time'])
def send_time(message):
    now = datetime.datetime.now().strftime("%H:%M:%S")
    logger.info(f"Пользователь {message.from_user.id} запросил время")
    bot.reply_to(message, f"Текущее время: {now}")

@bot.message_handler(commands=['menu'])
def send_menu(message):
    """Показывает клавиатуру с кнопками"""
    logger.info(f"Пользователь {message.from_user.id} открыл меню")
    bot.send_message(message.chat.id, "Вот ваше меню:", reply_markup=main_menu_keyboard())

@bot.message_handler(commands=['game'])
def cmd_game(message):
    """Запускает игру"""
    logger.info(f"Пользователь {message.from_user.id} начал игру")
    bot.send_message(message.chat.id, "Выберите свой ход:", reply_markup=games_inline_keyboard())

# ========== 6. ОБРАБОТЧИК НАЖАТИЙ НА ИНЛАЙН-КНОПКИ ==========
@bot.callback_query_handler(func=lambda call: True)
def handle_game_query(call):
    if call.data in ["rock", "scissors", "paper"]:
        player_choice = call.data
        bot_choice = random.choice(["rock", "scissors", "paper"])
        result = determine_winner(player_choice, bot_choice)
        
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id,
                         f"Ваш ход: {game_choices[player_choice]}\n"
                         f"Ход бота: {game_choices[bot_choice]}\n"
                         f"Результат: **{result}**",
                         parse_mode="Markdown")
        logger.info(f"Игра: {call.from_user.id} выбрал {player_choice}, бот {bot_choice}, результат {result}")
    elif call.data == "close":
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
        bot.answer_callback_query(call.id, "Меню закрыто")
    else:
        bot.answer_callback_query(call.id, "Неизвестная команда")

# ========== 7. ОБРАБОТЧИК ВСЕХ ТЕКСТОВЫХ СООБЩЕНИЙ (КНОПКИ И ЭХО) ==========
@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    try:
        # Обработка нажатий на кнопки главного меню
        if message.text == "ℹ️ Информация":
            bot.reply_to(message, "Я простой учебный бот с расширенным функционалом. Использую Python, Flask, pyTelegramBotAPI.")
        elif message.text == "🕒 Время":
            now = datetime.datetime.now().strftime("%H:%M:%S")
            bot.reply_to(message, f"Текущее время: {now}")
        elif message.text == "🎮 Игры":
            cmd_game(message)  # Запускаем игру
        elif message.text == "📞 Помощь":
            bot.reply_to(message, "Доступны команды: /start, /help, /menu, /game, /info, /time")
        else:
            # Если сообщение не похоже на команду и не кнопка - эхо
            bot.reply_to(message, f"Вы сказали: {message.text}")
    except Exception as e:
        logger.error(f"Ошибка при обработке сообщения от {message.from_user.id}: {e}")
        bot.reply_to(message, "Произошла техническая ошибка. Попробуйте позже.")

# ========== 8. ЗАПУСК БОТА В ПОТОКЕ И ВЕБ-СЕРВЕРА ==========
def run_bot():
    logger.info("Telegram бот запущен и начал прослушивание сообщений")
    bot.infinity_polling()

# Flask-приложение для того, чтобы хостинг видел, что приложение живо
app = Flask(__name__)

@app.route('/')
def hello():
    return "Telegram бот запущен и работает! Логи пишутся в logs/bot.log"

if __name__ == '__main__':
    # Запускаем бота в отдельном потоке
    bot_thread = threading.Thread(target=run_bot)
    bot_thread.start()
    
    # Запускаем Flask-сервер
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
