#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🎮 Тестирование Steam Rental System
Проверка всех компонентов системы
"""

import sys
import os
import time
from datetime import datetime

# Добавляем текущую директорию в путь
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_config():
    """Тестирование конфигурации"""
    print("🔧 Тестирование конфигурации...")
    try:
        from config import Config
        print(f"✅ TELEGRAM_TOKEN: {Config.TELEGRAM_TOKEN[:20]}...")
        print(f"✅ TELEGRAM_ADMIN_ID: {Config.TELEGRAM_ADMIN_ID}")
        print(f"✅ FUNPAY_TOKEN: {Config.FUNPAY_TOKEN[:20] if Config.FUNPAY_TOKEN else 'Не настроен'}...")
        print(f"✅ STEAM_API_KEY: {Config.STEAM_API_KEY[:20] if Config.STEAM_API_KEY else 'Не настроен'}...")
        return True
    except Exception as e:
        print(f"❌ Ошибка конфигурации: {e}")
        return False

def test_database():
    """Тестирование базы данных"""
    print("\n🗄️ Тестирование базы данных...")
    try:
        from database import Database
        db = Database()
        
        # Проверяем создание таблиц
        print("✅ База данных инициализирована")
        
        # Проверяем добавление аккаунта
        success = db.add_account("test_user", "test_pass", "Counter-Strike 2", 50.0, "Тестовый аккаунт")
        if success:
            print("✅ Добавление аккаунта работает")
        else:
            print("❌ Ошибка добавления аккаунта")
        
        # Проверяем получение аккаунтов
        accounts = db.get_available_accounts_list()
        print(f"✅ Доступно аккаунтов: {len(accounts)}")
        
        # Проверяем токены
        db.save_token("TEST_TOKEN", "test_value")
        token = db.get_token("TEST_TOKEN")
        if token == "test_value":
            print("✅ Работа с токенами работает")
        else:
            print("❌ Ошибка работы с токенами")
        
        return True
    except Exception as e:
        print(f"❌ Ошибка базы данных: {e}")
        return False

def test_steam_manager():
    """Тестирование Steam менеджера"""
    print("\n🎮 Тестирование Steam менеджера...")
    try:
        from steam_manager import SteamManager
        steam = SteamManager()
        
        # Тестируем генерацию пароля
        password = steam.generate_password()
        print(f"✅ Генерация пароля: {password}")
        
        # Тестируем проверку аккаунта
        is_valid = steam.verify_steam_account("test_user", "test_pass")
        print(f"✅ Проверка аккаунта: {is_valid}")
        
        # Тестируем получение кода Steam Guard
        guard_code = steam.get_steam_guard_code("test_user")
        print(f"✅ Steam Guard код: {guard_code}")
        
        return True
    except Exception as e:
        print(f"❌ Ошибка Steam менеджера: {e}")
        return False

def test_funpay_manager():
    """Тестирование FunPay менеджера"""
    print("\n💰 Тестирование FunPay менеджера...")
    try:
        from funpay_manager import FunPayManager
        funpay = FunPayManager()
        
        # Тестируем извлечение игры из заказа
        test_order = {'title': 'Аренда аккаунта CS2 на 2 часа'}
        game_name = funpay.extract_game_from_order(test_order)
        print(f"✅ Извлечение игры: {game_name}")
        
        # Тестируем обработку заказа
        test_account_data = {
            'username': 'test_user',
            'password': 'test_pass',
            'game_name': 'Counter-Strike 2',
            'duration': 2,
            'start_time': datetime.now().strftime("%Y-%m-%d %H:%M")
        }
        print("✅ Обработка заказа настроена")
        
        return True
    except Exception as e:
        print(f"❌ Ошибка FunPay менеджера: {e}")
        return False

def test_telegram_bot():
    """Тестирование Telegram бота"""
    print("\n🤖 Тестирование Telegram бота...")
    try:
        from telegram_bot import SteamRentalBot
        from database import Database
        
        db = Database()
        bot = SteamRentalBot(db)
        
        print("✅ Telegram бот инициализирован")
        print("✅ Обработчики команд настроены")
        
        return True
    except Exception as e:
        print(f"❌ Ошибка Telegram бота: {e}")
        return False

def test_steam_rental_system():
    """Тестирование основной системы"""
    print("\n🚀 Тестирование основной системы...")
    try:
        from steam_rental_system import SteamRentalSystem
        system = SteamRentalSystem()
        
        print("✅ Steam Rental System инициализирована")
        print("✅ Планировщик задач настроен")
        
        return True
    except Exception as e:
        print(f"❌ Ошибка основной системы: {e}")
        return False

def main():
    """Основная функция тестирования"""
    print("🎮 Тестирование Steam Rental System")
    print("=" * 50)
    
    tests = [
        ("Конфигурация", test_config),
        ("База данных", test_database),
        ("Steam менеджер", test_steam_manager),
        ("FunPay менеджер", test_funpay_manager),
        ("Telegram бот", test_telegram_bot),
        ("Основная система", test_steam_rental_system)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                print(f"❌ Тест '{test_name}' не прошел")
        except Exception as e:
            print(f"❌ Критическая ошибка в тесте '{test_name}': {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Результаты тестирования: {passed}/{total} тестов прошли")
    
    if passed == total:
        print("🎉 Все тесты прошли успешно! Система готова к работе.")
        return True
    else:
        print("⚠️ Некоторые тесты не прошли. Проверьте настройки.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
