"""
Draws the main window of the PyPLANE Qt5 interface
"""

import sys
from collections import namedtuple

from PyQt5.QtGui import *
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

from equations import DifferentialEquation, SystemOfEquations
from trajectory import PhaseSpacePlotter
from defaults import psp_by_dimensions, default_1D, default_2D
from errors import *

VERSION = "0.0-pre-alpha"
DEFAULT_DIMS = 2
DEFAULT_PARAM_NUM = 5

ParamEntries = namedtuple("ParamEntries", "names, vals")


class MainWindow(QMainWindow):
    """
    TODO: Insert docstring
    """

    def __init__(self) -> None:
        super().__init__()
        self.init_ui()

    def init_ui(self: QMainWindow) -> None:
        """
        Adds components (buttons, text boxes, etc.) and draws the window
        """

        self.setStyleSheet(open("source/styles.css").read())

        # Define central widget
        cent_widget = QWidget(self)
        self.setCentralWidget(cent_widget)

        # Configuring menu bar
        self.menu_bar()

        # Configuring phase plot
        self.psp_config()

        # Configuring parameter inputs
        self.param_config()

        # Configuring axes limit imputs
        self.axes_lims_config()

        # Configuring plot button
        self.button_config()

        # Configuring equation inputs
        self.equations_config()

        # Final tidy-up and drawing
        inputs_layout = QVBoxLayout()  # All input boxes
        inputs_layout.addLayout(self.equation_entry_layout)

        inputs_layout.addWidget(self.limits_heading)
        inputs_layout.addLayout(self.xlim_layout)
        inputs_layout.addLayout(self.ylim_layout)

        inputs_layout.addLayout(self.parameters_layout)
        inputs_layout.addStretch()

        plot_layout = QVBoxLayout()
        plot_layout.addWidget(NavigationToolbar(self.phase_plot, self))
        plot_layout.addWidget(self.phase_plot)

        self.overall_layout = QHBoxLayout()  # Input boxes and phase plot
        self.overall_layout.addLayout(inputs_layout)
        self.overall_layout.addLayout(plot_layout)

        cent_widget.setLayout(self.overall_layout)

        # Set window title and show
        self.setWindowTitle("PyPLANE " + VERSION)
        self.show()

    def menu_bar(self: QMainWindow) -> None:
        """
        Configures menu bar of main GUI window
        """
        # Menu Bar
        menu_bar = self.menuBar()
        menu_file = menu_bar.addMenu("File")
        menu_edit = menu_bar.addMenu("Edit")

        self.action_new_window = QAction("New Window", self)
        self.action_export_json = QAction("Export JSON", self)
        self.action_import_json = QAction("Import JSON", self)
        self.action_quit = QAction("Quit", self)
        self.action_nullclines = QAction("Plot Nullclines", self, checkable=True)

        menu_file.addAction(self.action_new_window)
        menu_file.addAction(self.action_quit)

        menu_edit.addAction(self.action_export_json)
        menu_edit.addAction(self.action_import_json)
        menu_edit.addAction(self.action_nullclines)

        self.action_quit.triggered.connect(self.close)
        self.action_export_json.triggered.connect(self.gather_system_data)

    def psp_config(self: QMainWindow) -> None:
        """
        Configures GUI for default PSP object
        """
        # Canvas to show the phase plot as part of the main window
        # By default, open application displaying a two dimensional system
        self.psp_canvas_default(DEFAULT_DIMS)

        # Window Features
        self.x_prime_label = QLabel(self.phase_plot.system.system_coords[0] + "' =")
        self.y_prime_label = QLabel(self.phase_plot.system.system_coords[1] + "' =")
        self.x_prime_entry = QLineEdit(self.phase_plot.system.ode_expr_strings[0])
        self.y_prime_entry = QLineEdit(self.phase_plot.system.ode_expr_strings[1])

        # Nullclines are set to toggle with the "Plot Nullclines" menu option
        self.action_nullclines.changed.connect(self.phase_plot.toggle_nullclines)

    def psp_canvas_default(self: QMainWindow, dimensions: int) -> None:
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

    def param_config(self: QMainWindow) -> None:
        """
        """
        self.param_names = [
            QLineEdit(name) for name in list(self.setup_dict["params"].keys())
        ]
        self.param_vals = [
            QLineEdit(str(val)) for val in list(self.setup_dict["params"].values())
        ]

        if len(self.param_names) < DEFAULT_PARAM_NUM:
            self.param_length_padder(self.param_names)
            self.param_length_padder(self.param_vals)

        equals_sign = QLabel("=")
        self.parameters_layout = QVBoxLayout()
        self.parameters_layout.addWidget(QLabel("Parameters (optional)"))

        for name, val in zip(self.param_names, self.param_vals):
            layout = QHBoxLayout()
            layout.addWidget(name)
            layout.addWidget(equals_sign)
            layout.addWidget(val)
            self.parameters_layout.addLayout(layout)

    def param_length_padder(self: QMainWindow, param_list: list) -> list:
        """
        """
        while len(param_list) < DEFAULT_PARAM_NUM:
            param_list.append(QLineEdit())

        return param_list

    def axes_lims_config(self: QMainWindow) -> None:
        """
        """
        self.limits_heading = QLabel("Limits of Axes:")

        self.x_min_label = QLabel(
            "Min " + self.phase_plot.system.system_coords[0] + " ="
        )
        self.x_min_input = QLineEdit(str(self.phase_plot.axes_limits[0][0]))

        self.x_max_label = QLabel(
            "Max " + self.phase_plot.system.system_coords[0] + " ="
        )
        self.x_max_input = QLineEdit(str(self.phase_plot.axes_limits[0][1]))

        self.xlim_layout = QHBoxLayout()
        self.xlim_layout.addWidget(self.x_min_label)
        self.xlim_layout.addWidget(self.x_min_input)
        self.xlim_layout.addWidget(self.x_max_label)
        self.xlim_layout.addWidget(self.x_max_input)

        self.y_min_label = QLabel(
            "Min " + self.phase_plot.system.system_coords[1] + " ="
        )
        self.y_min_input = QLineEdit(str(self.phase_plot.axes_limits[1][0]))

        self.y_max_label = QLabel(
            "Max " + self.phase_plot.system.system_coords[1] + " ="
        )
        self.y_max_input = QLineEdit(str(self.phase_plot.axes_limits[1][1]))

        self.ylim_layout = QHBoxLayout()
        self.ylim_layout.addWidget(self.y_min_label)
        self.ylim_layout.addWidget(self.y_min_input)
        self.ylim_layout.addWidget(self.y_max_label)
        self.ylim_layout.addWidget(self.y_max_input)

    def equations_config(self: QMainWindow) -> None:
        """
        """
        self.x_prime_layout = QHBoxLayout()  # Input box for first equation
        self.y_prime_layout = QHBoxLayout()  # Input box for second equation

        self.x_prime_layout.addWidget(self.x_prime_label)
        self.x_prime_layout.addWidget(self.x_prime_entry)
        self.y_prime_layout.addWidget(self.y_prime_label)
        self.y_prime_layout.addWidget(self.y_prime_entry)

        self.equation_entry_layout = (
            QVBoxLayout()
        )  # Contains input boxes for both eqations
        self.equation_entry_layout.addLayout(self.x_prime_layout)
        self.equation_entry_layout.addLayout(self.y_prime_layout)
        self.equation_entry_layout.addLayout(self.button_layout)

    def button_config(self: QMainWindow) -> None:
        """
        """
        self.plot_button = QPushButton("Plot")
        self.button_layout = QHBoxLayout()
        self.button_layout.addStretch()
        self.button_layout.addWidget(self.plot_button)
        self.button_layout.addStretch()
        # Button Actions
        self.plot_button.clicked.connect(self.plot_button_clicked)

    def plot_button_clicked(self: QMainWindow) -> None:
        """
        Gathers phase_coords and passed_params to feed into GUI checks.
        If GUI checks pass, self.update_psp is called.
        Else, self.handle_empty_entry is called.
        """
        phase_coords = ["x", "y"]

        # Grab parameters
        passed_params = dict(
            zip(
                [name.text() for name in self.param_names if name.text()],
                [value.text() for value in self.param_vals if value.text()],
            )
        )

        try:
            self.update_psp(phase_coords, passed_params)

        except ParameterTypeError as pte:
            print(pte.message)
            self.handle_pte(pte.args)

        except ParameterValidityError as pve:
            print(pve.message)
            self.handle_pve(pve.args)

        except LimitTypeError as lte:
            print(lte.message)
            self.handle_lte(lte.args)

        except LimitMagnitudeError as lme:
            print(lme.message)
            self.handle_lme(lme.args)

        except PPException as ppe:
            print(ppe.message)

        except Exception as e:
            print("Generic Exception caught:")
            print(e)

    def update_psp(self: QMainWindow, phase_coords: list, passed_params: dict) -> None:
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

    def handle_pte(self: QMainWindow, pte_args: tuple) -> None:
        self.plot_button.setProperty("warning-indicator", True)

    def handle_pve(self: QMainWindow, pve_args: tuple) -> None:
        print(pve_args)
        print(type(pve_args))

    def handle_lte(self: QMainWindow, lte_args: tuple) -> None:
        print(lte_args)
        print(type(lte_args))
        self.setStyleSheet("QLabel { background-color: red}")

    def handle_lme(self: QMainWindow, lme_args: tuple) -> None:
        print(lme_args)
        print(type(lme_args))

    def gather_system_data(self: QMainWindow) -> dict:
        """
        Extracts data about the current system from the relevant UI elements,
        storing it in a dict in preparation for exporting to a .json file.
        """
        system_data = dict()

        print("IT WORKS!")
        # return system_data


if __name__ == "__main__":
    PyPLANE = QApplication(sys.argv)
    PyPLANE_main_window = MainWindow()
    sys.exit(PyPLANE.exec_())
