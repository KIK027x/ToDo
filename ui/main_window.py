# ui/main_window.py
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QStackedWidget,
    QListWidget, QListWidgetItem, QLabel, QLineEdit, QPushButton,
    QComboBox
)
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QFont, QAction
from services.task_service import (
    add_task as svc_add_task,
    delete_task, toggle_completed, update_task_text,
    update_task_priority, get_tasks_filtered, get_tasks_sorted, clear_completed
)
from services.import_service import import_from_json
from ui.components import TaskItemWidget
from alarm_manager import AlarmManager
from plyer import notification
import sys


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ToDo App")
        self.resize(800, 600)

        # Центральный виджет
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        # Левое меню (скрытое, появляется по наведению)
        self.sidebar = Sidebar(self)
        self.sidebar.setFixedWidth(180)

        # Основной стек вкладок
        self.stacked_widget = QStackedWidget()
        self.list_view = TaskListView()
        self.stacked_widget.addWidget(self.list_view)

        # Layout
        main_layout = QHBoxLayout(self.central_widget)
        main_layout.addWidget(self.sidebar)
        main_layout.addWidget(self.stacked_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Меню сверху (для импорта и сортировки)
        self.create_menu_bar()

        # Запуск AlarmManager
        self.alarm_manager = AlarmManager()
        self.alarm_manager.alarm_triggered.connect(self.show_notification)
        self.alarm_manager.start()

    def create_menu_bar(self):
        menubar = self.menuBar()

        # Меню "Файл"
        file_menu = menubar.addMenu("Файл")
        import_action = QAction("Импортировать из JSON...", self)
        import_action.triggered.connect(self.import_json)
        file_menu.addAction(import_action)

        # Меню "Сортировка" (в верхнем меню)
        sort_menu = menubar.addMenu("Сортировка")
        sort_by_priority = QAction("По приоритету", self)
        sort_by_priority.triggered.connect(lambda: self.list_view.set_sort("priority"))
        sort_menu.addAction(sort_by_priority)

        sort_by_name = QAction("По названию", self)
        sort_by_name.triggered.connect(lambda: self.list_view.set_sort("name"))
        sort_menu.addAction(sort_by_name)

        sort_by_date = QAction("По дате", self)
        sort_by_date.triggered.connect(lambda: self.list_view.set_sort("date"))
        sort_menu.addAction(sort_by_date)

    def import_json(self):
        from PyQt6.QtWidgets import QFileDialog
        file_path, _ = QFileDialog.getOpenFileName(self, "Выберите JSON-файл", "", "JSON Files (*.json)")
        if file_path:
            import_from_json(file_path)
            self.list_view.refresh_tasks()

    def show_notification(self, task_id: int, task_text: str):
        notification.notify(
            title="Напоминание",
            message=f"Задача: {task_text}",
            timeout=10
        )


class Sidebar(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.main_window = parent
        self.setMouseTracking(True)
        self.hide()  # по умолчанию скрыто

        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(10, 20, 10, 10)

        self.buttons = {}
        for name in ["Все задачи", "Активные", "Завершённые"]:
            btn = QPushButton(name)
            btn.setCheckable(True)
            btn.clicked.connect(lambda checked, n=name: self.on_tab_click(n))
            layout.addWidget(btn)
            self.buttons[name] = btn

        self.sort_label = QLabel("Сортировать по:")
        self.sort_combo = QComboBox()
        self.sort_combo.addItems(["Приоритет", "Название", "Дате"])
        self.sort_combo.currentTextChanged.connect(self.on_sort_change)
        layout.addWidget(self.sort_label)
        layout.addWidget(self.sort_combo)

        layout.addStretch()

    def enterEvent(self, event):
        self.show()
        super().enterEvent(event)

    def leaveEvent(self, event):
        # Скрыть, если курсор не над sidebar и не над главным окном рядом
        pos = self.mapToGlobal(QPoint(0, 0))
        rect = self.geometry()
        cursor = self.main_window.mapFromGlobal(self.main_window.cursor().pos())
        if cursor.x() > self.width():
            self.hide()
        super().leaveEvent(event)

    def on_tab_click(self, name):
        self.main_window.list_view.set_filter(name)

    def on_sort_change(self, text):
        sort_map = {"Приоритет": "priority", "Название": "name", "Дате": "date"}
        self.main_window.list_view.set_sort(sort_map.get(text, "priority"))


class TaskListView(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)

        self.input = QLineEdit()
        self.input.setPlaceholderText("Новая задача...")
        self.input.returnPressed.connect(self.add_task)

        self.task_list = QListWidget()

        btn_layout = QHBoxLayout()
        self.add_btn = QPushButton("Добавить")
        self.del_btn = QPushButton("Удалить")
        self.clear_btn = QPushButton("Очистить завершённые")
        self.add_btn.clicked.connect(self.add_task)
        self.del_btn.clicked.connect(self.delete_task)
        self.clear_btn.clicked.connect(self.clear_completed)
        btn_layout.addWidget(self.add_btn)
        btn_layout.addWidget(self.del_btn)
        btn_layout.addWidget(self.clear_btn)

        layout.addWidget(self.input)
        layout.addWidget(self.task_list)
        layout.addLayout(btn_layout)

        self.current_filter = None  # None, True (completed), False (active)
        self.current_sort = "priority"  # по умолчанию сортировка по приоритету
        self.refresh_tasks()

    def set_filter(self, name):
        self.current_filter = {"Все задачи": None, "Активные": False, "Завершённые": True}.get(name)
        self.refresh_tasks()

    def set_sort(self, sort_key):
        self.current_sort = sort_key
        self.refresh_tasks()

    def add_task(self):
        text = self.input.text().strip()
        if text:
            try:
                svc_add_task(text)
                self.input.clear()
                self.refresh_tasks()
            except Exception as e:
                print(f"Ошибка при добавлении задачи: {e}")

    def delete_task(self):
        item = self.task_list.currentItem()
        if item and hasattr(item, 'task_id'):
            try:
                delete_task(item.task_id)
                self.refresh_tasks()
            except Exception as e:
                print(f"Ошибка при удалении задачи: {e}")

    def clear_completed(self):
        try:
            clear_completed()
            self.refresh_tasks()
        except Exception as e:
            print(f"Ошибка при очистке завершённых задач: {e}")

    def refresh_tasks(self):
        try:
            self.task_list.clear()
            if self.current_filter is not None:
                # фильтруем, но сортируем по выбранному параметру
                tasks = get_tasks_filtered(completed_filter=self.current_filter)
                # теперь сортируем вручную
                if self.current_sort == 'name':
                    tasks.sort(key=lambda t: t.text.lower())
                elif self.current_sort == 'date':
                    tasks.sort(key=lambda t: t.created_at)
                # priority уже отсортировано в SQL
            else:
                tasks = get_tasks_sorted(self.current_sort)

            for task in tasks:
                widget = TaskItemWidget(task)
                item = QListWidgetItem()
                item.task_id = task.id
                item.setSizeHint(widget.sizeHint())
                self.task_list.addItem(item)
                self.task_list.setItemWidget(item, widget)
        except Exception as e:
            print(f"Ошибка при обновлении списка задач: {e}")