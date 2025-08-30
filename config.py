import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Настройки FunPay
    FUNPAY_TOKEN = os.getenv('FUNPAY_TOKEN', 'your_funpay_token_here')
    FUNPAY_BASE_URL = 'https://funpay.com'
    
    # Устаревшие настройки (для совместимости)
    FUNPAY_LOGIN = os.getenv('FUNPAY_LOGIN', '')
    FUNPAY_PASSWORD = os.getenv('FUNPAY_PASSWORD', '')
    
    # Настройки Telegram бота
    TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN', '8200815840:AAFUEvg-sNOvNctvqQ2yBrrpKBvJxlwKg5g')
    TELEGRAM_ADMIN_ID = os.getenv('TELEGRAM_ADMIN_ID', '7890395437')
    
    # Проверка и логирование конфигурации
    print(f"🔧 Config: TELEGRAM_TOKEN = {TELEGRAM_TOKEN[:20] if TELEGRAM_TOKEN else 'НЕ НАЙДЕН'}...")
    print(f"🔧 Config: TELEGRAM_ADMIN_ID = {TELEGRAM_ADMIN_ID}")
    print(f"🔧 Config: FUNPAY_TOKEN = {FUNPAY_TOKEN[:20] if FUNPAY_TOKEN else 'НЕ НАЙДЕН'}...")
    
    # Настройки Steam
    STEAM_API_KEY = os.getenv('STEAM_API_KEY', 'your_steam_api_key_here')
    
    # Настройки базы данных
    DATABASE_PATH = 'steam_rental.db'
    
    # Настройки браузера
    BROWSER_HEADLESS = os.getenv('BROWSER_HEADLESS', 'True').lower() == 'true'
    BROWSER_TIMEOUT = 30
    
    # Настройки аренды
    DEFAULT_RENTAL_DURATION = 24  # часы
    PASSWORD_CHANGE_DELAY = 5  # минуты после окончания аренды
    
    # Часто задаваемые вопросы
    FAQ = {
        'Как работает аренда?': 'После оплаты вы получаете данные аккаунта Steam. Время аренды отсчитывается с момента получения данных.',
        'Что происходит после окончания аренды?': 'Пароль от аккаунта автоматически изменяется, и аккаунт снова становится доступным для аренды.',
        'Можно ли продлить аренду?': 'Да, вы можете продлить аренду, оплатив дополнительное время.',
        'Безопасно ли использовать арендованные аккаунты?': 'Да, все аккаунты проверены и безопасны для использования.',
        'Как получить поддержку?': 'Используйте команду /support для связи с администратором.'
    }
