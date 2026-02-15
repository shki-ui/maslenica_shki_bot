import sqlite3
from datetime import datetime

def init_db():
    """Создает таблицы при первом запуске"""
    conn = sqlite3.connect('bot_database.db')
    c = conn.cursor()
    
    # Таблица пользователей
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (user_id INTEGER PRIMARY KEY,
                  username TEXT,
                  first_name TEXT,
                  last_name TEXT,
                  registered_date TEXT)''')
    
    
    
    conn.commit()
    conn.close()
    print("База данных инициализирована")

def add_user(user_id, username, first_name, last_name):
    """Добавляет нового пользователя"""
    try:
        conn = sqlite3.connect('bot_database.db')
        c = conn.cursor()
        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        c.execute('''INSERT OR IGNORE INTO users 
                     (user_id, username, first_name, last_name, registered_date)
                     VALUES (?, ?, ?, ?, ?)''',
                  (user_id, username, first_name, last_name, date))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Ошибка добавления пользователя: {e}")
        return False



def get_user_count():
    """Получает количество пользователей"""
    try:
        conn = sqlite3.connect('bot_database.db')
        c = conn.cursor()
        
        c.execute('''SELECT COUNT(*) FROM users''')
        count = c.fetchone()[0]
        
        conn.close()
        return count
    except Exception as e:
        print(f"Ошибка получения количества пользователей: {e}")
        return 0
