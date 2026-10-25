import sys
from PySide6 import QtWidgets, QtCore
from storage import load_collection, save_collection
from config import NAME_FILE_SAVES


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Task Manager")
        self.resize(500, 400)

        self.collection = load_collection(NAME_FILE_SAVES)

        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)
        layout = QtWidgets.QVBoxLayout(central_widget)

        self.list_widget = QtWidgets.QListWidget()
        self.btn_show = QtWidgets.QPushButton("Посмотреть задачи")
        self.btn_add = QtWidgets.QPushButton("Добавить задачу")
        self.btn_quit = QtWidgets.QPushButton("Выход")

        layout.addWidget(self.list_widget)
        layout.addWidget(self.btn_show)
        layout.addWidget(self.btn_add)
        layout.addWidget(self.btn_quit)

        self.btn_show.clicked.connect(self.show_all_tasks)
        self.btn_add.clicked.connect(self.add_task)
        self.btn_quit.clicked.connect(self.close)

        self.refresh_list()

    def refresh_list(self):
        self.list_widget.clear()
        for task in self.collection:
            self.list_widget.addItem(task["name"])

    def show_all_tasks(self):
        self.refresh_list()

    def add_task(self):
        text, ok = QtWidgets.QInputDialog.getText(self, "Новая задача", "Введите задачу:")
        if ok and text:
            self.collection.append(text)
            save_collection(self.collection, NAME_FILE_SAVES)
            self.refresh_list()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
