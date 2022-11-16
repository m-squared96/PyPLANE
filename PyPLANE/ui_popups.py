from PyQt5.QtWidgets import (
    QMessageBox,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QWidget
)

class BasicPopup(QMessageBox):

    def __init__(self, title_text = "Title Text", message = "Message Text"):
        super().__init__()
        self.setWindowTitle(title_text)
        self.setText(message)
        self.setDetailedText('A bunch more text')
        # self.setSizeGripEnabled(True)
        # self.setMinimumSize(100, 100)

    layout = QVBoxLayout

def display_test_popup():
    test = BasicPopup()
    test.exec_()