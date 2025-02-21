from PyQt5.QtCore import QThreadPool, QRunnable, pyqtSlot
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QTextEdit
import sys
import time


class MyApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.threadpool = QThreadPool()

    def initUI(self):
        self.layout = QVBoxLayout()

        self.text_edit = QTextEdit(self)
        self.text_edit.setReadOnly(True)
        self.layout.addWidget(self.text_edit)

        self.start_button = QPushButton("Start Threads", self)
        self.start_button.clicked.connect(self.run_threads)
        self.layout.addWidget(self.start_button)

        self.setLayout(self.layout)
        self.setWindowTitle("PyQt5 ThreadPool Example")
        self.setGeometry(100, 100, 400, 300)

    def update_log(self, message):
        """Update the text box with log messages."""
        self.text_edit.append(message)

    def create_worker(self, task_name):
        """Creates a QRunnable worker that runs in a separate thread."""
        class Worker(QRunnable):
            def __init__(self, task_name, callback):
                super().__init__()
                self.task_name = task_name
                self.callback = callback
                self.setAutoDelete(True)  # Ensures proper cleanup

            @pyqtSlot()
            def run(self):
                """Simulated long-running task."""
                for i in range(5):
                    time.sleep(1)  # Simulate work
                    self.callback(f"{self.task_name}: Step {i+1} completed")

        return Worker(task_name, self.update_log)

    def run_threads(self):
        """Runs two separate tasks using QThreadPool."""
        worker1 = self.create_worker("Task 1")
        worker2 = self.create_worker("Task 2")

        self.threadpool.start(worker1)
        self.threadpool.start(worker2)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyApp()
    window.show()
    sys.exit(app.exec_())
