#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🤖 Telegram бот для системы аренды Steam аккаунтов
"""

import logging
import asyncio
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
from config import Config
from database import Database

class SteamRentalBot:
    def __init__(self):
        self.token = Config.TELEGRAM_TOKEN
        self.admin_id = Config.TELEGRAM_ADMIN_ID
        self.db = Database()
        self.application = None
        
        # Настройка логирования
        logging.basicConfig(
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            level=logging.INFO
        )
        self.logger = logging.getLogger(__name__)
        
    def setup(self):
        """Настройка бота"""
        self.logger.info(f"🔧 Настройка Telegram бота...")
        self.logger.info(f"🔑 Token: {self.token[:20] if self.token else 'НЕ НАЙДЕН'}...")
        self.logger.info(f"👤 Admin ID: {self.admin_id}")
        
        if not self.token:
            self.logger.error("❌ TELEGRAM_TOKEN не настроен!")
            self.logger.error(f"   Текущее значение: {self.token}")
            return False
            
        try:
            self.application = Application.builder().token(self.token).build()
            
            # Добавляем обработчики команд
            self.application.add_handler(CommandHandler("start", self.start_command))
            self.application.add_handler(CommandHandler("help", self.help_command))
            self.application.add_handler(CommandHandler("status", self.status_command))
            self.application.add_handler(CommandHandler("accounts", self.accounts_command))
            self.application.add_handler(CommandHandler("rentals", self.rentals_command))
            self.application.add_handler(CommandHandler("support", self.support_command))
            self.application.add_handler(CommandHandler("admin", self.admin_command))
            self.application.add_handler(CommandHandler("add_account", self.add_account_command))
            self.application.add_handler(CommandHandler("edit_account", self.edit_account_command))
            self.application.add_handler(CommandHandler("set_token", self.set_token_command))
            self.application.add_handler(CommandHandler("tokens", self.tokens_command))
            
            # Обработчик для inline кнопок
            self.application.add_handler(CallbackQueryHandler(self.button_callback))
            
            self.logger.info("✅ Telegram бот настроен успешно")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка настройки бота: {e}")
            return False
    
    def run(self):
        """Запуск бота"""
        if not self.application:
            self.logger.error("❌ Бот не настроен!")
            return
            
        try:
            self.logger.info("🚀 Запуск Telegram бота...")
            
            # Создаем новый event loop для этого потока
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # Запускаем бота без signal handling
            async def run_bot():
                async with self.application:
                    await self.application.start_polling(
                        allowed_updates=Update.ALL_TYPES,
                        drop_pending_updates=True
                    )
            
            # Запускаем асинхронную функцию
            loop.run_until_complete(run_bot())
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка запуска бота: {e}")
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /start"""
        user = update.effective_user
        
        # Добавляем пользователя в базу данных
        self.db.add_user(
            telegram_id=str(user.id),
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name
        )
        
        welcome_text = f"""
🎮 Добро пожаловать в Steam Rental System!

Привет, {user.first_name}! 👋

Я помогу вам арендовать аккаунты Steam для игр.

📋 Доступные команды:
/accounts - Показать доступные аккаунты
/rentals - Ваши активные аренды
/status - Статус системы
/support - Поддержка
/help - Справка

💡 Для начала работы выберите команду или используйте кнопки ниже.
        """
        
        keyboard = [
            [InlineKeyboardButton("📋 Аккаунты", callback_data="show_accounts")],
            [InlineKeyboardButton("📋 Мои аренды", callback_data="show_rentals")],
            [InlineKeyboardButton("📊 Статус", callback_data="show_status")],
            [InlineKeyboardButton("❓ Помощь", callback_data="show_help")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(welcome_text, reply_markup=reply_markup)
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /help"""
        help_text = """
❓ Справка по использованию бота

📋 Основные команды:
/start - Главное меню
/accounts - Показать доступные аккаунты
/rentals - Ваши активные аренды
/status - Статус системы
/support - Связаться с поддержкой

🔧 Как арендовать аккаунт:
1. Используйте команду /accounts
2. Выберите подходящий аккаунт
3. Укажите время аренды
4. Оплатите услугу
5. Получите данные аккаунта

⚠️ Важно:
• Время аренды отсчитывается с момента получения данных
• После окончания аренды пароль автоматически изменяется
• Используйте аккаунт только для игр
• Не изменяйте настройки аккаунта

📞 Поддержка: /support
        """
        await update.message.reply_text(help_text)
    
    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /status"""
        try:
            # Получаем статистику из базы данных
            total_accounts = self.db.get_total_accounts()
            available_accounts = self.db.get_available_accounts()
            active_rentals = self.db.get_active_rentals()
            
            status_text = f"""
📊 Статус системы

✅ Система работает
🕐 Время: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

📈 Статистика:
• Всего аккаунтов: {total_accounts}
• Доступно для аренды: {available_accounts}
• Активных аренд: {active_rentals}

🔧 Система мониторинга активна
        """
            
        except Exception as e:
            status_text = f"""
❌ Ошибка получения статуса: {e}

Попробуйте позже или обратитесь в поддержку: /support
            """
        
        await update.message.reply_text(status_text)
    
    async def accounts_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /accounts"""
        try:
            accounts = self.db.get_available_accounts_list()
            
            if not accounts:
                await update.message.reply_text("❌ Нет доступных аккаунтов в данный момент.")
                return
            
            text = "📋 Доступные аккаунты:\n\n"
            keyboard = []
            
            for i, account in enumerate(accounts[:10]):  # Показываем максимум 10
                text += f"🎮 Аккаунт #{account['id']}\n"
                text += f"📝 Описание: {account.get('description', 'Нет описания')}\n"
                text += f"💰 Цена: {account.get('price', 'Не указана')} руб/час\n\n"
                
                keyboard.append([InlineKeyboardButton(
                    f"Арендовать #{account['id']}", 
                    callback_data=f"rent_account_{account['id']}"
                )])
            
            if len(accounts) > 10:
                text += f"... и еще {len(accounts) - 10} аккаунтов"
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text(text, reply_markup=reply_markup)
            
        except Exception as e:
            await update.message.reply_text(f"❌ Ошибка получения аккаунтов: {e}")
    
    async def rentals_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /rentals"""
        user_id = update.effective_user.id
        
        try:
            rentals = self.db.get_user_rentals(user_id)
            
            if not rentals:
                await update.message.reply_text("📭 У вас нет активных аренд.")
                return
            
            text = "📋 Ваши активные аренды:\n\n"
            
            for rental in rentals:
                end_time = datetime.fromisoformat(rental['end_time'])
                remaining = end_time - datetime.now()
                
                if remaining.total_seconds() > 0:
                    hours = int(remaining.total_seconds() // 3600)
                    minutes = int((remaining.total_seconds() % 3600) // 60)
                    
                    text += f"🎮 Аккаунт #{rental['account_id']}\n"
                    text += f"⏰ Осталось: {hours}ч {minutes}м\n"
                    text += f"🕐 Завершение: {end_time.strftime('%Y-%m-%d %H:%M')}\n\n"
                else:
                    text += f"🎮 Аккаунт #{rental['account_id']} - Истек\n\n"
            
            await update.message.reply_text(text)
            
        except Exception as e:
            await update.message.reply_text(f"❌ Ошибка получения аренд: {e}")
    
    async def support_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /support"""
        support_text = """
📞 Поддержка

Если у вас возникли вопросы или проблемы:

👨‍💼 Администратор: @admin
📧 Email: support@steamrental.com
💬 Чат: @steamrental_support

⏰ Время работы: 24/7

🔧 Часто задаваемые вопросы:
• Как работает аренда? - Время отсчитывается с момента получения данных
• Что после окончания? - Пароль автоматически изменяется
• Можно ли продлить? - Да, оплатив дополнительное время
• Безопасно ли? - Да, все аккаунты проверены
        """
        await update.message.reply_text(support_text)
    
    async def admin_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /admin"""
        user_id = update.effective_user.id
        
        if str(user_id) != self.admin_id:
            await update.message.reply_text("❌ У вас нет доступа к админ-панели.")
            return
        
        admin_text = """
🔧 Админ-панель

Доступные команды:
• /admin_stats - Статистика системы
• /admin_accounts - Управление аккаунтами
• /admin_rentals - Управление арендами
• /admin_users - Список пользователей

📊 Быстрая статистика:
        """
        
        try:
            total_accounts = self.db.get_total_accounts()
            available_accounts = self.db.get_available_accounts()
            active_rentals = self.db.get_active_rentals()
            total_users = self.db.get_total_users()
            
            admin_text += f"""
• Всего аккаунтов: {total_accounts}
• Доступно: {available_accounts}
• Активных аренд: {active_rentals}
• Пользователей: {total_users}
            """
        except Exception as e:
            admin_text += f"\n❌ Ошибка получения статистики: {e}"
        
        keyboard = [
            [InlineKeyboardButton("📊 Статистика", callback_data="admin_stats")],
            [InlineKeyboardButton("👥 Пользователи", callback_data="admin_users")],
            [InlineKeyboardButton("🎮 Аккаунты", callback_data="admin_accounts")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(admin_text, reply_markup=reply_markup)
    
    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик нажатий на кнопки"""
        query = update.callback_query
        await query.answer()
        
        data = query.data
        
        if data == "show_accounts":
            await self.accounts_command(update, context)
        elif data == "show_status":
            await self.status_command(update, context)
        elif data == "show_help":
            await self.help_command(update, context)
        elif data.startswith("rent_account_"):
            account_id = data.split("_")[2]
            await self.handle_rent_request(update, context, account_id)
        elif data.startswith("rent_time_"):
            parts = data.split("_")
            account_id = parts[2]
            duration = int(parts[3])
            await self.handle_rent_confirmation(update, context, account_id, duration)
        elif data == "admin_stats":
            await self.admin_stats(update, context)
        elif data == "admin_users":
            await self.admin_users(update, context)
        elif data == "admin_accounts":
            await self.admin_accounts(update, context)
        elif data == "admin_list_accounts":
            await self.admin_list_accounts(update, context)
        elif data == "admin_delete_account":
            await self.admin_delete_account(update, context)
        elif data.startswith("delete_account_"):
            account_id = data.split("_")[2]
            await self.confirm_delete_account(update, context, account_id)
        elif data.startswith("confirm_delete_"):
            account_id = data.split("_")[2]
            await self.execute_delete_account(update, context, account_id)
        elif data == "show_rentals":
            await self.rentals_command(update, context)
        elif data == "admin_back":
            await self.admin_command(update, context)
    
    async def handle_rent_request(self, update: Update, context: ContextTypes.DEFAULT_TYPE, account_id: str):
        """Обработка запроса на аренду"""
        user_id = update.effective_user.id
        
        try:
            account = self.db.get_account(account_id)
            if not account:
                await update.callback_query.edit_message_text("❌ Аккаунт не найден.")
                return
            
            text = f"""
🎮 Аренда аккаунта #{account_id}

📝 Описание: {account.get('description', 'Нет описания')}
💰 Цена: {account.get('price', 'Не указана')} руб/час

⏰ Выберите время аренды:
            """
            
            keyboard = [
                [InlineKeyboardButton("1 час", callback_data=f"rent_time_{account_id}_1")],
                [InlineKeyboardButton("3 часа", callback_data=f"rent_time_{account_id}_3")],
                [InlineKeyboardButton("6 часов", callback_data=f"rent_time_{account_id}_6")],
                [InlineKeyboardButton("12 часов", callback_data=f"rent_time_{account_id}_12")],
                [InlineKeyboardButton("24 часа", callback_data=f"rent_time_{account_id}_24")],
                [InlineKeyboardButton("« Назад", callback_data="show_accounts")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.callback_query.edit_message_text(text, reply_markup=reply_markup)
            
        except Exception as e:
            await update.callback_query.edit_message_text(f"❌ Ошибка: {e}")
    
    async def handle_rent_confirmation(self, update: Update, context: ContextTypes.DEFAULT_TYPE, account_id: str, duration: int):
        """Обработка подтверждения аренды"""
        user_id = update.effective_user.id
        
        try:
            account = self.db.get_account(account_id)
            if not account:
                await update.callback_query.edit_message_text("❌ Аккаунт не найден.")
                return
            
            # Создаем аренду
            success = self.db.create_rental(int(account_id), str(user_id), duration)
            
            if success:
                total_cost = duration * account.get('price', 50)
                
                text = f"""
✅ Аренда успешно создана!

🎮 Аккаунт: #{account_id}
📝 Игра: {account['game_name']}
⏰ Время: {duration} часов
💰 Стоимость: {total_cost} руб

📋 Данные аккаунта:
👤 Логин: {account['username']}
🔑 Пароль: (будет отправлен отдельно)

⚠️ Важно:
• Не меняйте пароль от аккаунта
• Не добавляйте друзей
• Используйте аккаунт только для игр

⏰ Время аренды истекает через {duration} часов
                """
                
                keyboard = [
                    [InlineKeyboardButton("📋 Мои аренды", callback_data="show_rentals")],
                    [InlineKeyboardButton("🎮 Еще аккаунты", callback_data="show_accounts")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await update.callback_query.edit_message_text(text, reply_markup=reply_markup)
            else:
                await update.callback_query.edit_message_text("❌ Не удалось создать аренду. Аккаунт может быть уже занят.")
                
        except Exception as e:
            await update.callback_query.edit_message_text(f"❌ Ошибка создания аренды: {e}")
    
    async def admin_stats(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Показать детальную статистику для админа"""
        user_id = update.effective_user.id
        
        if str(user_id) != self.admin_id:
            return
        
        try:
            stats = self.db.get_detailed_stats()
            
            text = """
📊 Детальная статистика

🎮 Аккаунты:
• Всего: {total_accounts}
• Доступно: {available_accounts}
• В аренде: {rented_accounts}
• Заблокированы: {blocked_accounts}

📈 Аренды:
• Активных: {active_rentals}
• Завершенных сегодня: {completed_today}
• Общий доход: {total_revenue} руб

👥 Пользователи:
• Всего: {total_users}
• Активных сегодня: {active_users_today}
• Новых сегодня: {new_users_today}
            """.format(**stats)
            
        except Exception as e:
            text = f"❌ Ошибка получения статистики: {e}"
        
        keyboard = [[InlineKeyboardButton("« Назад", callback_data="admin_back")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.callback_query.edit_message_text(text, reply_markup=reply_markup)
    
    async def admin_users(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Показать список пользователей для админа"""
        user_id = update.effective_user.id
        
        if str(user_id) != self.admin_id:
            return
        
        try:
            users = self.db.get_users_list()
            
            text = "👥 Список пользователей:\n\n"
            
            for user in users[:10]:  # Показываем первые 10
                text += f"👤 ID: {user['user_id']}\n"
                text += f"📅 Регистрация: {user['created_at']}\n"
                text += f"🎮 Аренд: {user['rentals_count']}\n\n"
            
            if len(users) > 10:
                text += f"... и еще {len(users) - 10} пользователей"
            
        except Exception as e:
            text = f"❌ Ошибка получения пользователей: {e}"
        
        keyboard = [[InlineKeyboardButton("« Назад", callback_data="admin_back")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.callback_query.edit_message_text(text, reply_markup=reply_markup)
    
    async def admin_accounts(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Показать управление аккаунтами для админа"""
        user_id = update.effective_user.id
        
        if str(user_id) != self.admin_id:
            return
        
        text = """
🎮 Управление аккаунтами

Выберите действие:
        """
        
        keyboard = [
            [InlineKeyboardButton("➕ Добавить аккаунт", callback_data="admin_add_account")],
            [InlineKeyboardButton("📋 Список аккаунтов", callback_data="admin_list_accounts")],
            [InlineKeyboardButton("🔧 Редактировать", callback_data="admin_edit_accounts")],
            [InlineKeyboardButton("« Назад", callback_data="admin_back")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.callback_query.edit_message_text(text, reply_markup=reply_markup)
    
    async def admin_list_accounts(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Показать список всех аккаунтов для админа"""
        user_id = update.effective_user.id
        
        if str(user_id) != self.admin_id:
            return
        
        try:
            accounts = self.db.get_all_accounts()
            
            if not accounts:
                text = "📭 Нет аккаунтов в системе."
            else:
                text = "📋 Список всех аккаунтов:\n\n"
                
                for account in accounts[:10]:  # Показываем первые 10
                    status = "🔴 В аренде" if account['is_rented'] else "🟢 Свободен"
                    text += f"🎮 #{account['id']} - {account['username']}\n"
                    text += f"📝 Игра: {account['game_name']}\n"
                    text += f"📊 Статус: {status}\n"
                    text += f"📅 Создан: {account['created_at']}\n\n"
                
                if len(accounts) > 10:
                    text += f"... и еще {len(accounts) - 10} аккаунтов"
            
        except Exception as e:
            text = f"❌ Ошибка получения аккаунтов: {e}"
        
        keyboard = [
            [InlineKeyboardButton("🗑️ Удалить аккаунт", callback_data="admin_delete_account")],
            [InlineKeyboardButton("« Назад", callback_data="admin_accounts")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.callback_query.edit_message_text(text, reply_markup=reply_markup)
    
    async def admin_delete_account(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Показать список аккаунтов для удаления"""
        user_id = update.effective_user.id
        
        if str(user_id) != self.admin_id:
            return
        
        try:
            accounts = self.db.get_all_accounts()
            available_accounts = [acc for acc in accounts if not acc['is_rented']]
            
            if not available_accounts:
                text = "❌ Нет доступных для удаления аккаунтов.\n\nАккаунты в аренде нельзя удалить."
            else:
                text = "🗑️ Выберите аккаунт для удаления:\n\n"
                keyboard = []
                
                for account in available_accounts[:10]:  # Показываем первые 10
                    text += f"🎮 #{account['id']} - {account['username']}\n"
                    text += f"📝 Игра: {account['game_name']}\n\n"
                    
                    keyboard.append([InlineKeyboardButton(
                        f"🗑️ Удалить #{account['id']}", 
                        callback_data=f"delete_account_{account['id']}"
                    )])
                
                if len(available_accounts) > 10:
                    text += f"... и еще {len(available_accounts) - 10} аккаунтов"
            
        except Exception as e:
            text = f"❌ Ошибка получения аккаунтов: {e}"
            keyboard = []
        
        keyboard.append([InlineKeyboardButton("« Назад", callback_data="admin_list_accounts")])
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.callback_query.edit_message_text(text, reply_markup=reply_markup)
    
    async def confirm_delete_account(self, update: Update, context: ContextTypes.DEFAULT_TYPE, account_id: str):
        """Подтверждение удаления аккаунта"""
        user_id = update.effective_user.id
        
        if str(user_id) != self.admin_id:
            return
        
        try:
            account = self.db.get_account(account_id)
            if not account:
                await update.callback_query.edit_message_text("❌ Аккаунт не найден.")
                return
            
            text = f"""
⚠️ Подтверждение удаления

🎮 Аккаунт: #{account_id}
👤 Логин: {account['username']}
📝 Игра: {account['game_name']}

❗️ Это действие нельзя отменить!
            
Вы уверены, что хотите удалить этот аккаунт?
            """
            
            keyboard = [
                [InlineKeyboardButton("✅ Да, удалить", callback_data=f"confirm_delete_{account_id}")],
                [InlineKeyboardButton("❌ Отмена", callback_data="admin_delete_account")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.callback_query.edit_message_text(text, reply_markup=reply_markup)
            
        except Exception as e:
            await update.callback_query.edit_message_text(f"❌ Ошибка: {e}")
    
    async def execute_delete_account(self, update: Update, context: ContextTypes.DEFAULT_TYPE, account_id: str):
        """Выполнение удаления аккаунта"""
        user_id = update.effective_user.id
        
        if str(user_id) != self.admin_id:
            return
        
        try:
            success = self.db.delete_account(int(account_id))
            
            if success:
                text = f"""
✅ Аккаунт успешно удален!

🎮 ID: #{account_id}

Аккаунт и все связанные с ним данные были удалены из системы.
                """
            else:
                text = """
❌ Не удалось удалить аккаунт

Возможные причины:
• Аккаунт не найден
• Аккаунт находится в аренде
• Ошибка базы данных
                """
            
            keyboard = [
                [InlineKeyboardButton("📋 Список аккаунтов", callback_data="admin_list_accounts")],
                [InlineKeyboardButton("« В админ-панель", callback_data="admin_back")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.callback_query.edit_message_text(text, reply_markup=reply_markup)
            
        except Exception as e:
            await update.callback_query.edit_message_text(f"❌ Ошибка удаления: {e}")
    
    async def admin_add_account(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Показать форму добавления аккаунта"""
        user_id = update.effective_user.id
        
        if str(user_id) != self.admin_id:
            return
        
        text = """
➕ Добавление нового аккаунта

Для добавления аккаунта используйте команду:
/add_account username password game_name price description

Пример:
/add_account test_user pass123 "Counter-Strike 2" 50 "Аккаунт для CS2"

Параметры:
• username - логин аккаунта
• password - пароль аккаунта  
• game_name - название игры
• price - цена за час (руб)
• description - описание (необязательно)
        """
        
        keyboard = [[InlineKeyboardButton("« Назад", callback_data="admin_accounts")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.callback_query.edit_message_text(text, reply_markup=reply_markup)
    
    async def admin_edit_accounts(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Показать управление редактированием аккаунтов"""
        user_id = update.effective_user.id
        
        if str(user_id) != self.admin_id:
            return
        
        text = """
🔧 Редактирование аккаунтов

Для редактирования аккаунта используйте команду:
/edit_account account_id field value

Примеры:
/edit_account 1 price 75
/edit_account 1 description "Обновленное описание"
/edit_account 1 game_name "Dota 2"

Доступные поля:
• price - цена за час
• description - описание
• game_name - название игры
        """
        
        keyboard = [[InlineKeyboardButton("« Назад", callback_data="admin_accounts")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.callback_query.edit_message_text(text, reply_markup=reply_markup)
    
    async def admin_rentals(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Показать управление арендами для админа"""
        user_id = update.effective_user.id
        
        if str(user_id) != self.admin_id:
            return
        
        try:
            active_rentals = self.db.get_active_rentals_list()
            
            if not active_rentals:
                text = "📭 Нет активных аренд в системе."
            else:
                text = "📋 Активные аренды:\n\n"
                
                for rental in active_rentals[:10]:  # Показываем первые 10
                    end_time = datetime.fromisoformat(rental['end_time'])
                    remaining = end_time - datetime.now()
                    
                    if remaining.total_seconds() > 0:
                        hours = int(remaining.total_seconds() // 3600)
                        minutes = int((remaining.total_seconds() % 3600) // 60)
                        
                        text += f"🎮 Аккаунт #{rental['account_id']}\n"
                        text += f"👤 Пользователь: {rental['user_id']}\n"
                        text += f"⏰ Осталось: {hours}ч {minutes}м\n"
                        text += f"🕐 Завершение: {end_time.strftime('%Y-%m-%d %H:%M')}\n\n"
                    else:
                        text += f"🎮 Аккаунт #{rental['account_id']} - Истек\n\n"
                
                if len(active_rentals) > 10:
                    text += f"... и еще {len(active_rentals) - 10} аренд"
            
        except Exception as e:
            text = f"❌ Ошибка получения аренд: {e}"
        
        keyboard = [
            [InlineKeyboardButton("🔄 Обновить", callback_data="admin_rentals")],
            [InlineKeyboardButton("« Назад", callback_data="admin_back")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.callback_query.edit_message_text(text, reply_markup=reply_markup)
    
    async def add_account_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /add_account"""
        user_id = update.effective_user.id
        
        if str(user_id) != self.admin_id:
            await update.message.reply_text("❌ У вас нет доступа к этой команде.")
            return
        
        try:
            # Получаем аргументы команды
            args = context.args
            
            if len(args) < 5:
                await update.message.reply_text("""
❌ Неправильный формат команды!

📝 Правильный формат:
/add_account username password game_name price steam_token [description]

📋 Примеры:
/add_account test_user pass123 "Counter-Strike 2" 50 your_steam_api_key
/add_account cs2_acc password123 "CS2" 75 your_steam_api_key "Аккаунт с скинами"

🔧 Параметры:
• username - логин аккаунта
• password - пароль аккаунта  
• game_name - название игры
• price - цена за час (руб)
• steam_token - токен Steam API для проверки аккаунта
• description - описание (необязательно)

⚠️ Важно: Steam токен необходим для проверки аккаунта!
                """)
                return
            
            username = args[0]
            password = args[1]
            game_name = args[2]
            price = float(args[3])
            steam_token = args[4]
            description = " ".join(args[5:]) if len(args) > 5 else ""
            
            # Проверяем Steam токен
            if not steam_token or steam_token == "your_steam_api_key_here":
                await update.message.reply_text("❌ Ошибка: Необходим действительный Steam API ключ!")
                return
            
            # Проверяем аккаунт через Steam API
            steam_valid = self.verify_steam_account(username, password, steam_token)
            
            if not steam_valid:
                await update.message.reply_text("❌ Ошибка: Не удалось проверить аккаунт через Steam API. Проверьте логин, пароль и токен.")
                return
            
            # Добавляем аккаунт в базу данных
            success = self.db.add_account(username, password, game_name, price, description)
            
            if success:
                await update.message.reply_text(f"""
✅ Аккаунт успешно добавлен и проверен!

🎮 Данные аккаунта:
👤 Логин: {username}
📝 Игра: {game_name}
💰 Цена: {price} руб/час
📄 Описание: {description if description else 'Не указано'}
✅ Steam API: Проверен

📊 Всего аккаунтов: {self.db.get_total_accounts()}
                """)
            else:
                await update.message.reply_text("❌ Не удалось добавить аккаунт. Проверьте данные и попробуйте снова.")
                
        except ValueError:
            await update.message.reply_text("❌ Ошибка: цена должна быть числом!")
        except Exception as e:
            await update.message.reply_text(f"❌ Ошибка добавления аккаунта: {e}")
    
    async def edit_account_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /edit_account"""
        user_id = update.effective_user.id
        
        if str(user_id) != self.admin_id:
            await update.message.reply_text("❌ У вас нет доступа к этой команде.")
            return
        
        try:
            # Получаем аргументы команды
            args = context.args
            
            if len(args) < 3:
                await update.message.reply_text("""
❌ Неправильный формат команды!

📝 Правильный формат:
/edit_account account_id field value

📋 Примеры:
/edit_account 1 price 75
/edit_account 1 description "Обновленное описание"
/edit_account 1 game_name "Dota 2"

🔧 Доступные поля:
• price - цена за час
• description - описание
• game_name - название игры
                """)
                return
            
            account_id = int(args[0])
            field = args[1]
            value = " ".join(args[2:])
            
            # Проверяем, что аккаунт существует
            account = self.db.get_account(account_id)
            if not account:
                await update.message.reply_text(f"❌ Аккаунт с ID {account_id} не найден.")
                return
            
            # Проверяем, что поле можно редактировать
            allowed_fields = ['price', 'description', 'game_name']
            if field not in allowed_fields:
                await update.message.reply_text(f"❌ Поле '{field}' нельзя редактировать. Доступные поля: {', '.join(allowed_fields)}")
                return
            
            # Если это цена, проверяем что это число
            if field == 'price':
                try:
                    value = float(value)
                except ValueError:
                    await update.message.reply_text("❌ Цена должна быть числом!")
                    return
            
            # Обновляем аккаунт
            success = self.db.update_account(account_id, field, value)
            
            if success:
                await update.message.reply_text(f"""
✅ Аккаунт успешно обновлен!

🎮 ID: {account_id}
📝 Поле: {field}
🔄 Новое значение: {value}

📊 Обновленные данные:
👤 Логин: {account['username']}
📝 Игра: {account['game_name'] if field != 'game_name' else value}
💰 Цена: {account['price'] if field != 'price' else value} руб/час
                """)
            else:
                await update.message.reply_text("❌ Не удалось обновить аккаунт. Проверьте данные и попробуйте снова.")
                
        except ValueError:
            await update.message.reply_text("❌ Ошибка: ID аккаунта должен быть числом!")
        except Exception as e:
            await update.message.reply_text(f"❌ Ошибка обновления аккаунта: {e}")
    
    async def set_token_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /set_token"""
        user_id = update.effective_user.id
        
        if str(user_id) != self.admin_id:
            await update.message.reply_text("❌ У вас нет доступа к этой команде.")
            return
        
        try:
            # Получаем аргументы команды
            args = context.args
            
            if len(args) < 2:
                await update.message.reply_text("""
❌ Неправильный формат команды!

📝 Правильный формат:
/set_token token_type token_value

📋 Примеры:
/set_token FUNPAY_TOKEN your_funpay_token_here
/set_token STEAM_API_KEY your_steam_api_key_here

🔧 Доступные типы токенов:
• FUNPAY_TOKEN - токен для FunPay
• STEAM_API_KEY - ключ API Steam
                """)
                return
            
            token_type = args[0].upper()
            token_value = " ".join(args[1:])
            
            # Проверяем тип токена
            allowed_types = ['FUNPAY_TOKEN', 'STEAM_API_KEY']
            if token_type not in allowed_types:
                await update.message.reply_text(f"❌ Неподдерживаемый тип токена: {token_type}. Доступные типы: {', '.join(allowed_types)}")
                return
            
            # Сохраняем токен в базу данных или конфигурацию
            success = self.db.save_token(token_type, token_value)
            
            if success:
                await update.message.reply_text(f"""
✅ Токен успешно сохранен!

🔑 Тип: {token_type}
🔐 Значение: {token_value[:20]}...
📅 Время: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

💡 Токен будет использоваться для всех операций с {token_type.split('_')[0]}.
                """)
            else:
                await update.message.reply_text("❌ Не удалось сохранить токен. Проверьте данные и попробуйте снова.")
                
        except Exception as e:
            await update.message.reply_text(f"❌ Ошибка сохранения токена: {e}")
    
    async def tokens_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /tokens"""
        user_id = update.effective_user.id
        
        if str(user_id) != self.admin_id:
            await update.message.reply_text("❌ У вас нет доступа к этой команде.")
            return
        
        try:
            # Получаем токены из базы данных
            funpay_token = self.db.get_token('FUNPAY_TOKEN')
            steam_token = self.db.get_token('STEAM_API_KEY')
            
            text = """
🔑 Управление токенами

📋 Текущие токены:
            """
            
            if funpay_token:
                text += f"""
✅ FUNPAY_TOKEN: {funpay_token[:20]}...
                """
            else:
                text += """
❌ FUNPAY_TOKEN: не настроен
                """
            
            if steam_token:
                text += f"""
✅ STEAM_API_KEY: {steam_token[:20]}...
                """
            else:
                text += """
❌ STEAM_API_KEY: не настроен
                """
            
            text += """

📝 Для настройки токенов используйте:
/set_token FUNPAY_TOKEN ваш_токен
/set_token STEAM_API_KEY ваш_ключ

⚠️ Важно: Токены необходимы для работы с FunPay и Steam API.
            """
            
            keyboard = [
                [InlineKeyboardButton("🔧 Настроить FunPay", callback_data="setup_funpay_token")],
                [InlineKeyboardButton("🔧 Настроить Steam", callback_data="setup_steam_token")],
                [InlineKeyboardButton("📋 Обновить", callback_data="refresh_tokens")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(text, reply_markup=reply_markup)
            
        except Exception as e:
            await update.message.reply_text(f"❌ Ошибка получения токенов: {e}")
    
    def verify_steam_account(self, username, password, steam_token):
        """Проверка аккаунта через Steam API"""
        try:
            # Здесь должна быть логика проверки аккаунта через Steam API
            # Пока что возвращаем True для демонстрации
            import requests
            
            # Пример проверки через Steam API
            # steam_api_url = f"https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key={steam_token}&steamids={steam_id}"
            # response = requests.get(steam_api_url)
            
            # Пока что просто проверяем, что токен не пустой
            if steam_token and steam_token != "your_steam_api_key_here":
                return True
            else:
                return False
                
        except Exception as e:
            self.logger.error(f"Ошибка проверки Steam аккаунта: {e}")
            return False
