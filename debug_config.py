#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для отладки конфигурации
"""

import os
from config import Config

def debug_config():
    """Отладка конфигурации"""
    print("🔍 Отладка конфигурации...")
    print("=" * 50)
    
    # Проверяем переменные окружения напрямую
    print("📋 Переменные окружения:")
    print(f"TELEGRAM_TOKEN (env): {os.getenv('TELEGRAM_TOKEN', 'НЕ НАЙДЕН')}")
    print(f"TELEGRAM_ADMIN_ID (env): {os.getenv('TELEGRAM_ADMIN_ID', 'НЕ НАЙДЕН')}")
    print(f"FUNPAY_TOKEN (env): {os.getenv('FUNPAY_TOKEN', 'НЕ НАЙДЕН')}")
    print(f"STEAM_API_KEY (env): {os.getenv('STEAM_API_KEY', 'НЕ НАЙДЕН')}")
    
    print("\n📋 Значения из Config:")
    print(f"TELEGRAM_TOKEN (config): {Config.TELEGRAM_TOKEN}")
    print(f"TELEGRAM_ADMIN_ID (config): {Config.TELEGRAM_ADMIN_ID}")
    print(f"FUNPAY_TOKEN (config): {Config.FUNPAY_TOKEN}")
    print(f"STEAM_API_KEY (config): {Config.STEAM_API_KEY}")
    
    print("\n🔧 Проверка работоспособности:")
    
    # Проверяем токен
    if Config.TELEGRAM_TOKEN and Config.TELEGRAM_TOKEN != '':
        print("✅ TELEGRAM_TOKEN настроен")
        print(f"   Токен: {Config.TELEGRAM_TOKEN[:20]}...")
    else:
        print("❌ TELEGRAM_TOKEN не настроен")
    
    # Проверяем admin ID
    if Config.TELEGRAM_ADMIN_ID and Config.TELEGRAM_ADMIN_ID != '':
        print("✅ TELEGRAM_ADMIN_ID настроен")
        print(f"   Admin ID: {Config.TELEGRAM_ADMIN_ID}")
    else:
        print("❌ TELEGRAM_ADMIN_ID не настроен")
    
    # Проверяем FunPay
    if Config.FUNPAY_TOKEN and Config.FUNPAY_TOKEN != '' and Config.FUNPAY_TOKEN != 'your_funpay_token_here':
        print("✅ FUNPAY_TOKEN настроен")
        print(f"   Токен: {Config.FUNPAY_TOKEN[:20]}...")
    else:
        print("❌ FUNPAY_TOKEN не настроен")
    
    # Проверяем Steam
    if Config.STEAM_API_KEY and Config.STEAM_API_KEY != '' and Config.STEAM_API_KEY != 'your_steam_api_key_here':
        print("✅ STEAM_API_KEY настроен")
        print(f"   Ключ: {Config.STEAM_API_KEY[:20]}...")
    else:
        print("❌ STEAM_API_KEY не настроен")
    
    print("\n📊 Рекомендации:")
    
    if not Config.TELEGRAM_TOKEN or Config.TELEGRAM_TOKEN == '':
        print("⚠️ TELEGRAM_TOKEN не найден в переменных окружения")
        print("   Используется значение по умолчанию из config.py")
    
    if not Config.TELEGRAM_ADMIN_ID or Config.TELEGRAM_ADMIN_ID == '':
        print("⚠️ TELEGRAM_ADMIN_ID не найден в переменных окружения")
        print("   Используется значение по умолчанию из config.py")

if __name__ == '__main__':
    debug_config()
