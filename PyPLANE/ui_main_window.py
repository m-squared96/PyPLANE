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
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QAction,
    QWidgetAction,
    QComboBox,
    QMenu,
    QMessageBox,
    QListWidget,
    QListWidgetItem,
    QAbstractItemView,
    QScrollBar,
    QCheckBox,
    QRadioButton,
)
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from mpl_toolkits.mplot3d import Axes3D

from PyPLANE.core_info import VERSION
from PyPLANE.equations import DifferentialEquation, SystemOfEquations
from PyPLANE.trajectory import PhaseSpace1D, PhaseSpace2D
from PyPLANE.gallery import Gallery
from PyPLANE.defaults import psp_by_dimensions
from PyPLANE.analysis import TCAWindow
from PyPLANE.ui_layouts import (
    EquationEntryLayout,
    ParameterEntryLayout,
    AxisLimitEntryLayout,
)


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
        self.menu_analysis = menu_bar.addMenu("Analysis")
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

        # Analysis
        self.action_tca = QAction("Trajectory Component Analysis", self)
        self.menu_analysis.addAction(self.action_tca)
        self.action_tca.triggered.connect(self.tca_init)

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

    def tca_init(self) -> None:

        if self.phase_plot.system.dims == 1:
            self.handle_tca_dim_error()
            return

        self.phase_plot.toggle_annotation()

        #if self.tca_window is None:
        self.tca_window = TCAWindow(self.phase_plot.trajectories)
        self.tca_window.show()

        #self.phase_plot.toggle_annotation()

    def handle_tca_dim_error(self) -> None:
        self.basic_popup(
            icon=QMessageBox.Warning,
            button=QMessageBox.Ok,
            text="Trajectory component analysis only available for 2D systems"
        )

    def handle_tca_null_error(self) -> None:
        self.basic_popup(
            icon=QMessageBox.Warning,
            button=QMessageBox.Ok,
            text="Trajectories must be plotted before TCA can occur"
        )

    def handle_empty_entry(self, phase_coords: list, passed_params: dict) -> None:
        self.basic_popup(
            icon=QMessageBox.Warning,
            button=QMessageBox.Ok,
            text="Blank detected"
        )

    def handle_invalid_eqns(self) -> None:
        
        warning = """
            Equation string should not contain the following symbols:
             I, E, S, N, C, O, or Q
        """

        self.basic_popup(
            icon=QMessageBox.Warning,
            button=QMessageBox.Ok,
            text=warning
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

    def init_equation_layouts(self) -> None:
        """
        Draw the labels and widgets to allow inputing
        of equations (Including the plot button)
        """
        self.equation_entry_layout = QVBoxLayout()

        var1_name = self.phase_plot.system.system_coords[0]
        var1_equation = self.phase_plot.system.ode_expr_strings[0]
        self.var1_equation_layout = EquationEntryLayout(var1_name, var1_equation)
        self.equation_entry_layout.addLayout(self.var1_equation_layout)

        if self.active_dims == 2:
            var2_name = self.phase_plot.system.system_coords[1]
            var2_equation = self.phase_plot.system.ode_expr_strings[1]
            self.var2_equation_layout = EquationEntryLayout(var2_name, var2_equation)
            self.equation_entry_layout.addLayout(self.var2_equation_layout)

    def init_plot_button_layout(self) -> None:
        self.plot_button = QPushButton("Plot")
        self.plot_button.clicked.connect(self.plot_button_clicked)
        self.button_layout = QHBoxLayout()
        self.button_layout.addStretch()
        self.button_layout.addWidget(self.plot_button)
        self.button_layout.addStretch()

    def init_limit_layouts(self) -> None:
        """
        Entry boxes for the max and min values to be plotted
        on the x and y axes of the phase plot
        """
        self.lim_layout = QVBoxLayout()
        self.lim_layout.addWidget(QLabel("Limits of Axes:"))
        
        var1_name = self.phase_plot.system.system_coords[0]
        var1_max_val = self.phase_plot.axes_limits[0][1]
        var1_min_val = self.phase_plot.axes_limits[0][0]
        self.var1_lim_layout = AxisLimitEntryLayout(var1_name, var1_min_val,
                                                    var1_max_val)
        self.lim_layout.addLayout(self.var1_lim_layout)
        
        if self.active_dims == 2:
            var2_name = self.phase_plot.system.system_coords[1]
            var2_max_val = self.phase_plot.axes_limits[1][1]
            var2_min_val = self.phase_plot.axes_limits[1][0]
            self.var2_lim_layout = AxisLimitEntryLayout(var2_name, var2_min_val,
                                                        var2_max_val)
            self.lim_layout.addLayout(self.var2_lim_layout)

    def init_param_layouts(self) -> None:
        """
        Entry boxes for the names and values of the SOE parameters.
        """
        soe_params = self.setup_dict["params"]
        min_num_param_inputs = 5
        num_params = len(soe_params)
        self.num_param_inputs = max(min_num_param_inputs, num_params)

        self.parameters_layout = QVBoxLayout()
        self.parameters_layout.addWidget(QLabel("Parameters (Optional) :"))
        for name, val in soe_params.items():
            self.parameters_layout.addLayout(ParameterEntryLayout(name, val))

        num_empty_param_inputs = max(0, min_num_param_inputs - num_params)
        for i in range(num_empty_param_inputs):
            self.parameters_layout.addLayout(ParameterEntryLayout())

    def combine_input_layouts(self) -> None:
        self.inputs_layout = QVBoxLayout()  # All input boxes
        self.inputs_layout.addLayout(self.equation_entry_layout)
        self.inputs_layout.addLayout(self.button_layout)
        self.inputs_layout.addLayout(self.lim_layout)
        self.inputs_layout.addLayout(self.parameters_layout)
        self.inputs_layout.addStretch()

    def init_ui(self) -> None:
        """
        Puts together various compnents of the UI
        """
        # This will hold all UI elements apart from the menu bar
        self.cent_widget = QWidget(self)
        self.setCentralWidget(self.cent_widget)
        self.psp_canvas_default()
        self.draw_menubar()

        self.init_equation_layouts()
        self.init_plot_button_layout()
        self.init_limit_layouts()
        self.init_param_layouts()
        self.combine_input_layouts()

        plot_layout = QVBoxLayout()
        plot_layout.addWidget(NavigationToolbar(self.phase_plot, self))

        try:
            plot_layout.removeWidget(self.phase_plot)
        except AttributeError:
            pass

        plot_layout.addWidget(self.phase_plot)

        self.overall_layout = QHBoxLayout()
        self.overall_layout.addLayout(self.inputs_layout)
        self.overall_layout.addLayout(plot_layout)

        self.cent_widget.setLayout(self.overall_layout)

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

    def equations_valid(self, equations: list) -> bool:
        """
        Parses equation inputs and checks for invalid/disallowed symbols.
        Returns True if equation contains no offending characters.
        
        List of disallowed symbols can be found in the SymPy docs:
        https://docs.sympy.org/latest/gotchas.html
        """
        disallowed_symbols = ("I","E","S","N","C","O","Q")
        
        for eqn in equations:
            for sym in disallowed_symbols:
                if eqn.find(sym) != -1:
                    return False

        return True

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
        for param_layout in self.parameters_layout.children():
            param_name = param_layout.param_name_text()
            param_val = param_layout.param_val_text()
            if param_name:
                try:
                    # For scenario where parameter label is entered but given no value
                    # Cannot convert empty string to float
                    param_val = float(param_val)
                except ValueError:
                    pass
                # This will then be passed to DE object and rejected gracefully
                passed_params[param_name] = param_val

        self.eqn_entries = [self.var1_equation_layout.text()]
        self.lim_entries = [
            self.var1_lim_layout.min_val_text(),
            self.var1_lim_layout.max_val_text()
        ]

        if self.active_dims == 2:
            self.eqn_entries.append(self.var2_equation_layout.text())
            self.lim_entries.extend([
                self.var2_lim_layout.min_val_text(),
                self.var2_lim_layout.max_val_text()
            ])

        if not self.required_fields_full(phase_coords, passed_params):
            self.handle_empty_entry(phase_coords, passed_params)

        elif not self.equations_valid(self.eqn_entries):
            self.handle_invalid_eqns()

        else:
            self.update_psp(phase_coords, passed_params)

    def solve_method_changed(self) -> None:
        self.solve_method = self.solve_method_combo.currentText()
        self.phase_plot.system.set_solve_method(self.solve_method)

    def update_psp(self, phase_coords: list, passed_params: dict) -> None:
        """
        Gathers entry information from GUI and updates phase plot
        """
        f_1 = self.var1_equation_layout.text()
        eqns = [f_1]

        if self.active_dims == 2:
            f_2 = self.var2_equation_layout.text()
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
        for param_layout in self.parameters_layout.children():
            param_layout.clear()

    def clear_equation_inputs(self) -> None:
        self.var1_equation_layout.clear()
        if self.active_dims == 2:
            self.var2_equation_layout.clear()

    def clear_limits_inputs(self) -> None:
        self.var1_lim_layout.clear()
        if self.active_dims == 2:
            self.var2_lim_layout.clear()

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
        var1_equation = system_equations[0]
        self.var1_equation_layout.set_text(var1_equation)
        if self.active_dims == 2:
            var2_equation = system_equations[1]
            self.var2_equation_layout.set_text(var2_equation)

        # Limits
        axes_limits = system["axes_limits"]
        self.var1_lim_layout.set_min_max_text(*axes_limits[0])

        if self.active_dims == 2:
            self.var2_lim_layout.set_min_max_text(*axes_limits[1])

        # Parameters
        sys_name = system["system_name"]
        print("Plotting", sys_name)
        sys_params = system["params"]
        param_names = list(sys_params.keys())
        num_sys_params = len(param_names)

        # This loop assumes that the number of system params is fewer than
        # the number of parameter layouts. TODO: fix that.
        for param_num in range(num_sys_params):
            param_name = str(param_names[param_num])
            param_val = str(sys_params[param_name])
            param_layout = self.parameters_layout.children()[param_num]
            param_layout.set_name_val_text(param_name, param_val)

        self.plot_button_clicked()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app_main_window = MainWindow()
    sys.exit(app.exec_())
