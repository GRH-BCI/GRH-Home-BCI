import sys
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QScrollArea,
    QLabel,
)


class ScrollableWidgetDemo(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Vertical Scroll Bar Example")
        self.setGeometry(100, 100, 400, 300)  # Set window size

        # Create the main widget
        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget)

        # Create a vertical layout for the main widget
        layout = QVBoxLayout(self.main_widget)

        # Create a scroll area
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)  # Allow resizing of the content

        # Create a widget to hold scrollable content
        self.scroll_content = QWidget()
        self.scroll_area.setWidget(self.scroll_content)

        # Add the scroll area to the layout
        layout.addWidget(self.scroll_area)

        # Set the layout for the scrollable content
        self.scroll_layout = QVBoxLayout(self.scroll_content)

        # Add multiple widgets to the scrollable content
        for i in range(1, 21):  # Add 20 labels as an example
            label = QLabel(f"Item {i}")
            self.scroll_layout.addWidget(label)


def main():
    app = QApplication(sys.argv)
    window = ScrollableWidgetDemo()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()

