# alarm_manager.py
from PyQt6.QtCore import QTimer, QThread, pyqtSignal
from services.task_service import get_tasks_with_alarms, remove_alarm
from datetime import datetime

class AlarmManager(QThread):
    alarm_triggered = pyqtSignal(int, str)  # task_id, text

    def __init__(self):
        super().__init__()
        self.timer = QTimer()
        self.timer.timeout.connect(self.check_alarms)
        self.timer.start(10000)  # проверка каждые 10 секунд

    def run(self):
        self.exec()

    def check_alarms(self):
        tasks = get_tasks_with_alarms()
        now = datetime.now().isoformat()
        for task in tasks:
            if task.alarm_time and task.alarm_time <= now and not task.completed:
                self.alarm_triggered.emit(task.id, task.text)
                remove_alarm(task.id)