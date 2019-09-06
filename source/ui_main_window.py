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
    QAction,
)


#from ui_default_canvas import DefaultCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar


from equations import SystemOfEquations
from defaults import psp_by_dimensions

VERSION = "0.0-pre-alpha"


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

        # self.action_new_window = QAction("New Window", self)
        self.action_quit = QAction("Quit", self)
        # menu_file.addAction(self.action_new_window)
        menu_file.addAction(self.action_quit)

        self.action_quit.triggered.connect(self.close)

        self.action_nullclines = QAction("Plot Nullclines", self, checkable=True)
        menu_plot_opts.addAction(self.action_nullclines)

        # print(action_nullclines.isChecked())

        # Canvas to show the phase plot as part of the main window
        # By default, open application displaying a two dimensional system
        self.phase_plot = psp_by_dimensions(2)

        # Window Features
        self.x_prime_label = QLabel(self.phase_plot.system.system_coords[0] + " =")
        self.y_prime_label = QLabel(self.phase_plot.system.system_coords[1] + " =")
        self.x_prime_entry = QLineEdit(self.phase_plot.system.ode_expr_strings[0])
        self.y_prime_entry = QLineEdit(self.phase_plot.system.ode_expr_strings[1])
        self.plot_button = QPushButton("Plot")

        # Nullclines are set to toggle with the "Plot Nullclines" menu option
        self.action_nullclines.changed.connect(self.phase_plot.toggle_nullclines)

        # Parameter inputs
        self.parameter_input_boxes = {}
        self.no_of_params = 5  # Number of user defined parameters
        for param_num in range(self.no_of_params):
            self.parameter_input_boxes[
                "param_" + str(param_num) + "_name"
            ] = QLineEdit()
            self.parameter_input_boxes["param_" + str(param_num) + "_val"] = QLineEdit()

        # Axes limit imputs
        self.limits_heading = QLabel("Limits of Axes:")
        self.x_max_label = QLabel(
            "Max " + self.phase_plot.system.system_coords[0] + " ="
        )
        self.x_max_input = QLineEdit(str(self.phase_plot.axes_limits[0][1]))
        self.x_min_label = QLabel(
            "Min " + self.phase_plot.system.system_coords[0] + " ="
        )
        self.x_min_input = QLineEdit(str(self.phase_plot.axes_limits[0][0]))
        xlim_layout = QHBoxLayout()
        xlim_layout.addWidget(self.x_max_label)
        xlim_layout.addWidget(self.x_max_input)
        xlim_layout.addWidget(self.x_min_label)
        xlim_layout.addWidget(self.x_min_input)

        self.y_max_label = QLabel(
            "Max " + self.phase_plot.system.system_coords[1] + " ="
        )
        self.y_max_input = QLineEdit(str(self.phase_plot.axes_limits[1][1]))
        self.y_min_label = QLabel(
            "Min " + self.phase_plot.system.system_coords[1] + " ="
        )
        self.y_min_input = QLineEdit(str(self.phase_plot.axes_limits[1][0]))
        ylim_layout = QHBoxLayout()
        ylim_layout.addWidget(self.y_max_label)
        ylim_layout.addWidget(self.y_max_input)
        ylim_layout.addWidget(self.y_min_label)
        ylim_layout.addWidget(self.y_min_input)

        # Layouts
        x_prime_layout = QHBoxLayout()  # Input box for first equation
        y_prime_layout = QHBoxLayout()  # Input box for second equation
        button_layout = QHBoxLayout()

        self.parameter_layouts = (
            {}
        )  # Each layout contains two input boxes (parameter name and value) and an equals sign
        for param_num in range(self.no_of_params):
            self.parameter_layouts[
                "param_" + str(param_num) + "_layout"
            ] = QHBoxLayout()
            self.equals_sign = QLabel("=")
            self.parameter_layouts["param_" + str(param_num) + "_layout"].addWidget(
                self.parameter_input_boxes["param_" + str(param_num) + "_name"]
            )
            self.parameter_layouts["param_" + str(param_num) + "_layout"].addWidget(
                self.equals_sign
            )
            self.parameter_layouts["param_" + str(param_num) + "_layout"].addWidget(
                self.parameter_input_boxes["param_" + str(param_num) + "_val"]
            )

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
            parameters_layout.addLayout(
                self.parameter_layouts["param_" + str(param_num) + "_layout"]
            )

        inputs_layout = QVBoxLayout()  # All input boxes
        inputs_layout.addLayout(equation_entry_layout)

        inputs_layout.addWidget(self.limits_heading)
        inputs_layout.addLayout(xlim_layout)
        inputs_layout.addLayout(ylim_layout)

        inputs_layout.addLayout(parameters_layout)
        inputs_layout.addStretch()

        plot_layout = QVBoxLayout()
        plot_layout.addWidget(NavigationToolbar(self.phase_plot, self))
        plot_layout.addWidget(self.phase_plot)

        self.overall_layout = QHBoxLayout()  # Input boxes and phase plot
        self.overall_layout.addLayout(inputs_layout)
        self.overall_layout.addLayout(plot_layout)

        cent_widget.setLayout(self.overall_layout)

        # Button Actions
        self.plot_button.clicked.connect(self.plot_button_clicked)

        # Set window title and show
        self.setWindowTitle("PyPLANE " + VERSION)
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
            if self.parameter_input_boxes["param_" + str(param_num) + "_name"].text():
                passed_params[
                    self.parameter_input_boxes[
                        "param_" + str(param_num) + "_name"
                    ].text()
                ] = float(
                    self.parameter_input_boxes[
                        "param_" + str(param_num) + "_val"
                    ].text()
                )

        system_of_eqns = SystemOfEquations(phase_coords, eqns, params=passed_params)

        self.action_nullclines.setChecked(False)

        x_min = float(self.x_min_input.text())
        x_max = float(self.x_max_input.text())
        y_min = float(self.y_min_input.text())
        y_max = float(self.y_max_input.text())

        self.phase_plot.update_system(
            system_of_eqns, axes_limits=((x_min, x_max), (y_min, y_max))
        )


if __name__ == "__main__":
    PyPLANE = QApplication(sys.argv)
    PyPLANE_main_window = MainWindow()
    sys.exit(PyPLANE.exec_())
