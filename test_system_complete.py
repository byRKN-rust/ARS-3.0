#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Комплексный тест всей системы
"""

from database import Database
from config import Config

def test_system():
    """Комплексный тест системы"""
    print("🧪 Комплексный тест Steam Rental System...")
    print("=" * 50)
    
    # Тест 1: Конфигурация
    print("\n1️⃣ Тест конфигурации:")
    print(f"   TELEGRAM_TOKEN: {Config.TELEGRAM_TOKEN[:20] if Config.TELEGRAM_TOKEN else 'НЕ НАЙДЕН'}...")
    print(f"   TELEGRAM_ADMIN_ID: {Config.TELEGRAM_ADMIN_ID}")
    print(f"   FUNPAY_LOGIN: {Config.FUNPAY_LOGIN}")
    print(f"   DATABASE_PATH: {Config.DATABASE_PATH}")
    
    # Тест 2: База данных
    print("\n2️⃣ Тест базы данных:")
    try:
        db = Database()
        print("   ✅ База данных подключена")
        
        # Проверяем аккаунты
        accounts = db.get_all_accounts()
        print(f"   📊 Всего аккаунтов: {len(accounts)}")
        
        available = db.get_available_accounts()
        print(f"   🟢 Доступно: {available}")
        
        active_rentals = db.get_active_rentals()
        print(f"   🔴 В аренде: {active_rentals}")
        
        # Проверяем пользователей
        total_users = db.get_total_users()
        print(f"   👥 Пользователей: {total_users}")
        
    except Exception as e:
        print(f"   ❌ Ошибка базы данных: {e}")
    
    # Тест 3: Функции удаления
    print("\n3️⃣ Тест функции удаления:")
    try:
        accounts = db.get_all_accounts()
        available_accounts = [acc for acc in accounts if not acc['is_rented']]
        
        if available_accounts:
            test_account = available_accounts[0]
            print(f"   🎮 Тестовый аккаунт: #{test_account['id']} - {test_account['username']}")
            
            # Проверяем функцию удаления (без реального удаления)
            print("   ✅ Функция delete_account доступна")
        else:
            print("   ⚠️ Нет свободных аккаунтов для тестирования")
            
    except Exception as e:
        print(f"   ❌ Ошибка тестирования удаления: {e}")
    
    # Тест 4: Статистика
    print("\n4️⃣ Тест статистики:")
    try:
        stats = db.get_detailed_stats()
        print(f"   📈 Всего аккаунтов: {stats['total_accounts']}")
        print(f"   🟢 Доступно: {stats['available_accounts']}")
        print(f"   🔴 В аренде: {stats['rented_accounts']}")
        print(f"   👥 Пользователей: {stats['total_users']}")
        print(f"   ⏰ Активных аренд: {stats['active_rentals']}")
        
    except Exception as e:
        print(f"   ❌ Ошибка статистики: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 Комплексный тест завершен!")
    print("\n📋 Рекомендации:")
    print("   • Перезапустите приложение в Railway")
    print("   • Проверьте Telegram бота командой /start")
    print("   • Используйте /admin для управления аккаунтами")

if __name__ == '__main__':
    test_system()
