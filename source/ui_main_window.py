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
    QHBoxLayout,
    QAction
)

from ui_default_canvas import DefaultCanvas

from equations import SystemOfEquations

VERSION = "0.0-pre-apha"


class MainWindow(QMainWindow):
    """
    TODO: Insert docstring
    """

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self: QMainWindow) -> None:
        """
        Adds components (buttons, text boxes, etc.) and draws the window
        """

        # Define central widget
        cent_widget = QWidget(self)
        self.setCentralWidget(cent_widget)

        # Menu Bar
        menu_bar = self.menuBar()
        menu_file = menu_bar.addMenu("File")
        menu_edit = menu_bar.addMenu("Edit")
        menu_plot_opts = menu_edit.addMenu("Plot Options")

        self.action_new_window = QAction("New Window", self)
        self.action_quit = QAction("Quit", self)
        menu_file.addAction(self.action_new_window)
        menu_file.addAction(self.action_quit)

        self.action_nullclines = QAction("Plot Nullclines", self, checkable=True)
        self.action_nullclines.setChecked(True)
        menu_plot_opts.addAction(self.action_nullclines)

        #print(action_nullclines.isChecked())

        # Window Features
        self.x_prime_label = QLabel("x' =")
        self.y_prime_label = QLabel("y' =")
        self.x_prime_entry = QLineEdit("y*sin(x)")
        self.y_prime_entry = QLineEdit("-x")
        self.plot_button = QPushButton("Plot")

        # Canvas to show the phase plot as part of the main window
        self.phase_plot = DefaultCanvas()
        self.phase_plot.update_system(self.phase_plot.default_system)

        # Parameter inputs
        self.parameter_input_boxes = {}
        self.no_of_params = 5 # Number of user defined parameters
        for param_num in range(self.no_of_params):
            self.parameter_input_boxes["param_"+str(param_num)+"_name"] = QLineEdit()
            self.parameter_input_boxes["param_"+str(param_num)+"_val"] = QLineEdit()

        # Layouts
        x_prime_layout = QHBoxLayout() # Input box for first equation
        y_prime_layout = QHBoxLayout() # Input box for second equation
        button_layout = QHBoxLayout()

        self.parameter_layouts = {} # Each layout contains two input boxes (parameter name and value) and an equals sign
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

        equation_entry_layout = QVBoxLayout()  # Contains input boxes for both eqations
        equation_entry_layout.addLayout(x_prime_layout)
        equation_entry_layout.addLayout(y_prime_layout)
        equation_entry_layout.addLayout(button_layout)

        parameters_layout = QVBoxLayout()  # Inputs for all parameters
        parameters_layout.addWidget(QLabel("Parameters (Optional) :"))
        for param_num in range(self.no_of_params):
            parameters_layout.addLayout(self.parameter_layouts["param_"+str(param_num)+"_layout"])

        inputs_layout = QVBoxLayout()  # All input boxes
        inputs_layout.addLayout(equation_entry_layout)
        inputs_layout.addLayout(parameters_layout)
        inputs_layout.addStretch()

        overall_layout = QHBoxLayout()  # Input boxes and phase plot
        overall_layout.addLayout(inputs_layout)
        overall_layout.addWidget(self.phase_plot)

        cent_widget.setLayout(overall_layout)

        # Button Actions
        self.plot_button.clicked.connect(self.plot_button_clicked)

        # Set window title and show
        self.setWindowTitle("PyPLANE "+VERSION)
        self.show()

    def plot_button_clicked(self: QMainWindow) -> None:
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

        system_of_eqns = SystemOfEquations(phase_coords, eqns, params=passed_params)
        
        if self.action_nullclines.isChecked() == True:
            self.phase_plot.update_system(system_of_eqns)
        else:
            print("Nullclines false not yet implemented")


if __name__ == "__main__":
    PyPLANE = QApplication(sys.argv)
    PyPLANE_main_window = MainWindow()
    sys.exit(PyPLANE.exec_())
