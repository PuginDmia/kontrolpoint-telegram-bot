# KontrolPoint Telegram Bot

🤖 Автоматический Telegram бот для системы управления KontrolPoint.ru

## Возможности

- ✅ Автоматические ответы на команды 24/7
- ✅ Интеграция с системой задач
- ✅ Уведомления о новых задачах
- ✅ Голосовые сообщения через ChatGPT
- ✅ Привязка аккаунтов Telegram

## Развертывание на Render

### 1. Подключение репозитория
1. Зайдите на [render.com](https://render.com)
2. Создайте Web Service из этого GitHub репозитория
3. Выберите бесплатный план

### 2. Настройки сервиса
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `python auto_bot_monitor.py`
- **Environment Variable**: 
  - `TELEGRAM_BOT_TOKEN` = `7595296662:AAE4tPjCtHq2CugLLTmmskzr9o_HmxQ6zLc`

### 3. Автоматическое развертывание
При любых изменениях в репозитории Render автоматически обновит бота.

## Файлы проекта

- `auto_bot_monitor.py` - Основной файл бота
- `keep_alive.py` - Предотвращение автосна на Render
- `requirements.txt` - Python зависимости
- `Procfile` - Настройки запуска
- `runtime.txt` - Версия Python

## Статус

🟢 **Активен** - Бот работает 24/7 и отвечает на все команды

Последнее обновление: 09.07.2025 03:06

---
Создано для [KontrolPoint.ru](https://kontrolpoint.ru) - система управления производством кофейного оборудования
