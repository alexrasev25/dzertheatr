import os
import time
import requests
from bs4 import BeautifulSoup
from flask import Flask, request
import telebot
from repet import check_repertoire
from threading import Thread
from bileti import generate_response
from podpis import subscription_manager

# Получаем токен из переменных окружения
BOT_TOKEN = os.getenv("BOT_TOKEN")

bot = telebot.TeleBot(BOT_TOKEN)
user_last_activity = {}

# Фоновые задачи
def remind_inactivity():
    while True:
        current_time = time.time()
        for user_id, last_time in list(user_last_activity.items()):
            if current_time - last_time > 3600:  # пример таймаута, замените INACTIVITY_TIMEOUT если нужно
                bot.send_message(user_id, "")
                user_last_activity[user_id] = time.time()
        time.sleep(60)


def background_tasks():
    while True:
        try:
            subscription_manager.check_subscriptions(bot)
            time.sleep(3600)  # Проверка каждый час
        except Exception as e:
            print(f"Ошибка в фоновых задачах: {e}")


# Запуск фоновых потоков сразу
Thread(target=background_tasks, daemon=True).start()
Thread(target=remind_inactivity, daemon=True).start()


# Обработка webhook
app = Flask(__name__)

@app.route("/", methods=["POST"])
def webhook():
    json_string = request.get_data().decode("utf-8")
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "ok", 200


# Основные команды и обработка сообщений
@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_last_activity[message.chat.id] = time.time()
    bot.send_photo(
        chat_id=message.chat.id,
        photo="https://www.dzerteatr.ru/zdanie_ban3.jpg",
        caption=(
            "Привет! Я могу помочь Вам узнать о наличии билетов на спектакли Дзержинского театра драмы.\n"
            "Напишите название спектакля, я найду его в афише.\n"
            "Вам останется выбрать дату и, если билеты есть в наличии, перейти к сервису покупки."
        )
    )


@bot.message_handler(func=lambda m: True)
def handle_messages(message):
    user_id = message.chat.id
    user_last_activity[user_id] = time.time()

    if message.text.lower() in ["спасибо", "до свидания"]:
        bot.reply_to(message, "Рад помочь! 😊")
        return

    check_spectacle(message)


def check_spectacle(message):
    try:
        query = message.text.strip()
        THEATER_URL = os.getenv("THEATER_URL")  # можно вынести в env
        response = requests.get(THEATER_URL, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')

        found = False
        for link in soup.find_all('a'):
            if query.lower() in link.text.lower():
                spectacle_name = link.text
                ticket_url = link['href'] if link['href'].startswith('http') else f"https://quicktickets.ru{link['href']}"

                response_data = generate_response(ticket_url)
                if response_data['reply_markup']:
                    markup = telebot.types.InlineKeyboardMarkup()
                    markup.add(
                        telebot.types.InlineKeyboardButton(
                            text="Купить билеты 🎟", url=ticket_url))
                    bot.send_message(
                        message.chat.id,
                        f"🎭 Нашёл: {spectacle_name}\n{response_data['text']}",
                        reply_markup=markup)
                else:
                    bot.reply_to(message,
                                 f"🎭 {spectacle_name}\n{response_data['text']}")

                found = True
                break

        if not found:
            bot.reply_to(message,
