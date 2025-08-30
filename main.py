#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🎮 Steam Rental System - Простая версия для Railway
"""

import os
import logging
import threading
import time
from flask import Flask, jsonify

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Создаем Flask приложение для Railway
app = Flask(__name__)

# Глобальные переменные для бота и системы
bot = None
system = None

@app.route('/')
def home():
    """Главная страница"""
    return jsonify({
        "status": "running",
        "service": "Steam Rental System",
        "bot": "active" if bot else "inactive",
        "system": "active" if system else "inactive"
    })

@app.route('/health')
def health():
    """Проверка здоровья сервиса"""
    return jsonify({
        "status": "healthy",
        "bot_running": bot is not None,
        "system_running": system is not None
    })

@app.route('/status')
def status():
    """Статус системы"""
    return jsonify({
        "status": "running",
        "message": "Steam Rental System готов к работе"
    })

def start_bot():
    """Запуск Telegram бота в отдельном потоке"""
    global bot
    try:
        # Импортируем здесь, чтобы избежать ошибок при деплое
        from telegram_bot import SteamRentalBot
        
        # Создаем и настраиваем полного бота
        bot = SteamRentalBot()
        if bot.setup():
            logger.info("Telegram бот настроен успешно")
            logger.info("Telegram бот запущен")
            bot.run()
        else:
            logger.error("Не удалось настроить Telegram бота")
            
    except Exception as e:
        logger.error(f"Ошибка запуска бота: {e}")
        # Не останавливаем приложение при ошибке бота

def start_system():
    """Запуск основной системы в отдельном потоке"""
    global system
    try:
        # Импортируем здесь, чтобы избежать ошибок при деплое
        from steam_rental_system import SteamRentalSystem
        system = SteamRentalSystem()
        logger.info("Основная система запущена")
        system.start()
    except Exception as e:
        logger.error(f"Ошибка запуска системы: {e}")
        # Не останавливаем приложение при ошибке системы

if __name__ == '__main__':
    logger.info("🚀 Запуск Steam Rental System...")
    
    # Отладка конфигурации
    try:
        from debug_config import debug_config
        debug_config()
    except Exception as e:
        logger.warning(f"Ошибка отладки конфигурации: {e}")
    
    # Инициализируем систему (добавляем тестовые аккаунты)
    try:
        from init_system import init_system
        init_system()
    except Exception as e:
        logger.warning(f"Ошибка инициализации системы: {e}")
    
    # Запускаем основную систему в отдельном потоке
    system_thread = threading.Thread(target=start_system, daemon=True)
    system_thread.start()
    
    # Ждем немного для инициализации системы
    time.sleep(3)
    
    # Запускаем бота в отдельном потоке
    bot_thread = threading.Thread(target=start_bot, daemon=True)
    bot_thread.start()
    
    # Ждем еще немного для инициализации бота
    time.sleep(3)
    
    # Запускаем Flask сервер
    port = int(os.environ.get('PORT', 5000))
    logger.info(f"Запуск веб-сервера на порту {port}")
    app.run(host='0.0.0.0', port=port, debug=False)
