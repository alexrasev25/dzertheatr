import telebot
import time
import requests
from bs4 import BeautifulSoup
from config import BOT_TOKEN, THEATER_URL, INACTIVITY_TIMEOUT
from repet import check_repertoire
from threading import Thread
from bileti import generate_response
from podpis import subscription_manager

bot = telebot.TeleBot(BOT_TOKEN)
user_last_activity = {}


def run_bot():
    bot.polling(none_stop=True, interval=1)


@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_last_activity[message.chat.id] = time.time()
    bot.send_photo(
        chat_id=message.chat.id,
        photo="https://www.dzerteatr.ru/zdanie_ban3.jpg",
        caption=
        "Привет! Я могу помочь Вам узнать о наличии билетов на спектакли Дзержинского театра драмы.\n"
        "Напишите название спектакля, я найду его в афише.\n"
        "Вам останется выбрать дату и, если билеты есть в наличии, перейти к сервису покупки."
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
        response = requests.get(THEATER_URL, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')

        found = False
        for link in soup.find_all('a'):
            if query.lower() in link.text.lower():
                spectacle_name = link.text
                ticket_url = link['href'] if link['href'].startswith(
                    'http') else f"https://quicktickets.ru{link['href']}"

                response = generate_response(ticket_url)
                if response['reply_markup']:
                    markup = telebot.types.InlineKeyboardMarkup()
                    markup.add(
                        telebot.types.InlineKeyboardButton(
                            text="Купить билеты 🎟", url=ticket_url))
                    bot.send_message(
                        message.chat.id,
                        f"🎭 Нашёл: {spectacle_name}\n{response['text']}",
                        reply_markup=markup)
                else:
                    bot.reply_to(message,
                                 f"🎭 {spectacle_name}\n{response['text']}")

                found = True
                break

        if not found:
            bot.reply_to(message,
                         "Проверяю репертуар...\n\n" + check_repertoire(query))

    except Exception as e:
        bot.reply_to(message, f"⚠️ Ошибка: {str(e)}")


def remind_inactivity():
    while True:
        current_time = time.time()
        for user_id, last_time in list(user_last_activity.items()):
            if current_time - last_time > INACTIVITY_TIMEOUT:
                bot.send_message(user_id, "")
                user_last_activity[user_id] = time.time()
        time.sleep(60)


# Добавляем команды для подписок (в любое место после создания bot)
@bot.message_handler(commands=['subscribe'])
def handle_subscribe(message):
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        bot.reply_to(message, "Укажите: /subscribe Название")
        return

    spectacle = args[1].strip()
    if subscription_manager.add_subscription(message.chat.id, spectacle):
        bot.reply_to(message, f"✅ Подписка на «{spectacle}» оформлена!")
    else:
        bot.reply_to(message, f"ℹ️ Вы уже подписаны на «{spectacle}»")


# В фоновые задачи добавляем проверку подписок
def background_tasks():
    while True:
        try:
            subscription_manager.check_subscriptions(bot)
            time.sleep(3600)  # Проверка каждый час
        except Exception as e:
            print(f"Ошибка в фоновых задачах: {e}")


Thread(target=background_tasks, daemon=True).start()

if __name__ == '__main__':
    Thread(target=run_bot, daemon=True).start()
    Thread(target=remind_inactivity, daemon=True).start()
    while True:
        time.sleep(1)
