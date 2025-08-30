#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тест конфигурации
"""

from config import Config

def test_config():
    """Тест конфигурации"""
    print("🧪 Тест конфигурации...")
    
    # Проверяем токен
    if Config.TELEGRAM_TOKEN:
        print(f"✅ TELEGRAM_TOKEN: {Config.TELEGRAM_TOKEN[:20]}...")
    else:
        print("❌ TELEGRAM_TOKEN не найден")
        return False
    
    # Проверяем admin ID
    if Config.TELEGRAM_ADMIN_ID:
        print(f"✅ TELEGRAM_ADMIN_ID: {Config.TELEGRAM_ADMIN_ID}")
    else:
        print("❌ TELEGRAM_ADMIN_ID не найден")
        return False
    
    # Проверяем FunPay
    if Config.FUNPAY_LOGIN:
        print(f"✅ FUNPAY_LOGIN: {Config.FUNPAY_LOGIN}")
    else:
        print("❌ FUNPAY_LOGIN не найден")
    
    if Config.FUNPAY_PASSWORD:
        print(f"✅ FUNPAY_PASSWORD: {Config.FUNPAY_PASSWORD}")
    else:
        print("❌ FUNPAY_PASSWORD не найден")
    
    print("🎉 Тест конфигурации завершен!")
    return True

if __name__ == '__main__':
    test_config()
