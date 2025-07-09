#!/usr/bin/env python3
"""
Автоматический мониторинг сообщений Telegram бота
Запускается в фоновом режиме и обрабатывает сообщения каждые 10 секунд
"""

import os
import time
import asyncio
import logging
import signal
import sys
from datetime import datetime
from telegram import Bot
from telegram.error import TelegramError

# Импорт модуля для предотвращения автосна
try:
    from keep_alive import start_keep_alive
    KEEP_ALIVE_AVAILABLE = True
except ImportError:
    KEEP_ALIVE_AVAILABLE = False

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class BotMonitor:
    """Класс для мониторинга сообщений бота"""
    
    def __init__(self):
        self.token = os.environ.get("TELEGRAM_BOT_TOKEN")
        if not self.token:
            raise ValueError("TELEGRAM_BOT_TOKEN не найден")
        
        self.bot = Bot(token=self.token)
        self.last_update_id = 0
        self.running = True
    
    async def process_message(self, message):
        """Обработка одного сообщения"""
        try:
            chat_id = message.chat.id
            text = message.text.strip()
            user_name = message.from_user.first_name or "Пользователь"
            
            logger.info(f"📨 Сообщение от {user_name} ({chat_id}): {text}")
            
            response = None
            
            if text == "/start":
                response = (
                    f"🎉 Привет, {user_name}!\n\n"
                    "Добро пожаловать в систему управления KontrolPoint!\n\n"
                    "📋 Доступные команды:\n"
                    "/help - показать справку\n"
                    "/status - статус системы\n"
                    "/link логин - привязать аккаунт\n\n"
                    "Для привязки вашего аккаунта используйте команду /link с вашим логином."
                )
            elif text == "/help":
                response = (
                    "📖 Справка по командам:\n\n"
                    "🚀 /start - начать работу с ботом\n"
                    "❓ /help - показать эту справку\n"
                    "📊 /status - проверить статус системы\n"
                    "🔗 /link <логин> - привязать Telegram к аккаунту\n\n"
                    "💡 Пример использования:\n"
                    "/link admin - привязка аккаунта 'admin'\n\n"
                    "После привязки вы будете получать уведомления о новых задачах и изменениях в системе."
                )
            elif text == "/status":
                current_time = datetime.now().strftime('%d.%m.%Y %H:%M:%S')
                response = (
                    "🟢 Система KontrolPoint активна!\n\n"
                    f"⏰ Текущее время: {current_time}\n"
                    "🔄 Бот: Работает в автоматическом режиме\n"
                    "📡 Связь: Установлена\n"
                    "💾 База данных: Подключена\n\n"
                    "Все системы функционируют нормально!"
                )
            elif text.startswith("/link"):
                parts = text.split()
                if len(parts) >= 2:
                    username = parts[1]
                    response = (
                        f"🔗 Запрос на привязку аккаунта\n\n"
                        f"👤 Пользователь: {user_name}\n"
                        f"🆔 Telegram ID: {chat_id}\n"
                        f"📝 Логин для привязки: {username}\n\n"
                        "📋 Следующие шаги:\n"
                        "1. Войдите в веб-интерфейс KontrolPoint\n"
                        "2. Перейдите в 'Настройки Telegram'\n"
                        "3. Введите ваш Telegram ID и подтвердите\n\n"
                        "✅ После подтверждения вы начнете получать уведомления!"
                    )
                else:
                    response = (
                        "❌ Неправильный формат команды!\n\n"
                        "📝 Правильное использование:\n"
                        "/link ваш_логин\n\n"
                        "💡 Примеры:\n"
                        "/link admin\n"
                        "/link manager\n"
                        "/link production\n\n"
                        "Введите команду с вашим логином из системы KontrolPoint."
                    )
            else:
                response = (
                    f"❓ Неизвестная команда: {text}\n\n"
                    "📋 Доступные команды:\n"
                    "/start - начать работу\n"
                    "/help - справка\n"
                    "/status - статус системы\n"
                    "/link логин - привязка аккаунта\n\n"
                    "Используйте /help для подробной справки."
                )
            
            if response:
                await self.bot.send_message(chat_id=chat_id, text=response)
                logger.info(f"✅ Ответ отправлен пользователю {user_name} ({chat_id})")
        
        except Exception as e:
            logger.error(f"❌ Ошибка обработки сообщения: {e}")
    
    async def monitor_messages(self):
        """Основной цикл мониторинга"""
        logger.info("🚀 Запуск мониторинга сообщений...")
        
        while self.running:
            try:
                # Получаем обновления
                updates = await self.bot.get_updates(
                    offset=self.last_update_id + 1,
                    limit=5,
                    timeout=10
                )
                
                if updates:
                    logger.info(f"📩 Получено {len(updates)} новых сообщений")
                    
                    for update in updates:
                        if update.message and update.message.text:
                            await self.process_message(update.message)
                        
                        # Обновляем ID последнего обновления
                        self.last_update_id = max(self.last_update_id, update.update_id)
                
                # Пауза между проверками
                await asyncio.sleep(10)
            
            except TelegramError as e:
                logger.error(f"❌ Ошибка Telegram API: {e}")
                await asyncio.sleep(30)  # Увеличенная пауза при ошибке API
            
            except Exception as e:
                logger.error(f"❌ Неожиданная ошибка: {e}")
                await asyncio.sleep(60)  # Еще большая пауза при критической ошибке
    
    def stop(self):
        """Остановка мониторинга"""
        logger.info("⏹️ Остановка мониторинга...")
        self.running = False

# Обработчик сигналов для корректного завершения
def signal_handler(signum, frame):
    """Обработчик сигналов завершения"""
    print("\n⏹️ Получен сигнал завершения. Остановка бота...")
    if 'monitor' in globals():
        monitor.stop()
    sys.exit(0)

async def main():
    """Главная функция"""
    global monitor
    
    try:
        # Запускаем KeepAlive для предотвращения автосна
        if KEEP_ALIVE_AVAILABLE:
            start_keep_alive()
            logger.info("🔄 KeepAlive активирован для предотвращения автосна")
        
        # Создаем монитор
        monitor = BotMonitor()
        
        # Регистрируем обработчик сигналов
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        # Запускаем мониторинг
        await monitor.monitor_messages()
    
    except KeyboardInterrupt:
        logger.info("⏹️ Получен сигнал остановки (Ctrl+C)")
    except Exception as e:
        logger.error(f"💥 Критическая ошибка: {e}")
    finally:
        logger.info("🏁 Мониторинг завершен")

if __name__ == "__main__":
    print("🤖 Автоматический мониторинг Telegram бота KontrolPoint")
    print("📡 Проверка сообщений каждые 10 секунд")
    print("🛑 Для остановки нажмите Ctrl+C")
    print("-" * 50)
    
    asyncio.run(main())