import requests
import random
import string
import time
from typing import Optional
from config import Config

class SteamManager:
    def __init__(self):
        self.api_key = Config.STEAM_API_KEY
        self.session = requests.Session()
    
    def generate_password(self, length: int = 12) -> str:
        """Генерация случайного пароля"""
        characters = string.ascii_letters + string.digits + "!@#$%^&*"
        return ''.join(random.choice(characters) for _ in range(length))
    
    def change_steam_password(self, username: str, old_password: str, new_password: str) -> bool:
        """
        Изменение пароля Steam аккаунта
        Примечание: Это упрощенная версия. В реальности потребуется более сложная логика
        """
        try:
            # Здесь должна быть реальная логика изменения пароля через Steam API
            # или через веб-интерфейс Steam
            
            # Для демонстрации просто возвращаем True
            # В реальном проекте здесь будет код для:
            # 1. Авторизации в Steam
            # 2. Перехода на страницу изменения пароля
            # 3. Ввода старого и нового пароля
            # 4. Подтверждения изменения
            
            print(f"Пароль для аккаунта {username} изменен на: {new_password}")
            return True
            
        except Exception as e:
            print(f"Ошибка при изменении пароля для {username}: {e}")
            return False
    
    def verify_steam_account(self, username: str, password: str) -> bool:
        """
        Проверка валидности Steam аккаунта
        """
        try:
            # Здесь должна быть реальная проверка через Steam API
            # Для демонстрации возвращаем True
            
            # В реальном проекте здесь будет код для:
            # 1. Попытки авторизации в Steam
            # 2. Проверки успешности входа
            # 3. Проверки наличия игр в библиотеке
            
            return True
            
        except Exception as e:
            print(f"Ошибка при проверке аккаунта {username}: {e}")
            return False
    
    def get_steam_profile_info(self, username: str) -> Optional[dict]:
        """
        Получение информации о профиле Steam
        """
        try:
            # Используем Steam Web API для получения информации о профиле
            if not self.api_key:
                print("Steam API ключ не настроен")
                return None
            
            # Поиск пользователя по имени
            search_url = f"http://api.steampowered.com/ISteamUser/ResolveVanityURL/v1/"
            params = {
                'key': self.api_key,
                'vanityurl': username
            }
            
            response = self.session.get(search_url, params=params)
            if response.status_code == 200:
                data = response.json()
                if data['response']['success'] == 1:
                    steam_id = data['response']['steamid']
                    
                    # Получение информации о профиле
                    profile_url = f"http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v2/"
                    profile_params = {
                        'key': self.api_key,
                        'steamids': steam_id
                    }
                    
                    profile_response = self.session.get(profile_url, params=profile_params)
                    if profile_response.status_code == 200:
                        profile_data = profile_response.json()
                        player = profile_data['response']['players'][0]
                        
                        return {
                            'steam_id': steam_id,
                            'username': player['personaname'],
                            'avatar': player['avatarfull'],
                            'profile_url': player['profileurl'],
                            'status': player['personastate'],
                            'last_online': player.get('lastlogoff', 0)
                        }
            
            return None
            
        except Exception as e:
            print(f"Ошибка при получении информации о профиле {username}: {e}")
            return None
    
    def check_steam_guard_status(self, username: str) -> bool:
        """
        Проверка статуса Steam Guard для аккаунта
        """
        try:
            # Здесь должна быть реальная проверка Steam Guard
            # Для демонстрации возвращаем True
            
            # В реальном проекте здесь будет код для:
            # 1. Проверки настроек Steam Guard
            # 2. Определения типа защиты (email, mobile app)
            # 3. Получения статуса активации
            
            return True
            
        except Exception as e:
            print(f"Ошибка при проверке Steam Guard для {username}: {e}")
            return False
    
    def get_steam_guard_code(self, username: str) -> Optional[str]:
        """
        Получение кода Steam Guard для аккаунта
        """
        try:
            # Здесь должна быть реальная логика получения кода
            # Для демонстрации генерируем случайный код
            
            # В реальном проекте здесь будет код для:
            # 1. Проверки типа Steam Guard (email/mobile)
            # 2. Отправки запроса на получение кода
            # 3. Ожидания и получения кода
            
            # Генерируем случайный 5-значный код
            code = ''.join(random.choice(string.digits) for _ in range(5))
            print(f"Steam Guard код для {username}: {code}")
            return code
            
        except Exception as e:
            print(f"Ошибка при получении Steam Guard кода для {username}: {e}")
            return None
    
    def check_account_balance(self, username: str) -> float:
        """
        Проверка баланса Steam аккаунта
        """
        try:
            # Здесь должна быть реальная проверка баланса
            # Для демонстрации возвращаем случайную сумму
            
            # В реальном проекте здесь будет код для:
            # 1. Авторизации в аккаунте
            # 2. Перехода на страницу кошелька
            # 3. Парсинга баланса
            
            balance = random.uniform(0.0, 100.0)
            print(f"Баланс аккаунта {username}: {balance:.2f} руб")
            return balance
            
        except Exception as e:
            print(f"Ошибка при проверке баланса {username}: {e}")
            return 0.0
    
    def get_account_games(self, username: str) -> list:
        """
        Получение списка игр в аккаунте
        """
        try:
            # Здесь должна быть реальная проверка игр
            # Для демонстрации возвращаем список популярных игр
            
            # В реальном проекте здесь будет код для:
            # 1. Получения Steam ID пользователя
            # 2. Запроса к Steam API для получения игр
            # 3. Парсинга и форматирования списка
            
            popular_games = [
                "Counter-Strike 2",
                "Dota 2", 
                "PUBG",
                "Valorant",
                "League of Legends",
                "Fortnite",
                "Minecraft",
                "GTA V",
                "FIFA 24",
                "Call of Duty"
            ]
            
            # Возвращаем случайные игры
            games = random.sample(popular_games, random.randint(3, 8))
            print(f"Игры в аккаунте {username}: {', '.join(games)}")
            return games
            
        except Exception as e:
            print(f"Ошибка при получении игр для {username}: {e}")
            return []
    
    def check_account_status(self, username: str) -> dict:
        """
        Полная проверка статуса аккаунта
        """
        try:
            status = {
                'username': username,
                'is_valid': self.verify_steam_account(username, ""),
                'steam_guard_enabled': self.check_steam_guard_status(username),
                'balance': self.check_account_balance(username),
                'games': self.get_account_games(username),
                'profile_info': self.get_steam_profile_info(username)
            }
            
            return status
            
        except Exception as e:
            print(f"Ошибка при проверке статуса аккаунта {username}: {e}")
            return {
                'username': username,
                'is_valid': False,
                'steam_guard_enabled': False,
                'balance': 0.0,
                'games': [],
                'profile_info': None
            }
    
    def check_game_ownership(self, username: str, game_id: int) -> bool:
        """
        Проверка наличия игры в библиотеке пользователя
        """
        try:
            # В реальном проекте здесь будет проверка через Steam API
            # Для демонстрации возвращаем True
            
            # В реальном проекте здесь будет код для:
            # 1. Получения списка игр пользователя
            # 2. Проверки наличия конкретной игры
            
            return True
            
        except Exception as e:
            print(f"Ошибка при проверке игр для {username}: {e}")
            return False
    
    def get_account_status(self, username: str) -> str:
        """
        Получение статуса аккаунта (онлайн/оффлайн/заблокирован)
        """
        try:
            profile_info = self.get_steam_profile_info(username)
            if profile_info:
                status_map = {
                    0: "Оффлайн",
                    1: "Онлайн",
                    2: "Занят",
                    3: "Не беспокоить",
                    4: "Отошел",
                    5: "Ищет торговлю",
                    6: "Ищет игру"
                }
                return status_map.get(profile_info['status'], "Неизвестно")
            return "Недоступно"
            
        except Exception as e:
            print(f"Ошибка при получении статуса {username}: {e}")
            return "Ошибка"
    
    def is_account_banned(self, username: str) -> bool:
        """
        Проверка, заблокирован ли аккаунт
        """
        try:
            profile_info = self.get_steam_profile_info(username)
            if profile_info:
                # Проверяем различные признаки блокировки
                # В реальном проекте здесь будет более детальная проверка
                return False
            return True
            
        except Exception as e:
            print(f"Ошибка при проверке блокировки {username}: {e}")
            return True
    
    def backup_account_data(self, username: str, password: str, game_name: str) -> dict:
        """
        Создание резервной копии данных аккаунта
        """
        return {
            'username': username,
            'password': password,
            'game_name': game_name,
            'backup_time': time.time(),
            'status': 'active'
        }
    
    def restore_account_data(self, backup_data: dict) -> bool:
        """
        Восстановление данных аккаунта из резервной копии
        """
        try:
            # В реальном проекте здесь будет логика восстановления
            # Для демонстрации просто возвращаем True
            return True
            
        except Exception as e:
            print(f"Ошибка при восстановлении аккаунта: {e}")
            return False
