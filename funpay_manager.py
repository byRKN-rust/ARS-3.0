import time
import random
import requests
from bs4 import BeautifulSoup
from config import Config
import logging

class FunPayManager:
    def __init__(self):
        self.base_url = Config.FUNPAY_BASE_URL
        self.login = Config.FUNPAY_LOGIN
        self.password = Config.FUNPAY_PASSWORD
        self.session = requests.Session()
        self.is_logged_in = False
    
        # Настройка логирования
        self.logger = logging.getLogger(__name__)
        
        # Настройка сессии
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
    
    def login_to_funpay(self):
        """Вход в аккаунт FunPay через API"""
        try:
            self.logger.info("🔐 Попытка входа в FunPay...")
            
            # Получаем страницу входа для получения CSRF токена
            login_page = self.session.get(f"{self.base_url}/account/login")
            soup = BeautifulSoup(login_page.content, 'html.parser')
            
            # Ищем CSRF токен
            csrf_token = None
            csrf_input = soup.find('input', {'name': '_token'})
            if csrf_input:
                csrf_token = csrf_input.get('value')
            
            if not csrf_token:
                self.logger.warning("⚠️ CSRF токен не найден, продолжаем без него")
            
            # Данные для входа
            login_data = {
                'login': self.login,
                'password': self.password,
            }
            
            if csrf_token:
                login_data['_token'] = csrf_token
            
            # Выполняем вход
            response = self.session.post(
                f"{self.base_url}/account/login",
                data=login_data,
                allow_redirects=True
            )
            
            # Проверяем успешность входа
            if response.status_code == 200:
                # Проверяем, что мы на странице аккаунта
                if 'account' in response.url or 'profile' in response.url:
                    self.is_logged_in = True
                    self.logger.info("✅ Успешный вход в FunPay")
                    return True
                else:
                    # Проверяем наличие элементов, указывающих на успешный вход
                    soup = BeautifulSoup(response.content, 'html.parser')
                    if soup.find('a', {'href': '/account/logout'}) or soup.find('div', {'class': 'user-menu'}):
                        self.is_logged_in = True
                        self.logger.info("✅ Успешный вход в FunPay (по элементам страницы)")
            return True
            
            self.logger.error("❌ Не удалось войти в FunPay")
            return False
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка при входе в FunPay: {e}")
            return False
    
    def get_orders(self):
        """Получение списка заказов"""
        try:
            if not self.is_logged_in:
                if not self.login_to_funpay():
                    return []
            
            self.logger.info("📋 Получение списка заказов...")
            
            response = self.session.get(f"{self.base_url}/account/orders")
            if response.status_code != 200:
                self.logger.error(f"❌ Ошибка получения заказов: {response.status_code}")
                return []
            
            soup = BeautifulSoup(response.content, 'html.parser')
            orders = []
            
            # Парсим заказы
            order_elements = soup.find_all('div', {'class': 'order-item'})
            
            for order_elem in order_elements:
                try:
                    order = {
                        'id': order_elem.get('data-order-id', ''),
                        'title': order_elem.find('div', {'class': 'order-title'}).text.strip(),
                        'status': order_elem.find('div', {'class': 'order-status'}).text.strip(),
                        'price': order_elem.find('div', {'class': 'order-price'}).text.strip(),
                        'date': order_elem.find('div', {'class': 'order-date'}).text.strip()
                    }
                    orders.append(order)
                except Exception as e:
                    self.logger.warning(f"⚠️ Ошибка парсинга заказа: {e}")
                    continue
            
            self.logger.info(f"✅ Получено {len(orders)} заказов")
            return orders
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка получения заказов: {e}")
            return []
    
    def get_reviews(self):
        """Получение списка отзывов"""
        try:
            if not self.is_logged_in:
                if not self.login_to_funpay():
                    return []
            
            self.logger.info("⭐ Получение списка отзывов...")
            
            response = self.session.get(f"{self.base_url}/account/reviews")
            if response.status_code != 200:
                self.logger.error(f"❌ Ошибка получения отзывов: {response.status_code}")
                return []
            
            soup = BeautifulSoup(response.content, 'html.parser')
            reviews = []
            
            # Парсим отзывы
            review_elements = soup.find_all('div', {'class': 'review-item'})
            
            for review_elem in review_elements:
                try:
                    review = {
                        'id': review_elem.get('data-review-id', ''),
                        'order_id': review_elem.get('data-order-id', ''),
                        'rating': int(review_elem.find('div', {'class': 'rating'}).get('data-rating', 0)),
                        'comment': review_elem.find('div', {'class': 'comment'}).text.strip(),
                        'date': review_elem.find('div', {'class': 'review-date'}).text.strip()
                    }
                    reviews.append(review)
                except Exception as e:
                    self.logger.warning(f"⚠️ Ошибка парсинга отзыва: {e}")
                    continue
            
            self.logger.info(f"✅ Получено {len(reviews)} отзывов")
            return reviews
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка получения отзывов: {e}")
            return []
    
    def send_message(self, order_id: str, message: str) -> bool:
        """Отправка сообщения в чат заказа"""
        try:
            if not self.is_logged_in:
                if not self.login_to_funpay():
                    return False
            
            self.logger.info(f"📤 Отправка сообщения для заказа {order_id}")
            
            # Получаем страницу чата заказа
            response = self.session.get(f"{self.base_url}/account/orders/{order_id}/chat")
            if response.status_code != 200:
                self.logger.error(f"❌ Ошибка получения чата: {response.status_code}")
                return False
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Ищем форму отправки сообщения
            form = soup.find('form', {'action': lambda x: x and 'send' in x})
            if not form:
                self.logger.error("❌ Форма отправки сообщения не найдена")
                return False
            
            # Получаем CSRF токен
            csrf_token = None
            csrf_input = form.find('input', {'name': '_token'})
            if csrf_input:
                csrf_token = csrf_input.get('value')
            
            # Данные для отправки
            send_data = {
                'message': message,
                'order_id': order_id
            }
            
            if csrf_token:
                send_data['_token'] = csrf_token
            
            # Отправляем сообщение
            response = self.session.post(
                form.get('action'),
                data=send_data,
                allow_redirects=True
            )
            
            if response.status_code == 200:
                self.logger.info(f"✅ Сообщение отправлено для заказа {order_id}")
                return True
            else:
                self.logger.error(f"❌ Ошибка отправки сообщения: {response.status_code}")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Ошибка отправки сообщения: {e}")
            return False
    
    def update_listing(self, listing_id: str, data: dict) -> bool:
        """Обновление объявления на FunPay"""
        try:
            if not self.is_logged_in:
                if not self.login_to_funpay():
                    return False
            
            self.logger.info(f"📝 Обновление объявления {listing_id}")
            
            # Получаем страницу редактирования объявления
            response = self.session.get(f"{self.base_url}/account/listings/{listing_id}/edit")
            if response.status_code != 200:
                self.logger.error(f"❌ Ошибка получения страницы редактирования: {response.status_code}")
                return False
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Ищем форму редактирования
            form = soup.find('form', {'action': lambda x: x and 'update' in x})
            if not form:
                self.logger.error("❌ Форма редактирования не найдена")
                return False
            
            # Получаем CSRF токен
            csrf_token = None
            csrf_input = form.find('input', {'name': '_token'})
            if csrf_input:
                csrf_token = csrf_input.get('value')
            
            # Подготавливаем данные для обновления
            update_data = data.copy()
            if csrf_token:
                update_data['_token'] = csrf_token
            
            # Отправляем обновление
            response = self.session.post(
                form.get('action'),
                data=update_data,
                allow_redirects=True
            )
            
            if response.status_code == 200:
                self.logger.info(f"✅ Объявление {listing_id} обновлено")
                return True
            else:
                self.logger.error(f"❌ Ошибка обновления объявления: {response.status_code}")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Ошибка обновления объявления: {e}")
            return False
    
    def delete_listing(self, listing_id: str):
        """Удаление объявления"""
        try:
            if not self.is_logged_in:
                if not self.login_to_funpay():
                    return False
            
            self.logger.info(f"🗑️ Удаление объявления {listing_id}")
            
            # Получаем страницу удаления
            response = self.session.get(f"{self.base_url}/account/sells/delete/{listing_id}")
            if response.status_code != 200:
                self.logger.error(f"❌ Ошибка получения страницы удаления: {response.status_code}")
                return False
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Ищем CSRF токен
            csrf_token = None
            csrf_input = soup.find('input', {'name': '_token'})
            if csrf_input:
                csrf_token = csrf_input.get('value')
            
            # Данные для удаления
            delete_data = {}
            if csrf_token:
                delete_data['_token'] = csrf_token
            
            # Удаляем объявление
            response = self.session.post(
                f"{self.base_url}/account/sells/delete/{listing_id}",
                data=delete_data,
                allow_redirects=True
            )
            
            if response.status_code == 200:
                self.logger.info("✅ Объявление успешно удалено")
                return True
            else:
                self.logger.error(f"❌ Ошибка удаления объявления: {response.status_code}")
                return False
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка удаления объявления: {e}")
            return False
    
    def sync_with_funpay(self):
        """Синхронизация с FunPay"""
        try:
            self.logger.info("🔄 Синхронизация с FunPay...")
            
            # Получаем заказы
            orders = self.get_orders()
            
            # Получаем отзывы
            reviews = self.get_reviews()
            
            self.logger.info(f"✅ Синхронизация завершена. Заказов: {len(orders)}, отзывов: {len(reviews)}")
            
            return {
                'orders': orders,
                'reviews': reviews,
                'success': True
            }
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка синхронизации с FunPay: {e}")
            return {
                'orders': [],
                'reviews': [],
                'success': False,
                'error': str(e)
            }
    
    def close(self):
        """Закрытие сессии"""
        try:
            self.session.close()
            self.logger.info("🔒 Сессия FunPay закрыта")
        except Exception as e:
            self.logger.error(f"❌ Ошибка закрытия сессии: {e}")

    def check_new_orders(self):
        """Проверка новых заказов"""
        try:
            if not self.is_logged_in:
                if not self.login_to_funpay():
                    return []
            self.logger.info("🆕 Проверка новых заказов...")
            orders = self.get_orders()
            new_orders = []
            for order in orders:
                if order.get('status', '').lower() in ['new', 'pending', 'новый', 'в обработке']:
                    game_name = self.extract_game_from_order(order)
                    if game_name:
                        order['game_name'] = game_name
                        new_orders.append(order)
            self.logger.info(f"✅ Найдено {len(new_orders)} новых заказов")
            return new_orders
        except Exception as e:
            self.logger.error(f"❌ Ошибка проверки новых заказов: {e}")
            return []
    
    def extract_game_from_order(self, order: dict) -> str:
        """Извлечение названия игры из заказа"""
        try:
            title = order.get('title', '').lower()
            game_mapping = {
                'cs2': 'Counter-Strike 2', 'cs:go': 'Counter-Strike 2', 'counter-strike': 'Counter-Strike 2',
                'dota': 'Dota 2', 'dota 2': 'Dota 2', 'pubg': 'PUBG', 'playerunknown': 'PUBG',
                'valorant': 'Valorant', 'lol': 'League of Legends', 'league of legends': 'League of Legends',
                'fortnite': 'Fortnite', 'minecraft': 'Minecraft', 'gta': 'GTA V', 'grand theft auto': 'GTA V',
                'fifa': 'FIFA 24', 'cod': 'Call of Duty', 'call of duty': 'Call of Duty',
                'overwatch': 'Overwatch', 'apex': 'Apex Legends', 'apex legends': 'Apex Legends'
            }
            for keyword, game_name in game_mapping.items():
                if keyword in title:
                    self.logger.info(f"🎮 Определена игра: {game_name} из заказа '{order.get('title', '')}'")
                    return game_name
            self.logger.warning(f"⚠️ Не удалось определить игру из заказа: {order.get('title', '')}")
            return 'Unknown Game'
        except Exception as e:
            self.logger.error(f"❌ Ошибка извлечения игры из заказа: {e}")
            return 'Unknown Game'
    
    def process_order(self, order_id: str, account_data: dict) -> bool:
        """Обработка заказа - отправка данных аккаунта"""
        try:
            self.logger.info(f"📤 Отправка данных аккаунта для заказа {order_id}")
            response = self.session.get(f"{self.base_url}/account/orders/{order_id}")
            if response.status_code != 200:
                self.logger.error(f"❌ Ошибка получения страницы заказа: {response.status_code}")
                return False
            soup = BeautifulSoup(response.content, 'html.parser')
            form = soup.find('form', {'action': lambda x: x and 'send' in x})
            if not form:
                self.logger.error("❌ Форма отправки данных не найдена")
                return False
            csrf_token = None
            csrf_input = form.find('input', {'name': '_token'})
            if csrf_input:
                csrf_token = csrf_input.get('value')
            message = f"""
🎮 Данные аккаунта для игры {account_data['game_name']}

👤 Логин: {account_data['username']}
🔑 Пароль: {account_data['password']}
⏰ Время аренды: {account_data['duration']} часов
🕐 Начало: {account_data['start_time']}

📋 Инструкции:
1. Войдите в Steam
2. Введите логин и пароль
3. При запросе Steam Guard код будет отправлен отдельно
4. Не меняйте пароль от аккаунта
5. Используйте аккаунт только для игр

⭐ Оставьте отзыв 5 звезд для получения +30 минут бонусного времени!

🆘 При проблемах обращайтесь в поддержку.
            """.strip()
            send_data = {
                'message': message,
                'order_id': order_id
            }
            if csrf_token:
                send_data['_token'] = csrf_token
            response = self.session.post(
                form.get('action'),
                data=send_data,
                allow_redirects=True
            )
            if response.status_code == 200:
                self.logger.info(f"✅ Данные аккаунта отправлены для заказа {order_id}")
                return True
            else:
                self.logger.error(f"❌ Ошибка отправки данных: {response.status_code}")
                return False
        except Exception as e:
            self.logger.error(f"❌ Ошибка обработки заказа {order_id}: {e}")
            return False
    
    def check_reviews(self):
        """Проверка новых отзывов"""
        try:
            if not self.is_logged_in:
                if not self.login_to_funpay():
                    return []
            self.logger.info("⭐ Проверка новых отзывов...")
            reviews = self.get_reviews()
            new_reviews = []
            for review in reviews:
                # Проверяем, что отзыв новый (за последние 24 часа)
                # Здесь можно добавить логику проверки даты
                new_reviews.append(review)
            self.logger.info(f"✅ Найдено {len(new_reviews)} новых отзывов")
            return new_reviews
        except Exception as e:
            self.logger.error(f"❌ Ошибка проверки отзывов: {e}")
            return []
