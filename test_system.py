#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для проверки работоспособности системы
"""

import os
import sys
from config import Config
from database import Database
from telegram_bot import SteamRentalBot

def test_config():
    """Проверка конфигурации"""
    print("🔧 Проверка конфигурации...")
    
    # Проверяем переменные окружения
    required_vars = [
        'TELEGRAM_TOKEN',
        'TELEGRAM_ADMIN_ID',
        'FUNPAY_LOGIN',
        'FUNPAY_PASSWORD'
    ]
    
    missing_vars = []
    for var in required_vars:
        value = getattr(Config, var, None)
        if not value:
            missing_vars.append(var)
        else:
            print(f"✅ {var}: {'*' * len(str(value))} (скрыто)")
    
    if missing_vars:
        print(f"❌ Отсутствуют переменные: {', '.join(missing_vars)}")
        return False
    
    print("✅ Конфигурация корректна")
    return True

def test_database():
    """Проверка базы данных"""
    print("\n🗄️ Проверка базы данных...")
    
    try:
        db = Database()
        
        # Проверяем создание таблиц
        total_accounts = db.get_total_accounts()
        available_accounts = db.get_available_accounts()
        active_rentals = db.get_active_rentals()
        total_users = db.get_total_users()
        
        print(f"✅ База данных работает")
        print(f"📊 Статистика:")
        print(f"   • Всего аккаунтов: {total_accounts}")
        print(f"   • Доступно: {available_accounts}")
        print(f"   • В аренде: {active_rentals}")
        print(f"   • Пользователей: {total_users}")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка базы данных: {e}")
        return False

def test_telegram_bot():
    """Проверка Telegram бота"""
    print("\n🤖 Проверка Telegram бота...")
    
    try:
        bot = SteamRentalBot()
        
        if not bot.token:
            print("❌ TELEGRAM_TOKEN не настроен")
            return False
        
        if not bot.admin_id:
            print("❌ TELEGRAM_ADMIN_ID не настроен")
            return False
        
        # Проверяем настройку бота
        if bot.setup():
            print("✅ Telegram бот настроен корректно")
            print(f"🔑 Admin ID: {bot.admin_id}")
            return True
        else:
            print("❌ Ошибка настройки Telegram бота")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка Telegram бота: {e}")
        return False

def test_funpay_manager():
    """Проверка FunPay менеджера"""
    print("\n🛒 Проверка FunPay менеджера...")
    
    try:
        from funpay_manager import FunPayManager
        
        manager = FunPayManager()
        
        if not manager.login or not manager.password:
            print("❌ Данные для входа в FunPay не настроены")
            return False
        
        print("✅ FunPay менеджер инициализирован")
        print(f"🔗 URL: {manager.base_url}")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка FunPay менеджера: {e}")
        return False

def main():
    """Основная функция проверки"""
    print("🚀 Проверка работоспособности Steam Rental System")
    print("=" * 50)
    
    tests = [
        test_config,
        test_database,
        test_telegram_bot,
        test_funpay_manager
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ Ошибка выполнения теста: {e}")
            results.append(False)
    
    print("\n" + "=" * 50)
    print("📊 Результаты проверки:")
    
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        print("🎉 Все тесты пройдены! Система готова к работе.")
        return True
    else:
        print(f"⚠️ Пройдено {passed}/{total} тестов")
        print("❌ Система требует настройки")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
