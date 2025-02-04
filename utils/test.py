from PyQt5.QtWidgets import QApplication, QMessageBox
import sys

def show_warning_popup(message="This is a warning!", title="Warning"):
    """Creates a warning popup in PyQt5."""
    app = QApplication(sys.argv)
    msg_box = QMessageBox()
    msg_box.setIcon(QMessageBox.Warning)
    msg_box.setWindowTitle(title)
    msg_box.setText(message)
    msg_box.setStandardButtons(QMessageBox.Ok)
    msg_box.exec_()

# Example usage
if __name__ == "__main__":
    show_warning_popup("This is a custom warning message!", "Custom Warning")