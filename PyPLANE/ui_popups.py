from PyQt5.QtWidgets import (
    QMessageBox,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QWidget
)
from PyQt5.QtGui import QWindow

class BasicPopup(QMessageBox):

    def __init__(self, title_text = "Title Text", message = "Message Text"):
        
        super().__init__()
        self.setSizeGripEnabled(True)

        self.setWindowTitle(title_text)
        self.setText(message)
        self.setDetailedText('A bunch more text')
        # self.setSizeGripEnabled(True)
        self.resize(500, 500)

    layout = QVBoxLayout

# class BasicPopup(QWidget):

#     def __init__(self, title_text = "Title Text", message = "Message Text"):
#         super().__init__()
#         layout = QVBoxLayout()
#         self.label = QLabel(title_text)
#         layout.addWidget(self.label)
#         self.setLayout(layout)

def display_test_popup():
    test = BasicPopup()
    test.exec_()