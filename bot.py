import logging
import sqlite3
import asyncio  # если нет
import os
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
from config import TOKEN, GAME_1_URL, GAME_2_URL, GAME_3_URL, CHANNEL_ID
from database import init_db, add_user
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.date import DateTrigger
from keep_alive import keep_alive

# Запускаем веб-сервер для Render
keep_alive()

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Инициализация базы данных
init_db()

# Планировщик для отправки сообщений по расписанию
scheduler = AsyncIOScheduler()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start - первое сообщение с игрой"""
    user = update.effective_user
    
    # Сохраняем пользователя в базу
    add_user(user.id, user.username, user.first_name, user.last_name)
    
    # Сохраняем chat_id для рассылки
    if 'user_ids' not in context.bot_data:
        context.bot_data['user_ids'] = set()
    context.bot_data['user_ids'].add(update.effective_chat.id)
    
    # Создаем кнопку с миниаппом (игрой)
    keyboard = [
    [InlineKeyboardButton("🌟 Играть в игру", web_app=WebAppInfo(url=GAME_1_URL))]
]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Текст новости
    news_text = """
🎉 *Понедельник — «Встреча»*

В первый день Масленицы начинались приготовления к празднику. Делали соломенное чучело Масленицы, украшали дома и дворы, пекли первые блины. Этот день был спокойным и семейным — люди настраивались на весёлую масленичную неделю и делились угощением с близкими.
    """
    
    await update.message.reply_text(
        news_text,
        parse_mode='Markdown',
        reply_markup=reply_markup
    )


async def send_game_1(context: ContextTypes.DEFAULT_TYPE):
    """Отправка первой игры (18 февраля)"""
    keyboard = [
        [InlineKeyboardButton("🌟 Играть в игру", web_app=WebAppInfo(url=GAME_2_URL))],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    text = """
 ✨*Среда — «Лакомка»*

Среда считалась самым вкусным днём Масленицы. Хозяйки накрывали богатые столы с блинами, мёдом, вареньем и сметаной. По традиции тёщи приглашали зятьёв в гости и угощали их самыми лучшими блюдами, показывая своё гостеприимство и добрые отношения.
    """
    
    # Отправляем всем пользователям
    if CHANNEL_ID:
        await context.bot.send_message(
            chat_id=CHANNEL_ID,
            text=text,
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
    else:
        # Отправляем всем сохраненным пользователям
        for chat_id in context.bot_data.get('user_ids', set()):
            try:
                await context.bot.send_message(
                    chat_id=chat_id,
                    text=text,
                    parse_mode='Markdown',
                    reply_markup=reply_markup
                )
            except Exception as e:
                logger.error(f"Не удалось отправить сообщение {chat_id}: {e}")

async def send_game_2(context: ContextTypes.DEFAULT_TYPE):
    """Отправка второй игры (20 февраля)"""
    keyboard = [
        [InlineKeyboardButton("🌟 Играть в игру", web_app=WebAppInfo(url=GAME_3_URL))],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    text = """
 🎊*Пятница — «Тёщины вечерки»*

В этот день зятья отвечали тёщам взаимностью — приглашали их к себе в гости. Хозяин дома должен был сам угощать блинами, проявляя уважение и благодарность. Пятница символизировала примирение, внимание к семье и укрепление родственных связей.
    """
    
    if CHANNEL_ID:
        await context.bot.send_message(
            chat_id=CHANNEL_ID,
            text=text,
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
    else:
        for chat_id in context.bot_data.get('user_ids', set()):
            try:
                await context.bot.send_message(
                    chat_id=chat_id,
                    text=text,
                    parse_mode='Markdown',
                    reply_markup=reply_markup
                )
            except Exception as e:
                logger.error(f"Не удалось отправить сообщение {chat_id}: {e}")


async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """📢 ОТПРАВИТЬ СООБЩЕНИЕ ВСЕМ ПОЛЬЗОВАТЕЛЯМ ИЗ БАЗЫ ДАННЫХ"""
    
    # Твой USER ID (админ)
    YOUR_USER_ID = 1453183670
    
    # Проверка прав
    if update.effective_user.id != YOUR_USER_ID:
        await update.message.reply_text("⛔ Эта команда только для админа")
        return
    
    await update.message.reply_text("⏳ Загружаю список пользователей из базы данных...")
    
    # Подключаемся к базе данных
    conn = sqlite3.connect('bot_database.db')
    c = conn.cursor()
    c.execute("SELECT user_id FROM users")
    db_users = c.fetchall()
    conn.close()
    
    # Превращаем в список ID
    user_ids = [row[0] for row in db_users]
    total = len(user_ids)
    
    if total == 0:
        await update.message.reply_text("❌ В базе нет пользователей! Попроси кого-нибудь написать /start")
        return
    
    await update.message.reply_text(f"👥 Найдено пользователей: {total}. Начинаю рассылку...")
    
    # Текст сообщения (как в send_game_1)
    text = """
 ✨*Среда — «Лакомка»*

Среда считалась самым вкусным днём Масленицы. Хозяйки накрывали богатые столы с блинами, мёдом, вареньем и сметаной. По традиции тёщи приглашали зятьёв в гости и угощали их самыми лучшими блюдами, показывая своё гостеприимство и добрые отношения.
    """
    
    keyboard = [
        [InlineKeyboardButton("🌟 Играть в игру", web_app=WebAppInfo(url=GAME_2_URL))],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Отправляем
    sent = 0
    failed = 0
    
    for chat_id in user_ids:
        try:
            await context.bot.send_message(
                chat_id=chat_id,
                text=text,
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
            sent += 1
            # Маленькая пауза, чтобы не забанили
            await asyncio.sleep(0.05)
        except Exception as e:
            failed += 1
            logger.error(f"Не удалось отправить {chat_id}: {e}")
    
    # Отчёт
    await update.message.reply_text(
        f"✅ Рассылка завершена!\n"
        f"📨 Отправлено: {sent}\n"
        f"❌ Ошибок: {failed}\n"
        f"👥 Всего в базе: {total}"
    )


def main():
    """Главная функция запуска бота"""
    # Создаем приложение
    application = Application.builder().token(TOKEN).build()
    
    # Регистрируем обработчики команд
    application.add_handler(CommandHandler("start", start)) 
    application.add_handler(CommandHandler("sendnow", send_now))
    application.add_handler(CommandHandler("broadcast", broadcast))
    
    # Настраиваем расписание для 2025 года
    current_year = datetime.now().year
    
    # Отправка 18 февраля в 9:00
    scheduler.add_job(
        send_game_1,
    DateTrigger(run_date=datetime(current_year, 2, 18, 5, 0)),
    args=[application],
    id='game1_18feb',
    misfire_grace_time=3600,
    replace_existing=True  

    )
    
    # Отправка 20 февраля в 9:00
    scheduler.add_job(
        send_game_2,
        DateTrigger(run_date=datetime(current_year, 2, 20, 9, 0)),
        args=[application],
        id='game2_20feb'
    )
    
    # Запускаем планировщик
    scheduler.start()
    
    # Запускаем бота
    print("Бот запущен! Нажми Ctrl+C для остановки.")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()