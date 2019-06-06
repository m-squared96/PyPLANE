"""
Draws the main window of the PyPLANE Qt5 interface
"""
# TODO: Take user input for params
# TODO: Take user input for phase_coords
# TODO: Take user input for t_f and t_r
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
        self.plot_button = QPushButton("Plot")

        # Layouts
        x_prime_layout = QHBoxLayout()
        y_prime_layout = QHBoxLayout()
        button_layout = QHBoxLayout()

        x_prime_layout.addWidget(self.x_prime_label)
        x_prime_layout.addWidget(self.x_prime_entry)
        y_prime_layout.addWidget(self.y_prime_label)
        y_prime_layout.addWidget(self.y_prime_entry)
        
        button_layout.addStretch()
        button_layout.addWidget(self.plot_button)
        button_layout.addStretch()

        # Arrange Layouts
        overall_layout = QVBoxLayout()
        overall_layout.addLayout(x_prime_layout)
        overall_layout.addLayout(y_prime_layout)
        overall_layout.addLayout(button_layout)

        self.setLayout(overall_layout)

        # Button Actions
        self.plot_button.clicked.connect(self.plot_button_clicked)

        # Set window title and show
        self.setWindowTitle("PyPLANE Main Window")
        self.show()

    def plot_button_clicked(self):
        """
        Plot the phase space when the 'plot' button is clicked
        """
        f_1 = self.x_prime_entry.text()
        f_2 = self.y_prime_entry.text()
        #print(f_1, f_2)

        phase_coords = ['x', 'y']
        eqns = [f_1, f_2]
        params = {'a': -1, 'b': 5, 'c': -4, 'd': -2}
        t_f = 5
        t_r = -5

        system_of_eqns = SystemOfEquations(phase_coords, eqns, params=params)
        plotter = PhaseSpacePlotter(system_of_eqns, t_f, t_r)
        

if __name__ == "__main__":
    PyPLANE = QApplication(sys.argv)
    PyPLANE_main_window = MainWindow()
    sys.exit(PyPLANE.exec_())