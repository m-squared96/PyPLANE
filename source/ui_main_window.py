"""
Draws the main window of the PyPLANE Qt5 interface
"""
import sys
from PyQt5.QtWidgets import (
    QLineEdit, # Text boxes
    QPushButton, # Buttons
    QVBoxLayout, # For arranging Widgets
    QHBoxLayout,
    QWidget,
    QApplication
)
from equations import SystemOfEquations
from trajectory import PhaseSpacePlotter

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
        
        self.setWindowTitle("PyPLANE")
        self.show()

PyPLANE = QApplication(sys.argv)
PyPLANE_main_window = MainWindow()
sys.exit(PyPLANE.exec_())