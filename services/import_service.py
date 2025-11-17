# services/import_service.py
import json
from pathlib import Path
from database import get_connection
from datetime import datetime

def import_from_json(file_path: str):
    with open(file_path, 'r', encoding='utf-8') as f:
        tasks = json.load(f)

    conn = get_connection()
    cursor = conn.cursor()
    for task in tasks:
        created = task.get('created_at', datetime.now().isoformat())
        completed = int(task.get('completed', False))
        priority = task.get('priority', 'normal')
        if priority not in ('low', 'normal', 'high'):
            priority = 'normal'
        cursor.execute(
            "INSERT INTO tasks (text, completed, priority, created_at, alarm_time) VALUES (?, ?, ?, ?, ?)",
            (task['text'], completed, priority, created, task.get('alarm_time', None))
        )
    conn.commit()
    conn.close()