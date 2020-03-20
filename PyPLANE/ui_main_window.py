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

from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar

from PyPLANE.core_info import VERSION
from PyPLANE.equations import DifferentialEquation, SystemOfEquations
from PyPLANE.trajectory import PhaseSpacePlotter
from PyPLANE.defaults import psp_by_dimensions, default_1D, default_2D


class MainWindow(QMainWindow):
    """
    The application's main window.
    Contains sections for inputting a system of equations,
    a matplotlib canvas where the phase space is plotted,
    as well as a menu bar for access to common options.
    """

    def __init__(self) -> None:
        super().__init__()
        self.init_ui()
        self.draw_window()

    def draw_window(self, app_name="PyPLANE", app_version=VERSION) -> None:
        self.setWindowTitle(app_name + " " + app_version)
        self.show()

    def setup_canvas(self) -> None:
        """
        Canvas to show the phase plot as part of the main window
        By default, open application displaying a two dimensional system
        """
        self.default_dims = 2
        self.psp_canvas_default(self.default_dims)

    def draw_menubar(self) -> None:
        """
        Draws the menu bar that appears at the top of the window
        TODO: File > New Window
        """
        menu_bar = self.menuBar()

        # Add menus to the bar
        menu_file = menu_bar.addMenu("File")
        menu_edit = menu_bar.addMenu("Edit")

        # File > Quit
        self.action_quit = QAction("Quit", self)
        menu_file.addAction(self.action_quit)
        self.action_quit.triggered.connect(self.close)

        # Edit > Show Nullclines
        self.action_nullclines = QAction("Show Nullclines", self, checkable=True)
        menu_edit.addAction(self.action_nullclines)
        self.action_nullclines.changed.connect(self.phase_plot.toggle_nullclines)

        # Edit > Show Fixed Points
        self.action_fixed_points = QAction("Show Fixed Points", self, checkable=True)
        menu_edit.addAction(self.action_fixed_points)
        self.action_fixed_points.changed.connect(self.phase_plot.toggle_fixed_points)

    def setup_equation_inputs(self) -> None:
        """
        Draw the labels and widgets to allow inputing
        of equations (Including the plot button)
        """
        self.x_prime_label = QLabel(self.phase_plot.system.system_coords[0] + "' =")
        self.y_prime_label = QLabel(self.phase_plot.system.system_coords[1] + "' =")
        self.x_prime_entry = QLineEdit(self.phase_plot.system.ode_expr_strings[0])
        self.y_prime_entry = QLineEdit(self.phase_plot.system.ode_expr_strings[1])
        self.plot_button = QPushButton("Plot")

        # Action on clicking plot button
        self.plot_button.clicked.connect(self.plot_button_clicked)

    def setup_parameter_inputs(self) -> None:
        """
        Allow user to enter a number of parameters
        """
        param_names = list(self.setup_dict["params"].keys())
        param_vals = list(self.setup_dict["params"].values())

        self.parameter_input_boxes = {}
        self.no_of_params = 5  # Number of user defined parameters
        for param_num in range(self.no_of_params):
            # Fills parameter input boxes with parameter vars and corresponding vals
            if param_num < len(self.setup_dict["params"].keys()):
                self.parameter_input_boxes[
                    "param_" + str(param_num) + "_name"
                ] = QLineEdit(param_names[param_num])
                self.parameter_input_boxes[
                    "param_" + str(param_num) + "_val"
                ] = QLineEdit(str(param_vals[param_num]))
            # Allows for the situation where self.no_of_params > len(self.setup_dict["params"].keys())
            else:
                self.parameter_input_boxes[
                    "param_" + str(param_num) + "_name"
                ] = QLineEdit()
                self.parameter_input_boxes[
                    "param_" + str(param_num) + "_val"
                ] = QLineEdit()

    def setup_limit_inputs(self) -> None:
        """
        Entry boxes for the max and min values to be plotted
        on the x and y axes of the phase plot
        """
        self.limits_heading = QLabel("Limits of Axes:")

        # The x axis
        self.x_max_label = QLabel(
            "Max " + self.phase_plot.system.system_coords[0] + " ="
        )
        self.x_max_input = QLineEdit(str(self.phase_plot.axes_limits[0][1]))
        self.x_min_label = QLabel(
            "Min " + self.phase_plot.system.system_coords[0] + " ="
        )
        self.x_min_input = QLineEdit(str(self.phase_plot.axes_limits[0][0]))

        # And the y axis
        self.y_max_label = QLabel(
            "Max " + self.phase_plot.system.system_coords[1] + " ="
        )
        self.y_max_input = QLineEdit(str(self.phase_plot.axes_limits[1][1]))
        self.y_min_label = QLabel(
            "Min " + self.phase_plot.system.system_coords[1] + " ="
        )
        self.y_min_input = QLineEdit(str(self.phase_plot.axes_limits[1][0]))

    def init_ui(self) -> None:
        """
        Puts together various compnents of the UI
        """

        # Define central widget
        # This will hold all UI elements apart from the menu bar
        cent_widget = QWidget(self)
        self.setCentralWidget(cent_widget)

        # matplotlib canvas which shows the plot
        self.setup_canvas()

        # Menu bar at the top of the window
        self.draw_menubar()

        # Fields to enter values for x' and y' (and a plot button)
        self.setup_equation_inputs()

        # Where the user enter limits for the plot's x and y axes
        self.setup_limit_inputs()

        # These take parameters which can be used in x' and y'
        self.setup_parameter_inputs()

        # Generate layots to arrange UI elements on the window
        # Begin with the equatiom entry boxes
        x_prime_layout = QHBoxLayout()
        x_prime_layout.addWidget(self.x_prime_label)
        x_prime_layout.addWidget(self.x_prime_entry)

        y_prime_layout = QHBoxLayout()
        y_prime_layout.addWidget(self.y_prime_label)
        y_prime_layout.addWidget(self.y_prime_entry)

        # Then do the plot button
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(self.plot_button)
        button_layout.addStretch()

        # Combine these into one layout
        equation_entry_layout = QVBoxLayout()
        equation_entry_layout.addLayout(x_prime_layout)
        equation_entry_layout.addLayout(y_prime_layout)
        equation_entry_layout.addLayout(button_layout)

        # And the axes limit inputs
        xlim_layout = QHBoxLayout()
        xlim_layout.addWidget(self.x_max_label)
        xlim_layout.addWidget(self.x_max_input)
        xlim_layout.addWidget(self.x_min_label)
        xlim_layout.addWidget(self.x_min_input)

        ylim_layout = QHBoxLayout()
        ylim_layout.addWidget(self.y_max_label)
        ylim_layout.addWidget(self.y_max_input)
        ylim_layout.addWidget(self.y_min_label)
        ylim_layout.addWidget(self.y_min_input)

        # Layouts for user-definable parameters
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

        parameters_layout = QVBoxLayout()  # Inputs for all parameters
        parameters_layout.addWidget(QLabel("Parameters (Optional) :"))
        for param_num in range(self.no_of_params):
            parameters_layout.addLayout(
                self.parameter_layouts["param_" + str(param_num) + "_layout"]
            )

        # Combine the system input area into one layout
        inputs_layout = QVBoxLayout()  # All input boxes
        inputs_layout.addLayout(equation_entry_layout)

        inputs_layout.addWidget(self.limits_heading)
        inputs_layout.addLayout(xlim_layout)
        inputs_layout.addLayout(ylim_layout)

        inputs_layout.addLayout(parameters_layout)
        inputs_layout.addStretch()

        # Create a laout to hold the canvas (phase plot) and matplotlib toolbar
        plot_layout = QVBoxLayout()
        plot_layout.addWidget(NavigationToolbar(self.phase_plot, self))
        plot_layout.addWidget(self.phase_plot)

        # Create the final laout, and place on the central widget
        self.overall_layout = QHBoxLayout()  # Input boxes and phase plot
        self.overall_layout.addLayout(inputs_layout)
        self.overall_layout.addLayout(plot_layout)

        cent_widget.setLayout(self.overall_layout)

    def psp_canvas_default(self, dimensions: int) -> None:
        """
        Initialises default PSP
        """
        if dimensions == 1:
            self.setup_dict = default_1D

        elif dimensions == 2:
            self.setup_dict = default_2D

        # Unpacks self.setup_dict into SOE.
        sys = SystemOfEquations(**self.setup_dict)
        self.phase_plot = PhaseSpacePlotter(sys, **self.setup_dict)

    def plot_button_clicked(self) -> None:
        """
        Gathers phase_coords and passed_params to feed into GUI checks.
        If GUI checks pass, self.update_psp is called.
        Else, self.handle_empty_entry is called.
        """
        phase_coords = ["x", "y"]

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

        if self.required_fields_full(phase_coords, passed_params):
            self.update_psp(phase_coords, passed_params)

        else:
            self.handle_empty_entry(phase_coords, passed_params)

    def update_psp(self, phase_coords: list, passed_params: dict) -> None:
        """
        Gathers entry information from GUI and updates phase plot
        """
        f_1 = self.x_prime_entry.text()
        f_2 = self.y_prime_entry.text()
        eqns = [f_1, f_2]

        system_of_eqns = SystemOfEquations(phase_coords, eqns, params=passed_params)

        self.action_nullclines.setChecked(False)

        x_min = float(self.x_min_input.text())
        x_max = float(self.x_max_input.text())
        y_min = float(self.y_min_input.text())
        y_max = float(self.y_max_input.text())

        self.phase_plot.update_system(
            system_of_eqns, axes_limits=((x_min, x_max), (y_min, y_max))
        )

    def handle_empty_entry(self, phase_coords: list, passed_params: dict) -> None:
        print("Blank detected")

    def required_fields_full(self, phase_coords: list, passed_params: dict) -> bool:
        """
        Checks if all of the required entry boxes on the GUI are full and are compatible, where applicable.
        Returns True if all full.
        Returns False if any are empty
        """
        if self.equations_undefined():
            return False

        for var, eqn in zip(
            phase_coords, (self.x_prime_entry.text(), self.y_prime_entry.text())
        ):
            if self.params_undefined(var, phase_coords, eqn, passed_params):
                return False

        return not self.lims_undefined()

    def equations_undefined(self) -> bool:
        """
        Checks if either ODE expression entry boxes are entry. Returns True if either
        are empty. Returns False if both are not empty
        """
        for string_eqn in (self.x_prime_entry.text(), self.y_prime_entry.text()):
            if string_eqn == "":
                return True

        return False

    def params_undefined(
        self, dep_var: str, phase_coords: list, ode_str: str, passed_params: dict,
    ) -> bool:
        """
        Checks for undefined parameters in ODE expressions.
        Returns True if undefined parameters found.
        Returns False otherwise
        """
        for val in passed_params.values():
            try:
                float(val)
            except ValueError:
                return True

        ode = DifferentialEquation(dep_var, phase_coords, ode_str)

        # Currently unused, except to determine that there are undefined params.
        # Could be used later to highlight offending ode expression?
        undefined_params = [
            str(sym) for sym in ode.params if str(sym) not in passed_params.keys()
        ]

        return len(undefined_params) != 0

    def lims_undefined(self) -> bool:
        """
        Checks for undefined axes limits. Returns True if any of the axes limits
        entry boxes are empty or contain non-numerical characters.
        Returns False if all contain text that can be converted to floats.
        """
        for lim in (
            self.x_min_input.text(),
            self.x_max_input.text(),
            self.y_min_input.text(),
            self.y_max_input.text(),
        ):
            if lim == "":
                return True
            try:
                float(lim)
            except ValueError:
                return True
        return False


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app_main_window = MainWindow()
    sys.exit(app.exec_())
