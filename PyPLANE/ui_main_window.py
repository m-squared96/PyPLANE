"""
Draws the main window of the PyPLANE Qt5 interface
"""

import sys
import os
import functools
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
    QWidgetAction,
    QComboBox,
    QMenu,
    QMessageBox,
)

from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar

from PyPLANE.core_info import VERSION
from PyPLANE.equations import DifferentialEquation, SystemOfEquations
from PyPLANE.trajectory import PhaseSpace1D, PhaseSpace2D
from PyPLANE.gallery import Gallery
from PyPLANE.defaults import psp_by_dimensions


class MainWindow(QMainWindow):
    """
    The application's main window.
    Contains sections for inputting a system of equations,
    a matplotlib canvas where the phase space is plotted,
    as well as a menu bar for access to common options.
    """

    def __init__(self) -> None:
        super().__init__()

        # Working directory changed so that resources can be loaded
        main_window_file_path = os.path.abspath(__file__)
        main_window_file_dir = os.path.dirname(main_window_file_path)
        os.chdir(main_window_file_dir)
        self.working_dir = main_window_file_dir
        print("New working directory: {}".format(self.working_dir))

        self.load_gallery("resources/gallery_2D.json", "gallery_2D", 2)
        self.load_gallery("resources/gallery_1D.json", "gallery_1D", 1)
        self.show_2D()
        self.draw_window()

    def load_gallery(self, filename: str, gallery_name: str, num_dims: int) -> None:
        setattr(self, gallery_name, Gallery(filename, num_dims))

    def draw_window(self, app_name="PyPLANE", app_version=VERSION) -> None:
        self.setWindowTitle(app_name + " " + app_version)
        self.show()

    def basic_popup(
            self, 
            icon=QMessageBox.Information, 
            button=QMessageBox.Ok,
            text="Pop-Up"
        ):
        """
        Basic pop-up window facility. Displays pop-up which grabs screen's attention.

        icon -> Icon displayed in top-left corner. Can take the following values:
            - QMessageBox.Critical
            - QMessageBox.Warning
            - QMessageBox.Information
            - QMessageBox.Question

        button -> Button displayed on bottom of pop-up. Can take the following values:
            - QMessageBox.Ok
            - QMessageBox.Open
            - QMessageBox.Save
            - QMessageBox.Cancel
            - QMessageBox.Close
            - QMessageBox.Yes
            - QMessageBox.No
            - QMessageBox.Abort
            - QMessageBox.Retry
            - QMessageBox.Ignore

        text -> Main message of pop-up
        """

        msg = QMessageBox()
        msg.setWindowTitle("PyPLANE")
        msg.setText(text)
        
        # If a non-permitted icon value passed -> default to info
        try:
            msg.setIcon(icon)
        except:
            msg.setIcon(QMessageBox.Information)
            
        # If a non-permitted button value passed -> default to OK
        try:
            msg.setStandardButtons(button)
        except:
            msg.setStandardButtons(QMessageBox.Ok)

        # Show pop-up
        msg.exec_()

    def draw_menubar(self) -> None:
        """
        Draws the menu bar that appears at the top of the window. If method is recalled, existing menu bar
        is cleared and redrawn.
        TODO: File > New Window
        """

        menu_bar = self.menuBar()
        menu_bar.clear()  # If menu_bar already exists, clears and redraws.

        # Add menus to the bar
        self.menu_file = menu_bar.addMenu("File")
        self.menu_edit = menu_bar.addMenu("Edit")
        self.menu_dims = menu_bar.addMenu("Dimensions")
        self.menu_gallery = menu_bar.addMenu("Gallery")

        # File > Quit
        self.action_quit = QAction("Quit", self)
        self.menu_file.addAction(self.action_quit)
        self.action_quit.triggered.connect(self.close)

        # Edit > Show Nullclines
        self.action_nullclines = QAction("Show Nullclines", self, checkable=True)
        self.menu_edit.addAction(self.action_nullclines)
        self.action_nullclines.changed.connect(self.phase_plot.toggle_nullclines)

        # Edit > Show Fixed Points
        self.action_fixed_points = QAction("Show Fixed Points", self, checkable=True)
        self.menu_edit.addAction(self.action_fixed_points)
        self.action_fixed_points.changed.connect(self.phase_plot.toggle_fixed_points)

        # Dimensions > 1D
        self.action_1D = QAction("One-Dimensional PyPLANE", self)
        self.menu_dims.addAction(self.action_1D)
        self.action_1D.triggered.connect(self.show_1D)

        # Dimensions > 2D
        self.action_2D = QAction("Two-Dimensional PyPLANE", self)
        self.menu_dims.addAction(self.action_2D)
        self.action_2D.triggered.connect(self.show_2D)

        # Gallery
        self.create_gallery_menu("gallery_1D", "One-Dimensional", 1)
        self.create_gallery_menu("gallery_2D", "Two-Dimensional", 2)

    def create_gallery_menu(
        self, gallery_name: str, submenu_name: str, num_dims: int
    ) -> None:
        gallery_menu = self.menu_gallery.addMenu(submenu_name)
        gallery_actions = []
        gallery = getattr(self, gallery_name)

        for system in gallery:
            gall_item_action = QAction(system["system_name"], self)
            plot_sys_func = functools.partial(self.plot_gallery_item, system, num_dims)
            gall_item_action.triggered.connect(plot_sys_func)
            gallery_menu.addAction(gall_item_action)
            gallery_actions.append(gall_item_action)

        setattr(self, "menu_" + gallery_name, gallery_menu)
        setattr(self, "actions_" + gallery_name, gallery_actions)

    def handle_empty_entry(self, phase_coords: list, passed_params: dict) -> None:
        self.basic_popup(
            icon=QMessageBox.Warning,
            button=QMessageBox.Ok,
            text="Blank detected"
        )

    def required_fields_full(self, phase_coords: list, passed_params: dict) -> bool:
        """
        Checks if all of the required entry boxes on the GUI are full and are compatible, where applicable.
        Returns True if all full.
        Returns False if any are empty
        """
        if self.equations_undefined():
            return False

        for var, eqn in zip(phase_coords, self.eqn_entries):
            if self.params_undefined(var, phase_coords, eqn, passed_params):
                return False

        return not self.lims_undefined()

    def equations_undefined(self) -> bool:
        """
        Checks if either ODE expression entry boxes are entry. Returns True if either
        are empty. Returns False if both are not empty
        """
        for string_eqn in self.eqn_entries:
            if string_eqn == "":
                return True

        return False

    def params_undefined(
        self, dep_var: str, phase_coords: list, ode_str: str, passed_params: dict
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
        for lim in self.lim_entries:
            if lim == "":
                return True
            try:
                float(lim)
            except ValueError:
                return True
        return False

    def show_1D(self) -> None:
        self.active_dims = 1
        self.init_ui()

    def show_2D(self) -> None:
        self.active_dims = 2
        self.init_ui()

    def show_ND(self, num_dims: int) -> None:
        show_ND_funcs = {1: self.show_1D, 2: self.show_2D}
        try:
            if self.active_dims != num_dims:
                show_ND_funcs[num_dims]()
        except KeyError:
            raise ValueError("Trying to set to an unsupported number of dimensions")

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

    def setup_equation_inputs(self) -> None:
        """
        Draw the labels and widgets to allow inputing
        of equations (Including the plot button)
        """
        self.x_prime_label = QLabel(self.phase_plot.system.system_coords[0] + "' =")
        self.x_prime_entry = QLineEdit(self.phase_plot.system.ode_expr_strings[0])

        if self.active_dims == 2:
            self.y_prime_label = QLabel(self.phase_plot.system.system_coords[1] + "' =")
            self.y_prime_entry = QLineEdit(self.phase_plot.system.ode_expr_strings[1])

        self.plot_button = QPushButton("Plot")

        # Action on clicking plot button
        self.plot_button.clicked.connect(self.plot_button_clicked)

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

        if self.active_dims == 2:
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
        self.psp_canvas_default()

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

        if self.active_dims == 2:
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

        if self.active_dims == 2:
            equation_entry_layout.addLayout(y_prime_layout)

        equation_entry_layout.addLayout(button_layout)

        # And the axes limit inputs
        xlim_layout = QHBoxLayout()
        xlim_layout.addWidget(self.x_max_label)
        xlim_layout.addWidget(self.x_max_input)
        xlim_layout.addWidget(self.x_min_label)
        xlim_layout.addWidget(self.x_min_input)

        if self.active_dims == 2:
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

        if self.active_dims == 2:
            inputs_layout.addLayout(ylim_layout)

        inputs_layout.addLayout(parameters_layout)
        inputs_layout.addStretch()

        # Create a laout to hold the canvas (phase plot) and matplotlib toolbar
        plot_layout = QVBoxLayout()
        plot_layout.addWidget(NavigationToolbar(self.phase_plot, self))

        try:
            plot_layout.removeWidget(self.phase_plot)
        except AttributeError:
            pass

        plot_layout.addWidget(self.phase_plot)

        # Create the final laout, and place on the central widget
        self.overall_layout = QHBoxLayout()  # Input boxes and phase plot
        self.overall_layout.addLayout(inputs_layout)
        self.overall_layout.addLayout(plot_layout)

        cent_widget.setLayout(self.overall_layout)

    def psp_canvas_default(self) -> None:
        """
        Initialises default PSP
        """

        self.setup_dict = psp_by_dimensions(self.active_dims)
        if self.active_dims == 1:
            correct_phase_space = PhaseSpace1D
        elif self.active_dims == 2:
            correct_phase_space = PhaseSpace2D

        # Unpacks self.setup_dict into SOE.
        sys = SystemOfEquations(**self.setup_dict)
        self.phase_plot = correct_phase_space(sys, **self.setup_dict)

    def plot_button_clicked(self) -> None:
        """
        Gathers phase_coords and passed_params to feed into GUI checks.
        If GUI checks pass, self.update_psp is called.
        Else, self.handle_empty_entry is called.
        """

        if self.active_dims == 1:
            phase_coords = ["x"]
        elif self.active_dims == 2:
            phase_coords = ["x", "y"]

        # Grab parameters
        passed_params = {}
        for param_num in range(self.no_of_params):
            if self.parameter_input_boxes["param_" + str(param_num) + "_name"].text():
                # For scenario where parameter label is entered but given no value
                # Cannot convert empty string to float
                try:
                    passed_params[
                        self.parameter_input_boxes[
                            "param_" + str(param_num) + "_name"
                        ].text()
                    ] = float(
                        self.parameter_input_boxes[
                            "param_" + str(param_num) + "_val"
                        ].text()
                    )

                # This will then be passed to DE object and rejected gracefully
                except:
                    passed_params[
                        self.parameter_input_boxes[
                            "param_" + str(param_num) + "_name"
                        ].text()
                    ] = str(
                        self.parameter_input_boxes[
                            "param_" + str(param_num) + "_val"
                        ].text()
                    )

        if self.active_dims == 1:
            self.eqn_entries = [self.x_prime_entry.text()]
            self.lim_entries = [self.x_min_input.text(), self.x_max_input.text()]

        elif self.active_dims == 2:
            self.eqn_entries = [self.x_prime_entry.text(), self.y_prime_entry.text()]
            self.lim_entries = [
                self.x_min_input.text(),
                self.x_max_input.text(),
                self.y_min_input.text(),
                self.y_max_input.text(),
            ]

        if self.required_fields_full(phase_coords, passed_params):
            self.update_psp(phase_coords, passed_params)

        else:
            self.handle_empty_entry(phase_coords, passed_params)

    def solve_method_changed(self) -> None:
        self.solve_method = self.solve_method_combo.currentText()
        self.phase_plot.system.set_solve_method(self.solve_method)

    def update_psp(self, phase_coords: list, passed_params: dict) -> None:
        """
        Gathers entry information from GUI and updates phase plot
        """
        f_1 = self.x_prime_entry.text()
        f_2 = None
        eqns = [f_1]

        if self.active_dims == 2:
            f_2 = self.y_prime_entry.text()
            eqns.append(f_2)

        system_of_eqns = SystemOfEquations(phase_coords, eqns, params=passed_params)

        self.action_nullclines.setChecked(False)
        lim_floats = [float(lim) for lim in self.lim_entries]

        if self.active_dims == 1:
            axes_limits = ((-5, 5), (lim_floats[0], lim_floats[1]))

        elif self.active_dims == 2:
            axes_limits = (
                (lim_floats[0], lim_floats[1]),
                (lim_floats[2], lim_floats[3]),
            )

        self.phase_plot.init_space(
            system_of_eqns, axes_limits=axes_limits, axes_points=20
        )

    def clear_param_inputs(self) -> None:
        for i in range(self.no_of_params):
            param_name_key = "param_{}_name".format(i)
            param_val_key = "param_{}_val".format(i)
            self.parameter_input_boxes[param_name_key].setText("")
            self.parameter_input_boxes[param_val_key].setText("")

    def clear_equation_inputs(self) -> None:
        self.x_prime_entry.setText("")
        if self.active_dims == 2:
            self.y_prime_entry.setText("")

    def clear_limits_inputs(self) -> None:
        self.x_max_input.setText("")
        self.x_min_input.setText("")

        if self.active_dims == 2:
            self.y_max_input.setText("")
            self.y_min_input.setText("")

    def clear_all_inputs(self) -> None:
        self.clear_equation_inputs()
        self.clear_limits_inputs()
        self.clear_param_inputs()

    def plot_gallery_item(self, system: SystemOfEquations, num_dims: int) -> None:
        print("Plotting system - {}".format(system))

        self.show_ND(num_dims)

        self.clear_all_inputs()

        # Equations
        system_equations = system["ode_expr_strings"]
        x_prime_equation = system_equations[0]
        self.x_prime_entry.setText(x_prime_equation)
        if self.active_dims == 2:
            y_prime_equation = system_equations[1]
            self.y_prime_entry.setText(y_prime_equation)

        # Limits
        axes_limits = system["axes_limits"]
        x_min, x_max = [str(lim) for lim in axes_limits[0]]
        y_min, y_max = [str(lim) for lim in axes_limits[1]]
        self.x_max_input.setText(x_max)
        self.x_min_input.setText(x_min)

        if self.active_dims == 2:
            self.y_max_input.setText(y_max)
            self.y_min_input.setText(y_min)

        # Parameters
        sys_name = system["system_name"]
        print("Plotting", sys_name)
        sys_params = system["params"]
        param_names = list(sys_params.keys())
        num_sys_params = len(param_names)

        for param_num in range(num_sys_params):
            param_name = str(param_names[param_num])
            param_val = str(sys_params[param_name])

            param_name_key = "param_{}_name".format(param_num)
            param_val_key = "param_{}_val".format(param_num)
            self.parameter_input_boxes[param_name_key].setText(param_name)
            self.parameter_input_boxes[param_val_key].setText(param_val)

        self.plot_button_clicked()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app_main_window = MainWindow()
    sys.exit(app.exec_())
