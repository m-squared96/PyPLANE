"""
Draws the main window of the PyPLANE Qt5 interface
"""
from sys import argv, exit
from PyQt5.QtWidgets import (
    QLineEdit, # Text boxes
    QPushButton, # Buttons
    QVBoxLayout, # For arranging Widgets
    QHBoxLayout,
    QWidget,
    QApplication
)

class MainWindow(QWidget):
    """
    TODO: Insert docstring
    """

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        """
        Initalizes UI
        TODO: Make this docstring not state the bleedin' obvious
        """
        self.show()

PyPLANE = QApplication(argv)
PyPLANE_main_window = MainWindow()
exit(PyPLANE.exec_())