# ui/components.py
from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QCheckBox, QLineEdit, QComboBox, QLabel,
    QPushButton, QDateTimeEdit
)
from PyQt6.QtCore import Qt, QDateTime
from PyQt6.QtGui import QFont
from services.task_service import (
    toggle_completed, update_task_text, update_task_priority, set_alarm
)

class TaskItemWidget(QWidget):
    def __init__(self, task):
        super().__init__()
        self.task = task
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.checkbox = QCheckBox()
        self.checkbox.setChecked(task.completed)
        self.checkbox.stateChanged.connect(self.on_toggle)

        self.text_edit = QLineEdit(task.text)
        self.text_edit.editingFinished.connect(self.on_text_edit)

        self.priority_combo = QComboBox()
        self.priority_combo.addItems(["high", "normal", "low"])
        self.priority_combo.setCurrentText(task.priority)
        self.priority_combo.currentTextChanged.connect(self.on_priority_change)

        self.alarm_button = QPushButton("Будильник")
        self.alarm_button.clicked.connect(self.set_alarm_time)

        layout.addWidget(self.checkbox)
        layout.addWidget(self.text_edit, 1)
        layout.addWidget(self.priority_combo)
        layout.addWidget(self.alarm_button)

        if task.completed:
            self.apply_completed_style()

        if task.alarm_time:
            self.alarm_button.setText("⏰")

    def apply_completed_style(self):
        font = QFont()
        font.setStrikeOut(True)
        self.text_edit.setFont(font)
        self.text_edit.setStyleSheet("color: gray;")

    def on_toggle(self, state):
        completed = state == Qt.CheckState.Checked.value
        toggle_completed(self.task.id, completed)
        if completed:
            self.apply_completed_style()
        else:
            self.text_edit.setFont(QFont())
            self.text_edit.setStyleSheet("")

    def on_text_edit(self):
        new_text = self.text_edit.text().strip()
        if new_text:
            update_task_text(self.task.id, new_text)

    def on_priority_change(self, priority):
        update_task_priority(self.task.id, priority)

    def set_alarm_time(self):
        from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QPushButton
        dialog = QDialog()
        dialog.setWindowTitle("Установить будильник")
        layout = QVBoxLayout(dialog)

        date_time_edit = QDateTimeEdit()
        date_time_edit.setCalendarPopup(True)
        date_time_edit.setDateTime(QDateTime.currentDateTime())  # текущее время по умолчанию

        layout.addWidget(date_time_edit)

        btn_layout = QHBoxLayout()
        save_btn = QPushButton("Сохранить")
        cancel_btn = QPushButton("Отмена")
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

        def save_alarm():
            alarm_time = date_time_edit.dateTime().toPyDateTime().isoformat()
            set_alarm(self.task.id, alarm_time)
            self.alarm_button.setText("⏰")
            dialog.accept()

        save_btn.clicked.connect(save_alarm)
        cancel_btn.clicked.connect(dialog.reject)

        dialog.exec()