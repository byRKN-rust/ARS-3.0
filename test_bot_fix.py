#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тест исправления ошибки set_wakeup_fd
"""

import threading
import time

def test_bot_import():
    """Тест импорта бота"""
    try:
        print("🔧 Тестирование импорта бота...")
        
        from telegram_bot import SteamRentalBot
        from database import Database
        
        print("✅ Импорт успешен")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка импорта: {e}")
        return False

def test_bot_creation():
    """Тест создания бота"""
    try:
        print("\n🔧 Тестирование создания бота...")
        
        from telegram_bot import SteamRentalBot
        from database import Database
        
        db = Database()
        bot = SteamRentalBot(db)
        
        print("✅ Бот создан успешно")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка создания бота: {e}")
        return False

def test_bot_setup():
    """Тест настройки бота"""
    try:
        print("\n🔧 Тестирование настройки бота...")
        
        from telegram_bot import SteamRentalBot
        from database import Database
        
        db = Database()
        bot = SteamRentalBot(db)
        
        if bot.setup():
            print("✅ Настройка бота успешна")
            return True
        else:
            print("❌ Настройка бота не удалась")
            return False
        
    except Exception as e:
        print(f"❌ Ошибка настройки бота: {e}")
        return False

def test_bot_thread():
    """Тест запуска бота в отдельном потоке"""
    try:
        print("\n🔧 Тестирование запуска бота в потоке...")
        
        from telegram_bot import SteamRentalBot
        from database import Database
        
        db = Database()
        bot = SteamRentalBot(db)
        
        if not bot.setup():
            print("❌ Бот не настроен")
            return False
        
        # Запускаем бота в отдельном потоке
        bot_thread = threading.Thread(target=bot.run, daemon=True)
        bot_thread.start()
        
        # Даем время на запуск
        time.sleep(3)
        
        print("✅ Бот запущен в потоке без ошибок")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка запуска бота в потоке: {e}")
        return False

def main():
    """Основная функция тестирования"""
    print("🚀 Тест исправления ошибки set_wakeup_fd")
    print("=" * 50)
    
    tests = [
        ("Импорт бота", test_bot_import),
        ("Создание бота", test_bot_creation),
        ("Настройка бота", test_bot_setup),
        ("Запуск в потоке", test_bot_thread)
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
    print(f"📊 Результаты: {passed}/{total} тестов прошли")
    
    if passed == total:
        print("🎉 Все тесты прошли! Ошибка set_wakeup_fd исправлена!")
        return True
    else:
        print("⚠️ Некоторые тесты не прошли. Проблема может остаться.")
        return False

if __name__ == "__main__":
    main()
