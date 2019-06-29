"""
Draws the main window of the PyPLANE Qt5 interface
"""

import sys
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout
)

from PyQt5.QtGui import(
    QPixmap,
    QIcon
)

from ui_default_canvas import DefaultCanvas

import matplotlib.pyplot as plt

from equations import SystemOfEquations
from trajectory import PhaseSpacePlotter

VERSION = "0.0-pre-apha"

class MainWindow(QMainWindow):
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

        # Define central widget
        cent_widget = QWidget(self)
        self.setCentralWidget(cent_widget)

        # Window Features
        self.x_prime_label = QLabel("x' =")
        self.y_prime_label = QLabel("y' =")
        self.x_prime_entry = QLineEdit("y*sin(x)")
        self.y_prime_entry = QLineEdit("-x")
        self.plot_button = QPushButton("Plot")
        self.phase_plot = DefaultCanvas()
        
        self.phase_plot.update_system(self.phase_plot.default_system)
        
        # Parameter inputs
        self.parameter_input_boxes = {}
        self.no_of_params = 5
        for param_num in range(self.no_of_params):
            self.parameter_input_boxes["param_"+str(param_num)+"_name"] = QLineEdit()
            self.parameter_input_boxes["param_"+str(param_num)+"_val"] = QLineEdit()

        # Layouts
        x_prime_layout = QHBoxLayout()
        y_prime_layout = QHBoxLayout()
        button_layout = QHBoxLayout()

        self.parameter_layouts = {}
        for param_num in range(self.no_of_params):
            self.parameter_layouts["param_"+str(param_num)+"_layout"] = QHBoxLayout()
            self.equals_sign = QLabel("=")
            self.parameter_layouts["param_"+str(param_num)+"_layout"].addWidget(self.parameter_input_boxes["param_"+str(param_num)+"_name"])
            self.parameter_layouts["param_"+str(param_num)+"_layout"].addWidget(self.equals_sign)
            self.parameter_layouts["param_"+str(param_num)+"_layout"].addWidget(self.parameter_input_boxes["param_"+str(param_num)+"_val"])

        x_prime_layout.addWidget(self.x_prime_label)
        x_prime_layout.addWidget(self.x_prime_entry)
        y_prime_layout.addWidget(self.y_prime_label)
        y_prime_layout.addWidget(self.y_prime_entry)
        
        button_layout.addStretch()
        button_layout.addWidget(self.plot_button)
        button_layout.addStretch()

        # Arrange Layouts
        equation_entry_layout = QVBoxLayout()
        equation_entry_layout.addLayout(x_prime_layout)
        equation_entry_layout.addLayout(y_prime_layout)
        equation_entry_layout.addLayout(button_layout)

        parameters_layout = QVBoxLayout()
        parameters_layout.addWidget(QLabel("Parameters (Optional) :"))
        for param_num in range(self.no_of_params):
            parameters_layout.addLayout(self.parameter_layouts["param_"+str(param_num)+"_layout"])

        inputs_layout = QVBoxLayout()
        inputs_layout.addLayout(equation_entry_layout)
        inputs_layout.addLayout(parameters_layout)
        inputs_layout.addStretch()

        overall_layout = QHBoxLayout()
        overall_layout.addLayout(inputs_layout)
        overall_layout.addWidget(self.phase_plot)

        cent_widget.setLayout(overall_layout)

        # Button Actions
        self.plot_button.clicked.connect(self.plot_button_clicked)

        # Set window title and show
        self.setWindowTitle("PyPLANE "+VERSION)
        self.show()

    def plot_button_clicked(self):
        """
        Plot the phase space when the 'plot' button is clicked
        """
        f_1 = self.x_prime_entry.text()
        f_2 = self.y_prime_entry.text()

        phase_coords = ["x", "y"]
        eqns = [f_1, f_2]
        
        # Grab parameters
        passed_params = {}
        for param_num in range(self.no_of_params):
            if self.parameter_input_boxes["param_"+str(param_num)+"_name"].text():
                passed_params[self.parameter_input_boxes["param_"+str(param_num)+"_name"].text()] = float(self.parameter_input_boxes["param_"+str(param_num)+"_val"].text())

        t_f = 5
        t_r = -5

        system_of_eqns = SystemOfEquations(phase_coords, eqns, params=passed_params)
        self.phase_plot.update_system(system_of_eqns)
        

if __name__ == "__main__":
    PyPLANE = QApplication(sys.argv)
    PyPLANE_main_window = MainWindow()
    sys.exit(PyPLANE.exec_())