#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для добавления тестовых аккаунтов в базу данных
"""

from database import Database
import datetime

def add_test_accounts():
    """Добавление тестовых аккаунтов"""
    db = Database()
    
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
    
    print("🎮 Добавление тестовых аккаунтов...")
    
    for account in test_accounts:
        try:
            db.add_steam_account(
                username=account['username'],
                password=account['password'],
                game_name=account['game_name']
            )
            print(f"✅ Добавлен аккаунт: {account['username']} ({account['game_name']})")
        except Exception as e:
            print(f"❌ Ошибка добавления аккаунта {account['username']}: {e}")
    
    print(f"\n📊 Статистика:")
    print(f"• Всего аккаунтов: {db.get_total_accounts()}")
    print(f"• Доступно: {db.get_available_accounts()}")
    print(f"• В аренде: {db.get_active_rentals()}")

if __name__ == '__main__':
    add_test_accounts()
