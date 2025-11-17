# services/task_service.py
from database import get_connection
from models import Task
from typing import List, Optional
from datetime import datetime

PRIORITY_ORDER = {'high': 0, 'normal': 1, 'low': 2}


def add_task(text: str, alarm_time: str = None) -> int:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO tasks (text, completed, priority, created_at, alarm_time) VALUES (?, ?, ?, ?, ?)",
        (text, False, 'normal', datetime.now().isoformat(), alarm_time)
    )
    task_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return task_id


def delete_task(task_id: int):
    conn = get_connection()
    conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()


def clear_completed():
    conn = get_connection()
    conn.execute("DELETE FROM tasks WHERE completed = 1")
    conn.commit()
    conn.close()


def toggle_completed(task_id: int, completed: bool):
    conn = get_connection()
    conn.execute("UPDATE tasks SET completed = ? WHERE id = ?", (int(completed), task_id))
    conn.commit()
    conn.close()


def update_task_text(task_id: int, text: str):
    conn = get_connection()
    conn.execute("UPDATE tasks SET text = ? WHERE id = ?", (text, task_id))
    conn.commit()
    conn.close()


def update_task_priority(task_id: int, priority: str):
    if priority not in ('low', 'normal', 'high'):
        raise ValueError("Invalid priority")
    conn = get_connection()
    conn.execute("UPDATE tasks SET priority = ? WHERE id = ?", (priority, task_id))
    conn.commit()
    conn.close()


def set_alarm(task_id: int, alarm_time: str):
    conn = get_connection()
    conn.execute("UPDATE tasks SET alarm_time = ? WHERE id = ?", (alarm_time, task_id))
    conn.commit()
    conn.close()


def remove_alarm(task_id: int):
    conn = get_connection()
    conn.execute("UPDATE tasks SET alarm_time = NULL WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()


def get_all_tasks() -> List[Task]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, text, completed, priority, created_at, alarm_time FROM tasks ORDER BY completed ASC, CASE priority WHEN 'high' THEN 0 WHEN 'normal' THEN 1 ELSE 2 END, created_at ASC")
    rows = cursor.fetchall()
    conn.close()
    return [Task.from_row(row) for row in rows]


def get_tasks_filtered(completed_filter: Optional[bool] = None) -> List[Task]:
    conn = get_connection()
    cursor = conn.cursor()
    if completed_filter is not None:
        cursor.execute(
            "SELECT id, text, completed, priority, created_at, alarm_time FROM tasks WHERE completed = ? ORDER BY completed ASC, CASE priority WHEN 'high' THEN 0 WHEN 'normal' THEN 1 ELSE 2 END, created_at ASC",
            (int(completed_filter),)
        )
    else:
        cursor.execute(
            "SELECT id, text, completed, priority, created_at, alarm_time FROM tasks ORDER BY completed ASC, CASE priority WHEN 'high' THEN 0 WHEN 'normal' THEN 1 ELSE 2 END, created_at ASC")
    rows = cursor.fetchall()
    conn.close()
    return [Task.from_row(row) for row in rows]


def get_tasks_sorted(sort_by: str = 'priority') -> List[Task]:
    conn = get_connection()
    cursor = conn.cursor()

    order_clause = {
        'priority': "completed ASC, CASE priority WHEN 'high' THEN 0 WHEN 'normal' THEN 1 ELSE 2 END, created_at ASC",
        'name': "completed ASC, text COLLATE NOCASE ASC, created_at ASC",
        'date': "completed ASC, created_at ASC"
    }.get(sort_by, "completed ASC, CASE priority WHEN 'high' THEN 0 WHEN 'normal' THEN 1 ELSE 2 END, created_at ASC")

    cursor.execute(f"SELECT id, text, completed, priority, created_at, alarm_time FROM tasks ORDER BY {order_clause}")
    rows = cursor.fetchall()
    conn.close()
    return [Task.from_row(row) for row in rows]


def get_tasks_with_alarms() -> List[Task]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, text, completed, priority, created_at, alarm_time FROM tasks WHERE alarm_time IS NOT NULL")
    rows = cursor.fetchall()
    conn.close()
    return [Task.from_row(row) for row in rows]


def get_overdue_alarms() -> List[Task]:
    now = datetime.now().isoformat()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, text, completed, priority, created_at, alarm_time FROM tasks WHERE alarm_time IS NOT NULL AND alarm_time < ? AND completed = 0",
        (now,)
    )
    rows = cursor.fetchall()
    conn.close()
    return [Task.from_row(row) for row in rows]