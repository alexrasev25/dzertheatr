import json
from pathlib import Path
from datetime import datetime
import telebot
from bileti import check_available_tickets

class SubscriptionManager:
    def __init__(self):
        self.subscriptions_file = Path('subscriptions.json')
        self.subscriptions = self._load_subscriptions()

    def _load_subscriptions(self):
        """Загружает подписки из файла"""
        if not self.subscriptions_file.exists():
            return {}
        try:
            with open(self.subscriptions_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Ошибка загрузки подписок: {e}")
            return {}

    def save_subscriptions(self):
        """Сохраняет подписки в файл"""
        try:
            with open(self.subscriptions_file, 'w') as f:
                json.dump(self.subscriptions, f, indent=2)
        except Exception as e:
            print(f"Ошибка сохранения подписок: {e}")

    def add_subscription(self, chat_id, spectacle_name):
        """Добавляет новую подписку"""
        chat_id = str(chat_id)
        if chat_id not in self.subscriptions:
            self.subscriptions[chat_id] = {}

        if spectacle_name not in self.subscriptions[chat_id]:
            self.subscriptions[chat_id][spectacle_name] = {
                'last_check': None,
                'was_available': False
            }
            self.save_subscriptions()
            return True
        return False

    def check_subscriptions(self, bot):
        """Проверяет все подписки"""
        for chat_id, spectacles in self.subscriptions.items():
            for spectacle, data in spectacles.items():
                # Здесь должна быть логика проверки билетов
                # и отправки уведомлений через bot.send_message()
                pass

# Глобальный экземпляр
subscription_manager = SubscriptionManager()