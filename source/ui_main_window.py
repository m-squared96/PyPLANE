"""
Draws the main window of the PyPLANE Qt5 interface
"""
import sys
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout
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
        Adds components (buttons, text boxes, etc.) and draws the window
        """

        # Window Features
        self.x_prime_label = QLabel("x' =")
        self.y_prime_label = QLabel("y' =")
        self.x_prime_entry = QLineEdit()
        self.y_prime_entry = QLineEdit()

        # Layouts
        x_prime_layout = QHBoxLayout()
        y_prime_layout = QHBoxLayout()

        x_prime_layout.addWidget(self.x_prime_label)
        x_prime_layout.addWidget(self.x_prime_entry)
        y_prime_layout.addWidget(self.y_prime_label)
        y_prime_layout.addWidget(self.y_prime_entry)

        # Arrange Layouts
        overall_layout = QVBoxLayout()
        overall_layout.addLayout(x_prime_layout)
        overall_layout.addLayout(y_prime_layout)

        self.setLayout(overall_layout)

        # Set window title and show
        self.setWindowTitle("PyPLANE Main Window")
        self.show()

if __name__ == "__main__":
    PyPLANE = QApplication(sys.argv)
    PyPLANE_main_window = MainWindow()
    sys.exit(PyPLANE.exec_())