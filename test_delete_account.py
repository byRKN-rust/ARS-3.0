#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тест функции удаления аккаунтов
"""

from database import Database

def test_delete_account():
    """Тест удаления аккаунта"""
    print("🧪 Тест удаления аккаунтов...")
    
    db = Database()
    
    # Получаем список всех аккаунтов
    accounts = db.get_all_accounts()
    print(f"📊 Всего аккаунтов: {len(accounts)}")
    
    if not accounts:
        print("❌ Нет аккаунтов для тестирования")
        return
    
    # Находим свободный аккаунт для удаления
    available_accounts = [acc for acc in accounts if not acc['is_rented']]
    
    if not available_accounts:
        print("❌ Нет свободных аккаунтов для удаления")
        return
    
    test_account = available_accounts[0]
    account_id = test_account['id']
    
    print(f"🎮 Тестируем удаление аккаунта #{account_id}")
    print(f"   Логин: {test_account['username']}")
    print(f"   Игра: {test_account['game_name']}")
    
    # Пытаемся удалить аккаунт
    success = db.delete_account(account_id)
    
    if success:
        print("✅ Аккаунт успешно удален!")
        
        # Проверяем, что аккаунт действительно удален
        remaining_accounts = db.get_all_accounts()
        remaining_ids = [acc['id'] for acc in remaining_accounts]
        
        if account_id not in remaining_ids:
            print("✅ Подтверждение: аккаунт удален из базы данных")
        else:
            print("❌ Ошибка: аккаунт все еще в базе данных")
    else:
        print("❌ Не удалось удалить аккаунт")
    
    # Показываем финальную статистику
    final_accounts = db.get_all_accounts()
    print(f"\n📊 Финальная статистика:")
    print(f"   Всего аккаунтов: {len(final_accounts)}")
    print(f"   Свободных: {len([acc for acc in final_accounts if not acc['is_rented']])}")
    print(f"   В аренде: {len([acc for acc in final_accounts if acc['is_rented']])}")

if __name__ == '__main__':
    test_delete_account()
