# main.py
import sys
from PyQt6.QtWidgets import QApplication, QMessageBox, QSystemTrayIcon, QMenu
from PyQt6.QtGui import QIcon, QAction
from PyQt6.QtCore import Qt
from database import init_db
from ui.main_window import MainWindow
from services.task_service import get_overdue_alarms

class AppWithTray(MainWindow):
    def __init__(self):
        super().__init__()

        # Иконка в трее
        self.tray_icon = QSystemTrayIcon(self)
        # self.tray_icon.setIcon(QIcon("path/to/icon.png"))
        self.tray_icon.setIcon(self.style().standardIcon(self.style().StandardPixmap.SP_ComputerIcon))
        self.tray_icon.setVisible(True)

        # Создаём меню для иконки в трее
        tray_menu = QMenu()
        show_action = QAction("Показать", self)
        show_action.triggered.connect(self.show)
        tray_menu.addAction(show_action)

        quit_action = QAction("Выход", self)
        quit_action.triggered.connect(self.quit_app)
        tray_menu.addAction(quit_action)

        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.activated.connect(self.tray_icon_activated)

        # Проверка просроченных будильников при запуске
        overdue_tasks = get_overdue_alarms()
        if overdue_tasks:
            count = len(overdue_tasks)
            msg = f"У вас {count} незавершённых задач с прошедшим временем будильника."
            QMessageBox.information(None, "Просроченные задачи", msg)

    def tray_icon_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.show()

    def closeEvent(self, event):
        # Сворачиваем в трей вместо закрытия
        event.ignore()
        self.hide()

    def quit_app(self):
        self.alarm_manager.quit()
        QApplication.quit()

if __name__ == "__main__":
    init_db()
    app = QApplication(sys.argv)
    window = AppWithTray()
    window.show()
    sys.exit(app.exec())