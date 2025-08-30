#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для проверки работы Telegram бота
"""

from config import Config
from telegram_bot import SteamRentalBot

def check_bot():
    """Проверка работы Telegram бота"""
    print("🤖 Проверка Telegram бота...")
    
    print(f"🔑 TELEGRAM_TOKEN: {Config.TELEGRAM_TOKEN[:20]}..." if Config.TELEGRAM_TOKEN else "❌ TELEGRAM_TOKEN не найден")
    print(f"👤 TELEGRAM_ADMIN_ID: {Config.TELEGRAM_ADMIN_ID}")
    
    if not Config.TELEGRAM_TOKEN:
        print("❌ TELEGRAM_TOKEN не настроен!")
        return False
    
    if not Config.TELEGRAM_ADMIN_ID:
        print("❌ TELEGRAM_ADMIN_ID не настроен!")
        return False
    
    try:
        bot = SteamRentalBot()
        
        if bot.setup():
            print("✅ Telegram бот настроен успешно!")
            print(f"🔑 Admin ID: {bot.admin_id}")
            return True
        else:
            print("❌ Ошибка настройки Telegram бота")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка Telegram бота: {e}")
        return False

if __name__ == '__main__':
    check_bot()
