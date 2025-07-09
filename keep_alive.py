#!/usr/bin/env python3
"""
Дополнительный модуль для предотвращения автосна на Render
Отправляет ping каждые 10 минут для поддержания активности
"""

import requests
import time
import threading
import os
import logging

logger = logging.getLogger(__name__)

class KeepAlive:
    """Класс для поддержания активности сервиса"""
    
    def __init__(self, service_url=None):
        # Автоматически определяем URL сервиса
        if service_url:
            self.service_url = service_url
        else:
            # Для Render автоматически формируем URL
            app_name = os.environ.get('RENDER_SERVICE_NAME', 'kontrolpoint-bot')
            self.service_url = f"https://{app_name}.onrender.com"
        
        self.running = True
        self.ping_interval = 600  # 10 минут
    
    def ping_service(self):
        """Отправка ping запросов"""
        while self.running:
            try:
                response = requests.get(f"{self.service_url}/health", timeout=30)
                if response.status_code == 200:
                    logger.info(f"✅ Ping успешен: {self.service_url}")
                else:
                    logger.warning(f"⚠️ Ping неуспешен: {response.status_code}")
            except Exception as e:
                logger.error(f"❌ Ошибка ping: {e}")
            
            time.sleep(self.ping_interval)
    
    def start(self):
        """Запуск ping в отдельном потоке"""
        ping_thread = threading.Thread(target=self.ping_service)
        ping_thread.daemon = True
        ping_thread.start()
        logger.info(f"🔄 KeepAlive запущен для {self.service_url}")
    
    def stop(self):
        """Остановка ping"""
        self.running = False
        logger.info("⏹️ KeepAlive остановлен")

# Глобальный экземпляр
keep_alive = KeepAlive()

def start_keep_alive():
    """Функция для запуска из основного скрипта"""
    keep_alive.start()

if __name__ == "__main__":
    # Тестовый запуск
    keep_alive.start()
    print("KeepAlive запущен. Нажмите Ctrl+C для остановки.")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        keep_alive.stop()
        print("KeepAlive остановлен.")