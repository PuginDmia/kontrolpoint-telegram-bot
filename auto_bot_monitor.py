#!/usr/bin/env python3
"""
Исправленный Telegram бот для Render с HTTP сервером для health checks
"""

import os
import logging
import signal
import sys
import time
import threading
from datetime import datetime
from flask import Flask, request, jsonify
import requests

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Токен бота
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
if not TELEGRAM_BOT_TOKEN:
    logger.error("TELEGRAM_BOT_TOKEN не найден в переменных окружения!")
    sys.exit(1)

# Базовый URL Telegram API
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"

# Создаем Flask приложение для HTTP сервера
app = Flask(__name__)

class SimpleTelegramBot:
    """Простой обработчик Telegram бота"""
    
    def __init__(self):
        self.last_update_id = 0
        self.processed_messages = set()
        self.running = True
        logger.info("SimpleTelegramBot инициализирован")
    
    def send_message(self, chat_id, text):
        """Отправка сообщения через HTTP API"""
        try:
            url = f"{TELEGRAM_API_URL}/sendMessage"
            data = {
                'chat_id': chat_id,
                'text': text,
                'parse_mode': 'HTML'
            }
            
            response = requests.post(url, data=data, timeout=10)
            
            if response.status_code == 200:
                logger.info(f"Сообщение отправлено в чат {chat_id}")
                return True
            else:
                logger.error(f"Ошибка отправки: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Ошибка отправки сообщения: {e}")
            return False
    
    def get_updates(self):
        """Получение обновлений через HTTP API"""
        try:
            url = f"{TELEGRAM_API_URL}/getUpdates"
            params = {
                'offset': self.last_update_id + 1,
                'limit': 10,
                'timeout': 5
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data['ok']:
                    return data['result']
            
            return []
            
        except Exception as e:
            logger.error(f"Ошибка получения обновлений: {e}")
            return []
    
    def handle_message(self, message):
        """Обработка входящего сообщения"""
        try:
            message_id = f"{message['message_id']}_{message['chat']['id']}"
            
            if message_id in self.processed_messages:
                logger.info(f"Сообщение {message_id} уже обработано, пропускаем")
                return
            
            self.processed_messages.add(message_id)
            
            chat_id = message['chat']['id']
            
            if 'text' in message:
                text = message['text'].strip()
                logger.info(f"Получено сообщение: {text} от {chat_id}")
                
                if text.startswith('/start'):
                    self.send_start_response(chat_id)
                elif text.startswith('/help'):
                    self.send_help_response(chat_id)
                elif text.startswith('/status'):
                    self.send_status_response(chat_id)
                elif text.startswith('/link'):
                    self.handle_link_command(chat_id, text)
                else:
                    self.send_unknown_command_response(chat_id)
            
        except Exception as e:
            logger.error(f"Ошибка обработки сообщения: {e}")
    
    def send_start_response(self, chat_id):
        """Ответ на команду /start"""
        message = """
🤖 <b>Добро пожаловать в KontrolPoint!</b>

Этот бот поможет вам получать уведомления о задачах.

<b>Доступные команды:</b>
/help - показать справку
/status - проверить статус системы
/link [ID] - привязать аккаунт Telegram

Для получения уведомлений свяжите свой аккаунт командой /link
        """
        self.send_message(chat_id, message.strip())
    
    def send_help_response(self, chat_id):
        """Ответ на команду /help"""
        message = """
<b>📋 Справка по командам:</b>

/start - начать работу с ботом
/help - показать эту справку
/status - проверить статус системы
/link [ID] - привязать ваш Telegram к аккаунту KontrolPoint

<b>🔗 Привязка аккаунта:</b>
1. Войдите в свой аккаунт на KontrolPoint.ru
2. Перейдите в настройки Telegram
3. Скопируйте ваш User ID
4. Отправьте команду: /link [ваш_ID]

После привязки вы будете получать уведомления о новых задачах.
        """
        self.send_message(chat_id, message.strip())
    
    def send_status_response(self, chat_id):
        """Ответ на команду /status"""
        current_time = datetime.now().strftime('%d.%m.%Y %H:%M:%S')
        message = f"""
<b>✅ Статус системы</b>

🤖 Бот: Активен
🌐 KontrolPoint: Онлайн
⏰ Время: {current_time}

Все системы работают нормально!
        """
        self.send_message(chat_id, message.strip())
    
    def handle_link_command(self, chat_id, text):
        """Обработка команды /link"""
        parts = text.split()
        if len(parts) < 2:
            message = """
<b>❌ Неправильный формат команды</b>

Используйте: /link [ваш_User_ID]

Например: /link 123

Ваш User ID можно найти в настройках Telegram на сайте KontrolPoint.ru
            """
            self.send_message(chat_id, message.strip())
            return
        
        user_id = parts[1]
        message = f"""
<b>🔗 Запрос на привязку аккаунта</b>

User ID: {user_id}
Telegram ID: {chat_id}

Для завершения привязки перейдите в настройки Telegram на сайте KontrolPoint.ru и введите этот Telegram ID: <code>{chat_id}</code>
        """
        self.send_message(chat_id, message.strip())
    
    def send_unknown_command_response(self, chat_id):
        """Ответ на неизвестную команду"""
        message = """
❓ <b>Неизвестная команда</b>

Используйте /help для получения списка доступных команд.
        """
        self.send_message(chat_id, message.strip())
    
    def monitor_messages(self):
        """Основной цикл мониторинга сообщений"""
        logger.info("🚀 Запуск мониторинга сообщений...")
        
        while self.running:
            try:
                updates = self.get_updates()
                
                for update in updates:
                    if 'message' in update:
                        self.handle_message(update['message'])
                        self.last_update_id = update['update_id']
                    
                    # Очищаем старые сообщения (сохраняем только последние 1000)
                    if len(self.processed_messages) > 1000:
                        self.processed_messages = set(list(self.processed_messages)[-500:])
                
                # Пауза между проверками
                time.sleep(10)
                
            except Exception as e:
                logger.error(f"Ошибка в цикле мониторинга: {e}")
                time.sleep(30)  # Большая пауза при ошибке
        
        logger.info("Мониторинг сообщений остановлен")
    
    def stop(self):
        """Остановка мониторинга"""
        self.running = False

# Глобальный экземпляр бота
bot = SimpleTelegramBot()

# HTTP endpoints для Render
@app.route('/')
def health_check():
    """Health check endpoint для Render"""
    return jsonify({
        'status': 'OK',
        'bot': 'active',
        'timestamp': datetime.now().isoformat(),
        'service': 'kontrolpoint-telegram-bot'
    })

@app.route('/health')
def health():
    """Дополнительный health check"""
    return jsonify({'status': 'healthy'})

@app.route('/status')
def status():
    """Статус бота"""
    return jsonify({
        'bot_running': bot.running,
        'processed_messages': len(bot.processed_messages),
        'last_update_id': bot.last_update_id,
        'uptime': datetime.now().isoformat()
    })

def signal_handler(signum, frame):
    """Обработчик сигналов завершения"""
    logger.info(f"Получен сигнал {signum}. Остановка бота...")
    bot.stop()
    sys.exit(0)

def main():
    """Главная функция"""
    # Регистрируем обработчики сигналов
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    logger.info("KeepAlive запущен для https://kontrolpoint.ru")
    logger.info("Автоматический мониторинг Telegram бота активирован для предотвращения автосна")
    
    # Запускаем мониторинг сообщений в отдельном потоке
    monitor_thread = threading.Thread(target=bot.monitor_messages, daemon=True)
    monitor_thread.start()
    
    # Получаем порт из переменной окружения (Render устанавливает PORT)
    port = int(os.environ.get('PORT', 5000))
    
    logger.info(f"Запуск HTTP сервера на порту {port}")
    
    # Запускаем Flask сервер
    app.run(host='0.0.0.0', port=port, debug=False)

if __name__ == '__main__':
    main()