import sqlite3
from datetime import datetime
import uuid
def init_db():
    conn = sqlite3.connect('reservations.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS reservations
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  user_id TEXT,
                  date TEXT,
                  time TEXT,
                  UNIQUE(date, time))''')
    c.execute('''CREATE TABLE IF NOT EXISTS download_keys
                 (key TEXT PRIMARY KEY,
                  used BOOLEAN)''')
    c.execute('''CREATE TABLE IF NOT EXISTS user_levels
                (user_id TEXT PRIMARY KEY,
                name TEXT,
                phone TEXT,
                gender TEXT,
                level TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS user_sessions
                (user_id TEXT PRIMARY KEY,
                session_data TEXT,
                expire_time TEXT)''')
    conn.commit()
    conn.close()

def get_user_level(user_id):
    conn = sqlite3.connect('reservations.db')
    c = conn.cursor()
    c.execute("SELECT level FROM user_levels WHERE user_id = ?", (user_id,))
    result = c.fetchone()
    conn.close()
    return result[0] if result else "user"

def is_user_registered(user_id):
    conn = sqlite3.connect('reservations.db')
    c = conn.cursor()
    c.execute("SELECT * FROM user_levels WHERE user_id = ?", (user_id,))
    result = c.fetchone()
    conn.close()
    return result is not None

def set_user_session(user_id, session_data, expire_time):
    conn = sqlite3.connect('reservations.db')
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO user_sessions (user_id, session_data, expire_time) VALUES (?, ?, ?)",
              (user_id, str(session_data), expire_time.isoformat()))
    conn.commit()
    conn.close()

def get_user_session(user_id):
    conn = sqlite3.connect('reservations.db')
    c = conn.cursor()
    c.execute("SELECT session_data, expire_time FROM user_sessions WHERE user_id = ?", (user_id,))
    result = c.fetchone()
    conn.close()
    if result:
        session_data, expire_time_str = result
        expire_time = datetime.fromisoformat(expire_time_str)
        if datetime.now() > expire_time:
            delete_user_session(user_id)
            return None
        return eval(session_data)
    return None

def delete_user_session(user_id):
    conn = sqlite3.connect('reservations.db')
    c = conn.cursor()
    c.execute("DELETE FROM user_sessions WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()

def generate_download_key():
    key = str(uuid.uuid4())
    conn = sqlite3.connect('reservations.db')
    c = conn.cursor()
    c.execute("INSERT INTO download_keys (key, used) VALUES (?, ?)", (key, False))
    conn.commit()
    conn.close()
    return key