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


class TCAWindow(QWidget):
    """
    Selection menu consisting of candidate trajectories for TCA.
    """
    def __init__(self, traj_dict) -> None:
        super().__init__()

        self.tvsx = True
        self.tvsy = False
        self.tvsxvsy = False

        self.plot_separately = True
        self.plot_together = False

        # Define layout and widgets
        self.layout = QVBoxLayout()

        # Listbox for selection of curves
        self.listwidget_label = QLabel().setText("Select curves for analysis")

        self.listwidget = QListWidget() # List widget for selecting trajectories
        self.listwidget.setGeometry(50, 70, 150, 80) 
        self.listwidget.setSelectionMode(QAbstractItemView.MultiSelection)
        scroll_bar = QScrollBar(self)
        self.listwidget.setVerticalScrollBar(scroll_bar)
        #self.listwidget.addPermanentWidget(self.listwidget_label)

        self.traj_dict = traj_dict
        self.list_traj()

        # Tickboxes (AKA checkboxes) for components
        self.tickbox_label = QLabel().setText("Select components for analysis")

        self.component_tickbox_layout = QHBoxLayout()

        self.tickbox_tvsx = QCheckBox("t vs x(t)",self)
        self.tickbox_tvsx.setChecked(True)
        self.tickbox_tvsx.stateChanged.connect(self.toggle_tvsx)

        self.tickbox_tvsy = QCheckBox("t vs y(t)",self)
        self.tickbox_tvsy.stateChanged.connect(self.toggle_tvsy)

        self.tickbox_tvsxvsy = QCheckBox("t vs x(t) vs y(t)",self)
        self.tickbox_tvsxvsy.stateChanged.connect(self.toggle_tvsxvsy)

        self.component_tickbox_layout.addWidget(self.tickbox_tvsx)
        self.component_tickbox_layout.addWidget(self.tickbox_tvsy)
        self.component_tickbox_layout.addWidget(self.tickbox_tvsxvsy)

        # Radio buttons for plotting method
        self.radiobutton_label = QLabel().setText("Plot components together or separately")

        self.plotting_method_layout = QHBoxLayout()

        self.radiobutton_sep = QRadioButton("Separately", self)
        self.radiobutton_sep.setChecked(True)
        self.radiobutton_sep.toggled.connect(self.toggle_method_sep)

        self.radiobutton_tog = QRadioButton("Together", self)
        self.radiobutton_tog.setChecked(False)
        self.radiobutton_tog.toggled.connect(self.toggle_method_tog)

        self.plotting_method_layout.addWidget(self.radiobutton_sep)
        self.plotting_method_layout.addWidget(self.radiobutton_tog)
        
        # Big ol' plot button
        self.plot_button = QPushButton("Plot", self)
        self.plot_button.clicked.connect(self.plot_button_clicked)

        # Tying everything up
        #self.layout.addWidget(self.listwidget_label)
        self.layout.addWidget(self.listwidget)

        #self.layout.addWidget(self.tickbox_label)
        self.layout.addLayout(self.component_tickbox_layout)

        #self.layout.addWidget(self.radiobutton_label)
        self.layout.addLayout(self.plotting_method_layout)

        self.layout.addWidget(self.plot_button)

        self.setLayout(self.layout)

    def list_traj(self) -> None:
        """
        Add trajectories to list widget
        """
        keys = tuple(self.traj_dict.keys())

        for k in keys:
            item = QListWidgetItem("Curve " + str(k))
            self.listwidget.addItem(item)

    def toggle_tvsx(self):
        self.tvsx = not(self.tvsx)

    def toggle_tvsy(self):
        self.tvsy = not(self.tvsy)

    def toggle_tvsxvsy(self):
        self.tvsxvsy = not(self.tvsxvsy)

    def toggle_method_sep(self) -> None:
        self.plot_separately = True
        self.plot_together = False

    def toggle_method_tog(self) -> None:
        self.plot_separately = False
        self.plot_together = True

    def plot_button_clicked(self) -> None:
        curves = [int(i.text().replace("Curve ", "")) 
                for i in self.listwidget.selectedItems()]
        
        self.tca_graphs(curves)

        #self.close()

    def tca_graphs(self, curves: list) -> None:
        
        if self.tvsx:
            self.tca_tvsx(curves, sep=self.plot_separately)

        if self.tvsy:
            self.tca_tvsy(curves, sep=self.plot_separately)

        if self.tvsxvsy:
            self.tca_tvsxvsy(curves, sep=self.plot_separately)

        plt.show()

    def tca_tvsx(self, curves: list, sep: bool) -> None:
        if not sep:
            plt.figure()

        for c in curves:
            if sep:
                plt.figure()

            traj_data = self.traj_dict[c]

            time_lims = traj_data["time_lims"]
            sol_f = traj_data["sol_f"].y[0,:]
            sol_r = np.flip(traj_data["sol_r"].y[0,:])

            full_time = np.linspace(time_lims[0], time_lims[1], len(sol_f) + len(sol_r))
            full_curve = np.concatenate((sol_r, sol_f))

            plt.plot(full_time, full_curve, label="Curve " + str(c))
            plt.legend()
            plt.xlabel(r'$t$')
            plt.ylabel(r'$x(t)$')
            plt.title('PyPLANE: ' + r'$t$' + ' vs ' + r'$x(t)$')

    def tca_tvsy(self, curves: list, sep: bool) -> None:
        if not sep:
            plt.figure()

        for c in curves:
            if sep:
                plt.figure()

            traj_data = self.traj_dict[c]

            time_lims = traj_data["time_lims"]
            sol_f = traj_data["sol_f"].y[1,:]
            sol_r = np.flip(traj_data["sol_r"].y[1,:])

            full_time = np.linspace(time_lims[0], time_lims[1], len(sol_f) + len(sol_r))
            full_curve = np.concatenate((sol_r, sol_f))

            plt.plot(full_time, full_curve, label="Curve " + str(c))
            plt.legend()
            plt.xlabel(r'$t$')
            plt.ylabel(r'$y(t)$')
            plt.title('PyPLANE: ' + r'$t$' + ' vs ' + r'$y(t)$')

    def tca_tvsxvsy(self, curves: list, sep: bool) -> None:

        #if not sep:
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')

        for c in curves:

            traj_data = self.traj_dict[c]
            time_lims = traj_data["time_lims"]

            sol_f_x = traj_data["sol_f"].y[0,:]
            sol_r_x = np.flip(traj_data["sol_r"].y[0,:])
            full_curve_x = np.concatenate((sol_r_x, sol_f_x))

            sol_f_y = traj_data["sol_f"].y[1,:]
            sol_r_y = np.flip(traj_data["sol_r"].y[1,:])
            full_curve_y = np.concatenate((sol_r_y, sol_f_y))

            full_time = np.linspace(time_lims[0], time_lims[1], len(full_curve_x))
            
            ax.plot(full_time, full_curve_x, full_curve_y, label="Curve " + str(c))

        ax.set_title(r'$t$' + ' vs ' + r'$x(t)$'  + ' vs ' + r'$y(t)$')
        ax.set_xlabel(r'$t$')
        ax.set_ylabel(r'$x(t)$')
        ax.set_zlabel(r'$y(t)$')
        ax.legend()

        #else:
        #    figlist = []
        #    for c in curves:

        #        traj_data = self.traj_dict[c]
        #        time_lims = traj_data["time_lims"]

        #        sol_f_x = traj_data["sol_f"].y[0,:]
        #        sol_r_x = np.flip(traj_data["sol_r"].y[0,:])
        #        full_curve_x = np.concatenate((sol_r_x, sol_f_x))

        #        sol_f_y = traj_data["sol_f"].y[1,:]
        #        sol_r_y = np.flip(traj_data["sol_r"].y[1,:])
        #        full_curve_y = np.concatenate((sol_r_y, sol_f_y))

        #        full_time = np.linspace(time_lims[0], time_lims[1], len(full_curve_x))

        #        fig = plt.figure()
        #        ax = fig.add_subplot(111, projection='3d')

        #        ax.plot(full_time, full_curve_x, full_curve_y, label="Curve " + str(c))

        #        ax.set_title(r'$t$' + ' vs ' + r'$x(t)$'  + ' vs ' + r'$y(t)$')
        #        ax.set_xlabel(r'$t$')
        #        ax.set_ylabel(r'$x(t)$')
        #        ax.set_zlabel(r'$y(t)$')
        #        ax.legend()

        #        figlist.append(fig, ax)
