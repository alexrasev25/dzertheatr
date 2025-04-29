import requests  # Добавьте этот импорт в начале файла
from bs4 import BeautifulSoup
import time
import re  # Для улучшенного поиска

# Кэш для хранения распарсенных данных (чтобы не делать запрос при каждом вызове)
_REPERTOIRE_CACHE = {
    'last_update': 0,
    'titles': []
}

def get_titles_from_site():
    """Получает список спектаклей с сайта театра"""
    try:
        url = "https://www.dzerteatr.ru/repertuar_news.html"
        response = requests.get(url, timeout=10)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')

        titles = []
        for h3 in soup.find_all('h3', class_='heading-48'):
            a_tag = h3.find('a')
            if a_tag and a_tag.text:
                titles.append(a_tag.text.strip())
        return titles
    except Exception as e:
        print(f"Ошибка при парсинге сайта: {e}")
        return []

def check_repertoire(play_name):
    """
    Проверяет наличие спектакля в репертуаре театра
    :param play_name: название спектакля для поиска
    :return: строку с результатом проверки
    """
    try:
        # Обновляем кэш не чаще чем раз в 10 минут
        if time.time() - _REPERTOIRE_CACHE['last_update'] > 600:
            _REPERTOIRE_CACHE['titles'] = get_titles_from_site()
            _REPERTOIRE_CACHE['last_update'] = time.time()

        titles = _REPERTOIRE_CACHE['titles']
        user_input = play_name.strip().lower()

        # Улучшенный поиск (ищет частичные совпадения)
        matching_titles = []
        for title in titles:
            title_lower = title.lower()
            # Ищем хотя бы одно слово из запроса
            if (user_input in title_lower or 
                any(word in title_lower for word in user_input.split())):
                matching_titles.append(title)

        if matching_titles:
            return (f"✅ Этот спектакль есть в репертуаре театра, но его нет в ближайшей афише:\n" +
                    "\n".join(f"- {title}" for title in matching_titles))
        else:
            return (f"❌ Спектакль '{play_name}' не найден в репертуаре.\n"
                    "Может быть он был раньше, или будет в будущем.")

    except Exception as e:
        return f"⚠️ Ошибка при проверке репертуара: {str(e)}"