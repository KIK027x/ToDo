# database.py
import sqlite3
from datetime import datetime
from pathlib import Path

DB_PATH = Path("tasks.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            text TEXT NOT NULL,
            completed BOOLEAN NOT NULL DEFAULT 0,
            priority TEXT NOT NULL DEFAULT 'normal',
            created_at TEXT NOT NULL,
            alarm_time TEXT
        )
    ''')
    # проверим, есть ли колонка alarm_time
    cursor.execute("PRAGMA table_info(tasks)")
    columns = [row[1] for row in cursor.fetchall()]
    if 'alarm_time' not in columns:
        cursor.execute("ALTER TABLE tasks ADD COLUMN alarm_time TEXT")
    conn.commit()
    conn.close()

def get_connection():
    return sqlite3.connect(DB_PATH)