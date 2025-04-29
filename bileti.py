import requests
from bs4 import BeautifulSoup
import re

def check_available_tickets(url):
    """Проверяет наличие билетов на странице"""
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Проверка основных индикаторов
        sold_out = soup.find_all(string=re.compile(r'(мест нет|продано)', re.IGNORECASE))
        if sold_out:
            return False

        return True  # Если явных признаков "нет билетов" не найдено

    except Exception as e:
        print(f"Ошибка проверки билетов: {e}")
        return False

def generate_response(url):
    """Генерирует ответ бота"""
    has_tickets = check_available_tickets(url)

    if has_tickets:
        return {
            'text': "✅ Есть свободные места!",
            'reply_markup': True
        }
    return {
        'text': "❌ Сейчас билетов нет. Попробуйте позже.",
        'reply_markup': False
    }
