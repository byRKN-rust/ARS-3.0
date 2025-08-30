# 🚀 Развертывание Steam Rental System

## 📋 Требования

- Python 3.8+
- SQLite3
- Доступ к интернету
- Telegram Bot Token
- FunPay аккаунт
- Steam API ключ

## 🔧 Установка на Railway

### 1. Подготовка проекта

1. Создайте новый проект на Railway
2. Подключите ваш GitHub репозиторий
3. Установите переменные окружения:

```env
TELEGRAM_TOKEN=ваш_токен_бота
TELEGRAM_ADMIN_ID=7890395437
FUNPAY_TOKEN=ваш_токен_funpay
STEAM_API_KEY=ваш_ключ_steam_api
```

### 2. Настройка Railway

В настройках Railway:
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `python main.py`
- **Health Check Path**: `/health`

### 3. Переменные окружения

Добавьте в Railway Environment Variables:

| Переменная | Значение | Описание |
|------------|----------|----------|
| `TELEGRAM_TOKEN` | `8200815840:AAFUEvg-s...` | Токен вашего Telegram бота |
| `TELEGRAM_ADMIN_ID` | `7890395437` | Ваш Telegram ID |
| `FUNPAY_TOKEN` | `ваш_токен` | Токен FunPay API |
| `STEAM_API_KEY` | `ваш_ключ` | Ключ Steam API |

## 🔧 Установка локально

### 1. Клонирование репозитория

```bash
git clone https://github.com/your-username/steam-rental-system.git
cd steam-rental-system
```

### 2. Установка зависимостей

```bash
pip install -r requirements.txt
```

### 3. Настройка переменных окружения

Создайте файл `.env`:

```env
TELEGRAM_TOKEN=ваш_токен_бота
TELEGRAM_ADMIN_ID=7890395437
FUNPAY_TOKEN=ваш_токен_funpay
STEAM_API_KEY=ваш_ключ_steam_api
```

### 4. Запуск системы

```bash
python main.py
```

## 🧪 Тестирование

### Запуск тестов

```bash
python test_final_system.py
```

### Проверка компонентов

```bash
# Проверка конфигурации
python -c "from config import Config; print('Config OK')"

# Проверка базы данных
python -c "from database import Database; db = Database(); print('Database OK')"

# Проверка бота
python -c "from telegram_bot import SteamRentalBot; print('Bot OK')"
```

## 🔍 Мониторинг

### Логи

Система ведет подробные логи всех операций:

```bash
# Просмотр логов в реальном времени
tail -f logs/steam_rental.log

# Поиск ошибок
grep "ERROR" logs/steam_rental.log
```

### Статус системы

Проверьте статус системы:

```bash
curl http://localhost:8080/health
```

## 🛠️ Устранение неполадок

### Проблемы с Telegram ботом

1. **Бот не отвечает**
   ```bash
   # Проверьте токен
   echo $TELEGRAM_TOKEN
   
   # Проверьте права бота
   # Бот должен иметь права на отправку сообщений
   ```

2. **Ошибка signal handling**
   ```bash
   # Перезапустите систему
   pkill -f "python main.py"
   python main.py
   ```

### Проблемы с FunPay

1. **Не удается войти в FunPay**
   ```bash
   # Проверьте токен
   echo $FUNPAY_TOKEN
   
   # Проверьте аккаунт FunPay
   # Убедитесь, что аккаунт не заблокирован
   ```

2. **Не обрабатываются заказы**
   ```bash
   # Проверьте логи
   grep "заказ" logs/steam_rental.log
   
   # Проверьте настройки объявлений
   ```

### Проблемы с базой данных

1. **Ошибки SQLite**
   ```bash
   # Проверьте права доступа
   ls -la steam_rental.db
   
   # Создайте резервную копию
   cp steam_rental.db backup_$(date +%Y%m%d).db
   ```

2. **Повреждение базы данных**
   ```bash
   # Восстановите из бэкапа
   cp backup_YYYYMMDD.db steam_rental.db
   ```

## 🔄 Обновление системы

### Автоматическое обновление

```bash
# Остановите систему
pkill -f "python main.py"

# Обновите код
git pull origin main

# Переустановите зависимости
pip install -r requirements.txt

# Запустите систему
python main.py
```

### Ручное обновление

1. Создайте резервную копию
2. Обновите код
3. Проверьте совместимость
4. Запустите миграции БД
5. Перезапустите систему

## 📊 Мониторинг производительности

### Метрики системы

- Количество активных аренд
- Время обработки заказов
- Количество ошибок
- Использование памяти

### Алерты

Настройте алерты на:
- Высокое использование CPU
- Много ошибок в логах
- Отсутствие ответа от бота
- Проблемы с базой данных

## 🔐 Безопасность

### Рекомендации

1. **Регулярно меняйте пароли**
2. **Используйте HTTPS**
3. **Ограничьте доступ к API**
4. **Ведите аудит логов**
5. **Регулярно обновляйте зависимости**

### Резервное копирование

```bash
# Автоматическое резервное копирование
0 3 * * * /path/to/backup_script.sh

# Скрипт резервного копирования
#!/bin/bash
cp steam_rental.db backup_$(date +%Y%m%d_%H%M%S).db
find . -name "backup_*.db" -mtime +7 -delete
```

## 📞 Поддержка

При возникновении проблем:

1. Проверьте логи системы
2. Запустите тесты: `python test_final_system.py`
3. Проверьте документацию
4. Обратитесь в поддержку

### Контакты

- **Telegram**: @your_support
- **Email**: support@your-domain.com
- **Документация**: https://your-docs.com

---

**🎮 Steam Rental System готов к работе!**
