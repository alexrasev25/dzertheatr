import telebot
import requests
from bs4 import BeautifulSoup
from telebot import types
from config_r import BOT_TOKEN

bot = telebot.TeleBot(BOT_TOKEN)

URL = "https://www.dzerteatr.ru/repertuar_news.html"
OTHER_BOT_LINK = "https://t.me/zapros25_bot"


def get_titles():
    response = requests.get(URL)
    response.encoding = 'utf-8'  # Указываем кодировку
    soup = BeautifulSoup(response.text, "html.parser")
    titles = [a.get_text(strip=True) for a in soup.select("h3.heading-48 a")]
    return titles


@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Введите название спектакля:")


@bot.message_handler(func=lambda message: True)
def check_title(message):
    user_input = message.text.strip().lower()
    titles = get_titles()
    matched = [title for title in titles if user_input in title.lower()]

    if matched:
        bot.send_message(message.chat.id, f"✅ Найден спектакль: {matched[0]}")
    else:
        bot.send_message(message.chat.id,
                         "❌ Такого спектакля в репертуаре театра нет.")

    # Добавляем кнопку перехода в другой бот
    markup = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton("Перейти в другой бот",
                                     url=OTHER_BOT_LINK)
    markup.add(btn)
    bot.send_message(message.chat.id,
                     "Можете перейти в другой бот:",
                     reply_markup=markup)


# Запускаем бота
bot.polling()
