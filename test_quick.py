#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Быстрый тест исправлений
"""

def test_imports():
    """Тест импортов"""
    try:
        print("🔧 Тестирование импортов...")
        
        from config import Config
        print("✅ Config импортирован")
        
        from database import Database
        print("✅ Database импортирован")
        
        from steam_manager import SteamManager
        print("✅ SteamManager импортирован")
        
        from funpay_manager import FunPayManager
        print("✅ FunPayManager импортирован")
        
        from telegram_bot import SteamRentalBot
        print("✅ SteamRentalBot импортирован")
        
        from steam_rental_system import SteamRentalSystem
        print("✅ SteamRentalSystem импортирован")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка импорта: {e}")
        return False

def test_config():
    """Тест конфигурации"""
    try:
        print("\n🔧 Тестирование конфигурации...")
        
        from config import Config
        
        print(f"✅ TELEGRAM_TOKEN: {Config.TELEGRAM_TOKEN[:20]}...")
        print(f"✅ TELEGRAM_ADMIN_ID: {Config.TELEGRAM_ADMIN_ID}")
        print(f"✅ FUNPAY_TOKEN: {Config.FUNPAY_TOKEN[:20] if Config.FUNPAY_TOKEN else 'Не настроен'}...")
        print(f"✅ STEAM_API_KEY: {Config.STEAM_API_KEY[:20] if Config.STEAM_API_KEY else 'Не настроен'}...")
        
        # Проверяем устаревшие настройки
        print(f"✅ FUNPAY_LOGIN: {Config.FUNPAY_LOGIN[:20] if Config.FUNPAY_LOGIN else 'Не настроен'}...")
        print(f"✅ FUNPAY_PASSWORD: {'***' if Config.FUNPAY_PASSWORD else 'Не настроен'}")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка конфигурации: {e}")
        return False

def main():
    """Основная функция"""
    print("🚀 Быстрый тест исправлений")
    print("=" * 40)
    
    success = True
    
    if not test_imports():
        success = False
    
    if not test_config():
        success = False
    
    print("\n" + "=" * 40)
    if success:
        print("🎉 Все тесты прошли успешно!")
        print("✅ Система готова к запуску")
    else:
        print("❌ Некоторые тесты не прошли")
        print("⚠️ Проверьте исправления")
    
    return success

if __name__ == "__main__":
    main()
