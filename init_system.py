#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт инициализации системы
Добавляет тестовые аккаунты при первом запуске
"""

import os
from database import Database

def init_system():
    """Инициализация системы"""
    print("🚀 Инициализация Steam Rental System...")
    
    db = Database()
    
    # Проверяем, есть ли уже аккаунты в базе
    total_accounts = db.get_total_accounts()
    
    if total_accounts > 0:
        print(f"✅ Система уже инициализирована. Аккаунтов в базе: {total_accounts}")
        return
    
    print("📝 Добавление тестовых аккаунтов...")
    
    # Список тестовых аккаунтов
    test_accounts = [
        {
            'username': 'test_account_1',
            'password': 'test_pass_1',
            'game_name': 'Counter-Strike 2'
        },
        {
            'username': 'test_account_2',
            'password': 'test_pass_2',
            'game_name': 'Dota 2'
        },
        {
            'username': 'test_account_3',
            'password': 'test_pass_3',
            'game_name': 'PUBG'
        },
        {
            'username': 'test_account_4',
            'password': 'test_pass_4',
            'game_name': 'Valorant'
        },
        {
            'username': 'test_account_5',
            'password': 'test_pass_5',
            'game_name': 'League of Legends'
        }
    ]
    
    added_count = 0
    for account in test_accounts:
        try:
            db.add_steam_account(
                username=account['username'],
                password=account['password'],
                game_name=account['game_name']
            )
            added_count += 1
            print(f"✅ Добавлен аккаунт: {account['username']} ({account['game_name']})")
        except Exception as e:
            print(f"❌ Ошибка добавления аккаунта {account['username']}: {e}")
    
    print(f"\n🎉 Инициализация завершена!")
    print(f"📊 Добавлено аккаунтов: {added_count}")
    print(f"📊 Всего в базе: {db.get_total_accounts()}")
    print(f"📊 Доступно: {db.get_available_accounts()}")

if __name__ == '__main__':
    init_system()
