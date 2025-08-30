import sqlite3
import datetime
from typing import List, Dict, Optional
from config import Config

class Database:
    def __init__(self, db_path: str = None):
        self.db_path = db_path or Config.DATABASE_PATH
        self.init_database()
    
    def init_database(self):
        """Инициализация базы данных и создание таблиц"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Таблица аккаунтов Steam
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS steam_accounts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL,
                    password TEXT NOT NULL,
                    game_name TEXT NOT NULL,
                    price REAL DEFAULT 50.0,
                    description TEXT DEFAULT '',
                    is_rented BOOLEAN DEFAULT FALSE,
                    current_renter_id TEXT,
                    rental_start_time DATETIME,
                    rental_end_time DATETIME,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Таблица аренды
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS rentals (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    account_id INTEGER,
                    renter_id TEXT NOT NULL,
                    start_time DATETIME NOT NULL,
                    end_time DATETIME NOT NULL,
                    duration_hours INTEGER NOT NULL,
                    status TEXT DEFAULT 'active',
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (account_id) REFERENCES steam_accounts (id)
                )
            ''')
            
            # Таблица пользователей
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    telegram_id TEXT UNIQUE NOT NULL,
                    username TEXT,
                    first_name TEXT,
                    last_name TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # НОВАЯ таблица бонусов
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS bonuses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    bonus_minutes INTEGER NOT NULL,
                    reason TEXT NOT NULL,
                    is_used BOOLEAN DEFAULT FALSE,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # НОВАЯ таблица уведомлений
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS notifications (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    message TEXT NOT NULL,
                    type TEXT NOT NULL,
                    is_read BOOLEAN DEFAULT FALSE,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # НОВАЯ таблица истории операций
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS operation_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    operation_type TEXT NOT NULL,
                    description TEXT NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # НОВАЯ таблица статистики
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS statistics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    game_name TEXT NOT NULL,
                    total_rentals INTEGER DEFAULT 0,
                    total_revenue REAL DEFAULT 0.0,
                    average_rating REAL DEFAULT 0.0,
                    total_reviews INTEGER DEFAULT 0,
                    last_updated DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
    
    def add_steam_account(self, username: str, password: str, game_name: str) -> int:
        """Добавление нового аккаунта Steam"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO steam_accounts (username, password, game_name)
                VALUES (?, ?, ?)
            ''', (username, password, game_name))
            conn.commit()
            return cursor.lastrowid
    
    def get_available_accounts(self, game_name: str = None) -> List[Dict]:
        """Получение доступных аккаунтов"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            if game_name:
                cursor.execute('''
                    SELECT * FROM steam_accounts 
                    WHERE is_rented = FALSE AND game_name = ?
                ''', (game_name,))
            else:
                cursor.execute('''
                    SELECT * FROM steam_accounts 
                    WHERE is_rented = FALSE
                ''')
            
            columns = [description[0] for description in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    def rent_account(self, account_id: int, renter_id: str, duration_hours: int) -> bool:
        """Аренда аккаунта"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Проверяем, доступен ли аккаунт
            cursor.execute('''
                SELECT is_rented FROM steam_accounts WHERE id = ?
            ''', (account_id,))
            
            result = cursor.fetchone()
            if not result or result[0]:
                return False
            
            start_time = datetime.now()
            end_time = start_time + datetime.timedelta(hours=duration_hours)
            
            # Обновляем статус аккаунта
            cursor.execute('''
                UPDATE steam_accounts 
                SET is_rented = TRUE, current_renter_id = ?, 
                    rental_start_time = ?, rental_end_time = ?
                WHERE id = ?
            ''', (renter_id, start_time, end_time, account_id))
            
            # Создаем запись об аренде
            cursor.execute('''
                INSERT INTO rentals (account_id, renter_id, start_time, end_time, duration_hours)
                VALUES (?, ?, ?, ?, ?)
            ''', (account_id, renter_id, start_time, end_time, duration_hours))
            
            # Добавляем в историю операций
            cursor.execute('''
                INSERT INTO operation_history (user_id, operation_type, description)
                VALUES (?, ?, ?)
            ''', (renter_id, 'rental_start', f'Начата аренда аккаунта на {duration_hours} часов'))
            
            conn.commit()
            return True
    
    def get_rental_info(self, renter_id: str) -> Optional[Dict]:
        """Получение информации об аренде пользователя"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT sa.username, sa.game_name, r.start_time, r.end_time, r.duration_hours
                FROM steam_accounts sa
                JOIN rentals r ON sa.id = r.account_id
                WHERE r.renter_id = ? AND r.status = 'active'
                ORDER BY r.end_time DESC
                LIMIT 1
            ''', (renter_id,))
            
            result = cursor.fetchone()
            if result:
                return {
                    'username': result[0],
                    'game_name': result[1],
                    'start_time': result[2],
                    'end_time': result[3],
                    'duration_hours': result[4]
                }
            return None
    
    def get_remaining_time(self, renter_id: str) -> Optional[str]:
        """Получение оставшегося времени аренды"""
        rental_info = self.get_rental_info(renter_id)
        if not rental_info:
            return "У вас нет активной аренды"
        
        end_time = datetime.fromisoformat(rental_info['end_time'])
        now = datetime.now()
        
        if now >= end_time:
            return "Время аренды истекло"
        
        remaining = end_time - now
        hours = int(remaining.total_seconds() // 3600)
        minutes = int((remaining.total_seconds() % 3600) // 60)
        
        return f"Осталось: {hours}ч {minutes}м"
    
    def end_expired_rentals(self) -> int:
        """Завершение истекших аренд"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Находим истекшие аренды
                cursor.execute('''
                    SELECT r.id, r.account_id, r.renter_id
                    FROM rentals r
                    WHERE r.status = 'active' AND r.end_time < datetime('now')
                ''')
                
                expired_rentals = cursor.fetchall()
                expired_count = len(expired_rentals)
                
                for rental in expired_rentals:
                    rental_id, account_id, renter_id = rental
                    
                    # Обновляем статус аренды
                    cursor.execute('''
                        UPDATE rentals 
                        SET status = 'completed' 
                        WHERE id = ?
                    ''', (rental_id,))
                    
                    # Освобождаем аккаунт
                    cursor.execute('''
                        UPDATE steam_accounts 
                        SET is_rented = FALSE, current_renter_id = NULL,
                            rental_start_time = NULL, rental_end_time = NULL
                        WHERE id = ?
                    ''', (account_id,))
                    
                    # Добавляем в историю операций
                    cursor.execute('''
                        INSERT INTO operation_history (user_id, operation_type, description)
                        VALUES (?, ?, ?)
                    ''', (renter_id, 'rental_end', f'Завершена аренда аккаунта #{account_id}'))
                
                conn.commit()
                return expired_count
                
        except Exception as e:
            print(f"Ошибка завершения истекших аренд: {e}")
            return 0
    
    def create_rental(self, account_id: int, user_id: str, duration_hours: int) -> bool:
        """Создание новой аренды"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Проверяем, доступен ли аккаунт
                cursor.execute('''
                    SELECT is_rented FROM steam_accounts WHERE id = ?
                ''', (account_id,))
                
                result = cursor.fetchone()
                if not result or result[0]:
                    return False
                
                start_time = datetime.now()
                end_time = start_time + datetime.timedelta(hours=duration_hours)
                
                # Обновляем статус аккаунта
                cursor.execute('''
                    UPDATE steam_accounts 
                    SET is_rented = TRUE, current_renter_id = ?, 
                        rental_start_time = ?, rental_end_time = ?
                    WHERE id = ?
                ''', (user_id, start_time, end_time, account_id))
                
                # Создаем запись об аренде
                cursor.execute('''
                    INSERT INTO rentals (account_id, renter_id, start_time, end_time, duration_hours, status)
                    VALUES (?, ?, ?, ?, ?, 'active')
                ''', (account_id, user_id, start_time, end_time, duration_hours))
                
                # Добавляем в историю операций
                cursor.execute('''
                    INSERT INTO operation_history (user_id, operation_type, description)
                    VALUES (?, ?, ?)
                ''', (user_id, 'rental_start', f'Начата аренда аккаунта #{account_id} на {duration_hours} часов'))
                
                conn.commit()
                return True
                
        except Exception as e:
            print(f"Ошибка создания аренды: {e}")
            return False
    
    def get_user_rentals(self, user_id: str) -> List[Dict]:
        """Получение аренд пользователя"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT r.id, r.account_id, sa.game_name, r.start_time, r.end_time, r.duration_hours, r.status
                    FROM rentals r
                    JOIN steam_accounts sa ON r.account_id = sa.id
                    WHERE r.renter_id = ?
                    ORDER BY r.start_time DESC
                ''', (user_id,))
                
                rentals = []
                for row in cursor.fetchall():
                    rentals.append({
                        'id': row[0],
                        'account_id': row[1],
                        'game_name': row[2],
                        'start_time': row[3],
                        'end_time': row[4],
                        'duration_hours': row[5],
                        'status': row[6]
                    })
                
                return rentals
                
        except Exception as e:
            print(f"Ошибка получения аренд пользователя: {e}")
            return []
    
    def add_bonus_time(self, user_id: str, bonus_minutes: int, reason: str) -> bool:
        """Добавление бонусного времени"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Добавляем бонус
                cursor.execute('''
                    INSERT INTO bonuses (user_id, bonus_minutes, reason)
                    VALUES (?, ?, ?)
                ''', (user_id, bonus_minutes, reason))
                
                # Находим активную аренду пользователя
                cursor.execute('''
                    SELECT r.id, r.end_time
                    FROM rentals r
                    WHERE r.renter_id = ? AND r.status = 'active'
                    ORDER BY r.end_time DESC
                    LIMIT 1
                ''', (user_id,))
                
                result = cursor.fetchone()
                if result:
                    rental_id, current_end_time = result
                    
                    # Увеличиваем время аренды
                    new_end_time = datetime.fromisoformat(current_end_time) + datetime.timedelta(minutes=bonus_minutes)
                    
                    cursor.execute('''
                        UPDATE rentals 
                        SET end_time = ?
                        WHERE id = ?
                    ''', (new_end_time, rental_id))
                    
                    # Обновляем время в аккаунте
                    cursor.execute('''
                        UPDATE steam_accounts 
                        SET rental_end_time = ?
                        WHERE current_renter_id = ?
                    ''', (new_end_time, user_id))
                
                conn.commit()
                return True
                
        except Exception as e:
            print(f"Ошибка добавления бонусного времени: {e}")
            return False
    
    def get_user_bonuses(self, user_id: str) -> List[Dict]:
        """Получение бонусов пользователя"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT bonus_minutes, reason, created_at, is_used
                    FROM bonuses
                    WHERE user_id = ?
                    ORDER BY created_at DESC
                ''', (user_id,))
                
                bonuses = []
                for row in cursor.fetchall():
                    bonuses.append({
                        'bonus_minutes': row[0],
                        'reason': row[1],
                        'created_at': row[2],
                        'is_used': row[3]
                    })
                
                return bonuses
                
        except Exception as e:
            print(f"Ошибка получения бонусов пользователя: {e}")
            return []
    
    def get_accounts_count_by_game(self, game_name: str) -> int:
        """Получение количества доступных аккаунтов для конкретной игры"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT COUNT(*) FROM steam_accounts 
                WHERE is_rented = FALSE AND game_name = ?
            ''', (game_name,))
            return cursor.fetchone()[0]
    
    def get_all_games(self) -> List[str]:
        """Получение списка всех игр"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT DISTINCT game_name FROM steam_accounts
            ''')
            return [row[0] for row in cursor.fetchall()]
    
    def add_user(self, telegram_id: str, username: str = None, first_name: str = None, last_name: str = None):
        """Добавление нового пользователя"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR IGNORE INTO users (telegram_id, username, first_name, last_name)
                VALUES (?, ?, ?, ?)
            ''', (telegram_id, username, first_name, last_name))
            conn.commit()
    
    # НОВЫЕ ПОЛЕЗНЫЕ ФУНКЦИИ
    
    def get_total_bonus_time(self, user_id: str) -> int:
        """Получение общего количества бонусного времени пользователя"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT SUM(bonus_minutes) FROM bonuses 
                WHERE user_id = ? AND is_used = FALSE
            ''', (user_id,))
            
            result = cursor.fetchone()
            return result[0] if result[0] else 0
    
    def add_notification(self, user_id: str, message: str, notification_type: str = "info"):
        """Добавление уведомления пользователю"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO notifications (user_id, message, type)
                VALUES (?, ?, ?)
            ''', (user_id, message, notification_type))
            conn.commit()
    
    def get_user_notifications(self, user_id: str, unread_only: bool = True) -> List[Dict]:
        """Получение уведомлений пользователя"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            if unread_only:
                cursor.execute('''
                    SELECT message, type, created_at FROM notifications 
                    WHERE user_id = ? AND is_read = FALSE
                    ORDER BY created_at DESC
                ''', (user_id,))
            else:
                cursor.execute('''
                    SELECT message, type, is_read, created_at FROM notifications 
                    WHERE user_id = ?
                    ORDER BY created_at DESC
                    LIMIT 50
                ''', (user_id,))
            
            columns = [description[0] for description in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    def mark_notification_read(self, notification_id: int):
        """Отметить уведомление как прочитанное"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE notifications SET is_read = TRUE WHERE id = ?
            ''', (notification_id,))
            conn.commit()
    
    def get_operation_history(self, user_id: str, limit: int = 20) -> List[Dict]:
        """Получение истории операций пользователя"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT operation_type, description, created_at
                FROM operation_history 
                WHERE user_id = ?
                ORDER BY created_at DESC
                LIMIT ?
            ''', (user_id, limit))
            
            columns = [description[0] for description in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    def get_statistics(self) -> Dict:
        """Получение общей статистики системы"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Общее количество аккаунтов
            cursor.execute('SELECT COUNT(*) FROM steam_accounts')
            total_accounts = cursor.fetchone()[0]
            
            # Активных аренд
            cursor.execute('SELECT COUNT(*) FROM rentals WHERE status = "active"')
            active_rentals = cursor.fetchone()[0]
            
            # Общее количество пользователей
            cursor.execute('SELECT COUNT(*) FROM users')
            total_users = cursor.fetchone()[0]
            
            # Популярные игры
            cursor.execute('''
                SELECT game_name, COUNT(*) as count
                FROM steam_accounts 
                GROUP BY game_name 
                ORDER BY count DESC 
                LIMIT 5
            ''')
            popular_games = [{'game': row[0], 'count': row[1]} for row in cursor.fetchall()]
            
            return {
                'total_accounts': total_accounts,
                'active_rentals': active_rentals,
                'total_users': total_users,
                'popular_games': popular_games
            }
    
    def get_user_statistics(self, user_id: str) -> Dict:
        """Получение статистики конкретного пользователя"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Количество аренд
            cursor.execute('''
                SELECT COUNT(*) FROM rentals WHERE renter_id = ?
            ''', (user_id,))
            total_rentals = cursor.fetchone()[0]
            
            # Активные аренды
            cursor.execute('''
                SELECT COUNT(*) FROM rentals WHERE renter_id = ? AND status = "active"
            ''', (user_id,))
            active_rentals = cursor.fetchone()[0]
            
            # Общее бонусное время
            total_bonus = self.get_total_bonus_time(user_id)
            
            # Любимые игры
            cursor.execute('''
                SELECT sa.game_name, COUNT(*) as count
                FROM rentals r
                JOIN steam_accounts sa ON r.account_id = sa.id
                WHERE r.renter_id = ?
                GROUP BY sa.game_name
                ORDER BY count DESC
                LIMIT 3
            ''', (user_id,))
            favorite_games = [{'game': row[0], 'count': row[1]} for row in cursor.fetchall()]
            
            return {
                'total_rentals': total_rentals,
                'active_rentals': active_rentals,
                'total_bonus_minutes': total_bonus,
                'favorite_games': favorite_games
            }
    
    def search_accounts(self, query: str) -> List[Dict]:
        """Поиск аккаунтов по названию игры"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM steam_accounts 
                WHERE game_name LIKE ? AND is_rented = FALSE
            ''', (f'%{query}%',))
            
            columns = [description[0] for description in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    def get_recent_activity(self, limit: int = 10) -> List[Dict]:
        """Получение последней активности в системе"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT user_id, operation_type, description, created_at
                FROM operation_history 
                ORDER BY created_at DESC
                LIMIT ?
            ''', (limit,))
            
            columns = [description[0] for description in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]

    # Методы для Telegram бота
    def get_total_accounts(self) -> int:
        """Получение общего количества аккаунтов"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM steam_accounts')
            return cursor.fetchone()[0]
    
    def get_available_accounts(self) -> int:
        """Получение количества доступных аккаунтов"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM steam_accounts WHERE is_rented = FALSE')
            return cursor.fetchone()[0]
    
    def get_active_rentals(self) -> int:
        """Получение количества активных аренд"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM rentals WHERE status = "active"')
            return cursor.fetchone()[0]
    
    def get_available_accounts_list(self) -> List[Dict]:
        """Получение списка доступных аккаунтов"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, username, game_name, created_at
                FROM steam_accounts 
                WHERE is_rented = FALSE
                ORDER BY created_at DESC
            ''')
            
            columns = [description[0] for description in cursor.description]
            accounts = []
            for row in cursor.fetchall():
                account = dict(zip(columns, row))
                # Добавляем описание и цену (заглушки)
                account['description'] = f"Аккаунт для игры {account['game_name']}"
                account['price'] = 50  # Цена по умолчанию
                accounts.append(account)
            
            return accounts
    
    def get_user_rentals(self, user_id: str) -> List[Dict]:
        """Получение аренд пользователя"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT r.id, r.account_id, r.start_time, r.end_time, r.duration_hours, r.status,
                       sa.game_name
                FROM rentals r
                JOIN steam_accounts sa ON r.account_id = sa.id
                WHERE r.renter_id = ? AND r.status = "active"
                ORDER BY r.end_time DESC
            ''', (user_id,))
            
            columns = [description[0] for description in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    def get_total_users(self) -> int:
        """Получение общего количества пользователей"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM users')
            return cursor.fetchone()[0]
    
    def get_account(self, account_id: int) -> Optional[Dict]:
        """Получение аккаунта по ID"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT id, username, password, game_name, is_rented, created_at, price, description
                    FROM steam_accounts
                    WHERE id = ?
                ''', (account_id,))

                row = cursor.fetchone()
                if row:
                    columns = [description[0] for description in cursor.description]
                    account = dict(zip(columns, row))
                    # Устанавливаем значения по умолчанию, если поля отсутствуют
                    if 'price' not in account or account['price'] is None:
                        account['price'] = 50
                    if 'description' not in account or account['description'] is None:
                        account['description'] = f"Аккаунт для игры {account['game_name']}"
                    return account
                return None
                
        except Exception as e:
            print(f"Ошибка получения аккаунта: {e}")
            return None
    
    def get_detailed_stats(self) -> Dict:
        """Получение детальной статистики для админа"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Общая статистика аккаунтов
                cursor.execute('SELECT COUNT(*) FROM steam_accounts')
                total_accounts = cursor.fetchone()[0]
                
                cursor.execute('SELECT COUNT(*) FROM steam_accounts WHERE is_rented = FALSE')
                available_accounts = cursor.fetchone()[0]
                
                cursor.execute('SELECT COUNT(*) FROM steam_accounts WHERE is_rented = TRUE')
                rented_accounts = cursor.fetchone()[0]
                
                # Статистика аренд
                cursor.execute('SELECT COUNT(*) FROM rentals WHERE status = "active" AND end_time > datetime("now")')
                active_rentals = cursor.fetchone()[0]
                
                cursor.execute('SELECT COUNT(*) FROM rentals WHERE DATE(end_time) = DATE("now") AND status = "completed"')
                completed_today = cursor.fetchone()[0]
                
                # Общий доход (примерный расчет)
                cursor.execute('SELECT SUM(duration_hours * 50) FROM rentals WHERE status = "completed"')
                total_revenue = cursor.fetchone()[0] or 0
                
                # Статистика пользователей
                cursor.execute('SELECT COUNT(*) FROM users')
                total_users = cursor.fetchone()[0]
                
                cursor.execute('SELECT COUNT(DISTINCT renter_id) FROM rentals WHERE DATE(start_time) = DATE("now")')
                active_users_today = cursor.fetchone()[0]
                
                cursor.execute('SELECT COUNT(*) FROM users WHERE DATE(created_at) = DATE("now")')
                new_users_today = cursor.fetchone()[0]
                
                return {
                    'total_accounts': total_accounts,
                    'available_accounts': available_accounts,
                    'rented_accounts': rented_accounts,
                    'blocked_accounts': 0,  # Пока не реализовано
                    'active_rentals': active_rentals,
                    'completed_today': completed_today,
                    'total_revenue': total_revenue,
                    'total_users': total_users,
                    'active_users_today': active_users_today,
                    'new_users_today': new_users_today
                }
                
        except Exception as e:
            print(f"Ошибка получения детальной статистики: {e}")
            return {
                'total_accounts': 0,
                'available_accounts': 0,
                'rented_accounts': 0,
                'blocked_accounts': 0,
                'active_rentals': 0,
                'completed_today': 0,
                'total_revenue': 0,
                'total_users': 0,
                'active_users_today': 0,
                'new_users_today': 0
            }
    
    def get_users_list(self) -> List[Dict]:
        """Получение списка пользователей для админа"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT u.telegram_id, u.created_at, COUNT(r.id) as rentals_count
                    FROM users u
                    LEFT JOIN rentals r ON u.telegram_id = r.renter_id
                    GROUP BY u.telegram_id, u.created_at
                    ORDER BY u.created_at DESC
                ''')
                
                users = []
                for row in cursor.fetchall():
                    users.append({
                        'user_id': row[0],
                        'created_at': row[1],
                        'rentals_count': row[2]
                    })
                
                return users
                
        except Exception as e:
            print(f"Ошибка получения списка пользователей: {e}")
            return []
    
    def delete_account(self, account_id: int) -> bool:
        """Удаление аккаунта"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Проверяем, что аккаунт существует
                cursor.execute('SELECT id, is_rented FROM steam_accounts WHERE id = ?', (account_id,))
                account = cursor.fetchone()
                
                if not account:
                    return False
                
                # Проверяем, что аккаунт не в аренде
                if account[1]:  # is_rented = True
                    return False
                
                # Удаляем аккаунт
                cursor.execute('DELETE FROM steam_accounts WHERE id = ?', (account_id,))
                
                # Удаляем связанные записи (если есть)
                cursor.execute('DELETE FROM rentals WHERE account_id = ?', (account_id,))
                
                conn.commit()
                return True
                
        except Exception as e:
            print(f"Ошибка удаления аккаунта: {e}")
            return False
    
    def get_all_accounts(self) -> List[Dict]:
        """Получение всех аккаунтов для админа"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT id, username, game_name, is_rented, created_at, price, description
                    FROM steam_accounts
                    ORDER BY id DESC
                ''')
                
                accounts = []
                for row in cursor.fetchall():
                    accounts.append({
                        'id': row[0],
                        'username': row[1],
                        'game_name': row[2],
                        'is_rented': row[3],
                        'created_at': row[4],
                        'price': row[5] or 50,
                        'description': row[6] or ''
                    })
                
                return accounts
                
        except Exception as e:
            print(f"Ошибка получения всех аккаунтов: {e}")
            return []
    
    def add_account(self, username: str, password: str, game_name: str, price: float, description: str = "") -> bool:
        """Добавление нового аккаунта"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Проверяем, что аккаунт с таким логином не существует
                cursor.execute('SELECT id FROM steam_accounts WHERE username = ?', (username,))
                if cursor.fetchone():
                    return False
                
                # Добавляем аккаунт
                cursor.execute('''
                    INSERT INTO steam_accounts (username, password, game_name, price, description)
                    VALUES (?, ?, ?, ?, ?)
                ''', (username, password, game_name, price, description))
                
                conn.commit()
                return True
                
        except Exception as e:
            print(f"Ошибка добавления аккаунта: {e}")
            return False
    
    def save_token(self, token_type: str, token_value: str) -> bool:
        """Сохранение токена в базу данных"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Создаем таблицу токенов, если её нет
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS api_tokens (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        token_type TEXT UNIQUE NOT NULL,
                        token_value TEXT NOT NULL,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Обновляем или вставляем токен
                cursor.execute('''
                    INSERT OR REPLACE INTO api_tokens (token_type, token_value, updated_at)
                    VALUES (?, ?, datetime('now'))
                ''', (token_type, token_value))
                
                conn.commit()
                return True
                
        except Exception as e:
            print(f"Ошибка сохранения токена: {e}")
            return False
    
    def get_token(self, token_type: str) -> Optional[str]:
        """Получение токена из базы данных"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Создаем таблицу токенов, если её нет
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS api_tokens (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        token_type TEXT UNIQUE NOT NULL,
                        token_value TEXT NOT NULL,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                cursor.execute('SELECT token_value FROM api_tokens WHERE token_type = ?', (token_type,))
                result = cursor.fetchone()
                
                return result[0] if result else None
                
        except Exception as e:
            print(f"Ошибка получения токена: {e}")
            return None
    
    def delete_token(self, token_type: str) -> bool:
        """Удаление токена из базы данных"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM api_tokens WHERE token_type = ?', (token_type,))
                conn.commit()
                return True
                
        except Exception as e:
            print(f"Ошибка удаления токена: {e}")
            return False
    
    def get_all_tokens(self) -> Dict[str, str]:
        """Получение всех токенов"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Создаем таблицу токенов, если её нет
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS api_tokens (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        token_type TEXT UNIQUE NOT NULL,
                        token_value TEXT NOT NULL,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                cursor.execute('SELECT token_type, token_value FROM api_tokens')
                tokens = {}
                
                for row in cursor.fetchall():
                    tokens[row[0]] = row[1]
                
                return tokens
                
        except Exception as e:
            print(f"Ошибка получения всех токенов: {e}")
            return {}
