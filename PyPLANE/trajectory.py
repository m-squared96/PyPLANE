from collections.abc import Iterable

import numpy as np
import matplotlib  # Imported seperately for type hinting in onclick function signature
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigCanvas

from PyPLANE.equations import SystemOfEquations


class PhaseSpaceParent(FigCanvas):
    """
    Accepts a system of equations (equations.SystemOfEqutions object) and produces
    a phase plot. Individual trajectories evaluated upon click event.

    For now, can handle up to three-dimensional systems. An arbitrary number of dimensions
    may require a lot of work.
    """

    #TODO: I think we can get rid of these commented-out args
    def __init__(
        self,
        dimensions: int,
        # system: SystemOfEquations,
        fw_time_lim: float = 5.0,
        bw_time_lim: float = -5.0,
        # axes_limits: tuple = ((-5, 5), (-5, 5)),
        # max_trajectories: int = 10,
        # quiver_expansion_factor: float = 0.2,
        # axes_points: int = 20,
        # mesh_density: int = 200,
        *args,
        **kwargs,
    ) -> None:

        self.dimensions = dimensions
        self.fig = Figure()
        object.__init__(self)
        FigCanvas.__init__(self, self.fig)
        self.ax = self.fig.add_subplot(111)
        self.time_f = fw_time_lim
        self.time_r = bw_time_lim

    def generate_meshes(self) -> (np.ndarray, np.ndarray):
        """
        Returns R and Rprime, lists of mesh grids for coordinate positions and phase
        space slopes respectively
        """
        if self.system.dims == 1:
            tmin, tmax = self.get_calc_limits(self.axes_limits[0])
            xmin, xmax = self.get_calc_limits(self.axes_limits[1])

            R = np.meshgrid(
                np.linspace(tmin, tmax, self.mesh_density),
                np.linspace(xmin, xmax, self.mesh_density),
            )

            # Split the Rprime declaration into two lines for clarity
            dependent_primes = self.system.phasespace_eval(t=None, r=np.array([R[1]]))[
                0
            ]
            Rprime = [np.ones(R[0].shape), dependent_primes]

        elif self.system.dims == 2:
            xmin, xmax = self.get_calc_limits(self.axes_limits[0])
            ymin, ymax = self.get_calc_limits(self.axes_limits[1])

            R = np.meshgrid(
                np.linspace(xmin, xmax, self.mesh_density),
                np.linspace(ymin, ymax, self.mesh_density),
            )

        elif self.system.dims == 3:
            xmin, xmax = self.get_calc_limits(self.axes_limits[0])
            ymin, ymax = self.get_calc_limits(self.axes_limits[1])
            zmin, zmax = self.get_calc_limits(self.axes_limits[2])

            R = np.meshgrid(
                np.linspace(xmin, xmax, self.mesh_density),
                np.linspace(ymin, ymax, self.mesh_density),
                np.linspace(zmin, zmax, self.mesh_density),
            )

        if self.system.dims in (2, 3):
            Rprime = self.system.phasespace_eval(t=None, r=R)

        return R, Rprime

    def get_calc_limits(self, lims: list) -> (float, float):
        """
        Returns the limits to be used in the mesh grid generation expanded with the
        self.quiver_expansion_factor variable
        """
        extension = np.abs(lims[1] - lims[0]) * self.quiver_expansion_factor * 0.5
        min_lim = lims[0] - extension
        max_lim = lims[1] + extension

        return min_lim, max_lim

    def derivative_expression_resolve(
        self, display_vars: list, dimensions: int, positions: list
    ) -> np.ndarray:
        """
        Function to resolve the coordinates of an argument to the order of
        coordinates in an equations.SystemOfEquations object
        """
        eval_seq = []

        if dimensions in (2, 3):
            for var in self.system.system_coords:
                if not (var in display_vars):
                    eval_seq.append(0)

                elif var in display_vars:
                    eval_seq.append(positions[display_vars.index(var)])

        elif dimensions == 1:
            eval_seq.append(self.system.system_coords[0])

        return np.array(eval_seq)

    def plot_nullclines(self) -> list:
        """
        Plots the nullclines for the current 2-D system.
        """

        if self.dimensions == 1:
            X, *_ = self.quiver_data["t"]
            Y, V, *_ = self.quiver_data[self.system.system_coords[0]]
            contours_y = self.ax.contour(X, Y, V, levels=[0], colors="yellow")
            return [contours_y]

        elif self.dimensions == 2:
            X, U, *_ = self.quiver_data[self.system.system_coords[0]]
            Y, V, *_ = self.quiver_data[self.system.system_coords[1]]
            contours_x = self.ax.contour(X, Y, U, levels=[0], colors="red")
            contours_y = self.ax.contour(X, Y, V, levels=[0], colors="yellow")
            return [contours_x, contours_y]

    def toggle_nullclines(self) -> None:
        """
        Toggles nullcline visibility on plot
        """

        if not self.nullclines_init:
            self.nullcline_contour_sets = self.plot_nullclines()
            # self.plot_nullclines()
            self.nullclines_init = True
        else:
            for contour in self.nullcline_contour_sets:
                # The QuadContourSet object usually has a collections (list) attribute
                # with a single LineCollection object in it
                nc = contour.collections[0]
                nc.set_visible(not nc.get_visible())

        self.draw()

    def toggle_fixed_points(self):
        if not self.fixed_points_init:
            self.fixed_point_markers = self.ax.plot(
                *zip(*self.system.fixed_points), "ro", markersize=5
            )
            self.fixed_points_init = True
            self.draw()
        else:
            for fp in self.fixed_point_markers:
                fp.set_visible(not fp.get_visible())
            self.draw()

    def reduce_array_density(
        self, full_array: np.ndarray, axes_points: int
    ) -> np.ndarray:
        """
        Accepts a square, 2D Numpy array (array) and an integer variable (axes_points).
        Returns a less dense, 2D, square Numpy array with a size of (at least) axes_points squared.
        """
        if len(full_array.shape) == 2 and full_array.shape[0] == full_array.shape[1]:
            step = int(full_array.shape[0] / axes_points)
            return np.array(full_array[::step, ::step], dtype=float)


class PhaseSpace1D(PhaseSpaceParent):
    def __init__(
        self,
        system: SystemOfEquations,
        fw_time_lim: float = 5.0,
        bw_time_lim: float = -5.0,
        axes_limits: tuple = ((-5, 5), (-5, 5)),
        max_trajectories: int = 10,
        quiver_expansion_factor: float = 0.2,
        axes_points: int = 20,
        mesh_density: int = 200,
        *args,
        **kwargs,
    ) -> None:

        super().__init__(1, fw_time_lim, bw_time_lim)

        # Initialise button click event on local figure object
        self.cid = self.fig.canvas.mpl_connect("button_press_event", self.onclick)

        self.init_space(
            system,
            fw_time_lim,
            bw_time_lim,
            axes_limits,
            max_trajectories,
            quiver_expansion_factor,
            axes_points,
            mesh_density,
        )

    def init_space(
        self,
        system: SystemOfEquations,
        fw_time_lim: float = 5,
        bw_time_lim: float = -5,
        axes_limits: tuple = ((-5, 5), (-5, 5)),
        max_trajectories: int = 10,
        quiver_expansion_factor: float = 0.2,
        axes_points: int = 20,
        mesh_density: int = 200,
    ) -> None:

        self.ax.cla()
        self.system = system

        # # Time at which to stop forward trajectory evaluation
        # self.time_f = fw_time_lim
        # # Time at which to stop backward trajectory evaluation
        # self.time_r = bw_time_lim

        # Factor to expand quiverplot to ensure all visible regions plotted
        self.quiver_expansion_factor = quiver_expansion_factor

        # Two-dimensional array in the form [[x1min, x1max], [x2min, x2max], ...] etc
        if isinstance(axes_limits[0], Iterable):
            self.axes_limits = np.array(axes_limits)
        else:
            self.axes_limits = np.array(
                (float(bw_time_lim), float(fw_time_lim)),
                (axes_limits[0], axes_limits[1]),
            )

        # axes_points = number of points along each axis if quiver_expansion_factor = 0
        # self.axes_points = axes_points * (1 + self.quiver_expansion_factor) ==> expands vector field beyond FOV
        # whilst preserving as much as possible the spacing between individual vectors.
        # Another possible approach would be to explicitly define the spacing between vectors, but this method
        # could cause performance issues if large axis limits are required and the vector spacing is not adjusted
        # accordingly.
        self.axes_points = int(axes_points * (1 + self.quiver_expansion_factor))

        # TODO: explain
        self.mesh_density = mesh_density

        self.max_trajectories = (
            max_trajectories  # Maximum number of trajectories that can be visualised
        )
        self.trajectory_count = 0  # Trajectory increment variable
        self.trajectories = {}

        # Set to True only by toggle_nullclines method
        self.nullclines_init = False

        # List of references to the contour sets returned by plt.contour
        self.nullcline_contour_sets = None

        # Set to True only by toggle_fixed_points method
        self.fixed_points_init = False

        # list of references to fixed point markers
        self.fixed_point_markers = None

        display_vars = self.system.system_coords

        for var in display_vars:
            if not (var in self.system.system_coords):
                return

        self.display_vars = display_vars
        self.draw_quiver()

    def draw_quiver(self) -> None:
        # Returns R (coordinate grids) and Rprime (slope grids)
        R, Rprime = self.generate_meshes()
        quiver_data = {}

        quiver_data["t"] = (
            R[0],
            Rprime[0],
            self.axes_limits[0][0],
            self.axes_limits[0][1],
        )
        quiver_data[self.system.system_coords[0]] = (
            R[1],
            Rprime[1],
            self.axes_limits[1][0],
            self.axes_limits[1][1],
        )

        self.quiver_data = quiver_data

        # Display vars are the system variables to be plotted.
        # Given a system with coords [x, y], display_vars can take 4 forms:
        # 1. ["x"], 2. ["y"], 3. ["x", "y"], 4. ["y", "x"]
        # In the one-dimensional cases, the quiverplot will be t vs x, or t vs y.
        # In the two-dimensional cases, the variables plotted on a given axis depend on the order of display_vars.
        # If display_vars = ["y", "x"] the y variable is plotted on the x-axis, and x on the y-axis. Trippy, I know.

        X, U, xmin, xmax = self.quiver_data["t"]
        Y, V, ymin, ymax = self.quiver_data[self.display_vars[0]]

        self.ax.set_xlim(xmin, xmax)
        self.ax.set_ylim(ymin, ymax)

        # Sets up quiver plot
        self.quiver = self.ax.quiver(
            self.reduce_array_density(X, self.axes_points),
            self.reduce_array_density(Y, self.axes_points),
            self.reduce_array_density(U, self.axes_points),
            self.reduce_array_density(V, self.axes_points),
            pivot="middle",
            angles="xy",
        )

        self.trajectory = self.ax.plot(0, 0)  # Need an initial 'trajectory'

        self.draw()

    def onclick(self, event: matplotlib.backend_bases.MouseEvent) -> None:
        """
        Function called upon mouse click event
        """
        # Only works if mouse click is on axis and the maximum number of trajectories has not been reached
        if not event.inaxes == self.ax:
            return

        if event.dblclick and self.trajectory_count < self.max_trajectories:
            self.add_trajectory(event)
            self.plot_trajectories()
        else:
            self.regen_quiver(event)

    def regen_quiver(self, event) -> None:
        new_lims = np.asarray((tuple(self.ax.get_xlim()), tuple(self.ax.get_ylim())))

        if not np.all(self.axes_limits == new_lims):
            self.axes_limits = new_lims
            self.clear_plane()
            self.draw_quiver()
            self.plot_trajectories()

    def clear_plane(self) -> None:
        self.ax.cla()
        for traj in list(self.trajectories.keys()):
            self.trajectories[traj]["plotted"] = False

    def add_trajectory(self, event: matplotlib.backend_bases.MouseEvent) -> None:

        # Mouse click coordinates
        x_event = event.xdata
        y_event = event.ydata

        # Recall that in a 1D scenario, the x_event variable is essentially the inital time of the trajectory
        solution_f = self.system.solve((x_event, self.time_f), r0=[y_event])
        solution_r = self.system.solve((x_event, self.time_r), r0=[y_event])

        self.trajectory_count += 1

        traj_dict = {}
        traj_dict["x_event"] = x_event
        traj_dict["y_event"] = y_event
        traj_dict["sol_f"] = solution_f
        traj_dict["sol_r"] = solution_r
        traj_dict["plotted"] = False

        self.trajectories[self.trajectory_count] = traj_dict

    def plot_trajectories(self) -> None:
        
        for traj in list(self.trajectories.keys()):
            traj_dict = self.trajectories[traj]

            if traj_dict["plotted"]:
                continue

            x_event = traj_dict["x_event"]
            y_event = traj_dict["y_event"]
            solution_f = traj_dict["sol_f"]
            solution_r = traj_dict["sol_r"]

            # Plots a red "x" on the position of the user's click
            self.ax.plot(x_event, y_event, ls="", marker="x", c="#FF0000")

            for sol, t in zip((solution_f, solution_r), (self.time_f, self.time_r)):
                if sol.success:
                    y = sol.y[0, :]
                    if x_event != t:
                        x = np.linspace(x_event, t, y.size)
                    elif x_event == t:
                        x = x_event
                    self.trajectory = self.ax.plot(x, y, c="#0066FF")
                    self.fig.canvas.draw()
                else:
                    print(sol.message)



class PhaseSpace2D(PhaseSpaceParent):
    def __init__(
        self,
        system: SystemOfEquations,
        fw_time_lim: float = 5.0,
        bw_time_lim: float = -5.0,
        axes_limits: tuple = ((-5, 5), (-5, 5)),
        max_trajectories: int = 10,
        quiver_expansion_factor: float = 0.2,
        axes_points: int = 20,
        mesh_density: int = 200,
        *args,
        **kwargs,
    ) -> None:

        super().__init__(2)

        # Initialise button click event on local figure object
        self.cid = self.fig.canvas.mpl_connect("button_press_event", self.onclick)

        self.init_space(
            system,
            fw_time_lim,
            bw_time_lim,
            axes_limits,
            max_trajectories,
            quiver_expansion_factor,
            axes_points,
            mesh_density,
        )

    def init_space(
        self,
        system: SystemOfEquations,
        fw_time_lim: float = 5.0,
        bw_time_lim: float = -5.0,
        axes_limits: tuple = ((-5, 5), (-5, 5)),
        max_trajectories: int = 10,
        quiver_expansion_factor: float = 0.2,
        axes_points: int = 20,
        mesh_density: int = 200,
    ) -> None:

        self.ax.cla()
        self.system = system

        # Time at which to stop forward trajectory evaluation
        self.time_f = fw_time_lim
        # Time at which to stop backward trajectory evaluation
        self.time_r = bw_time_lim

        # Factor to expand quiverplot to ensure all visible regions plotted
        self.quiver_expansion_factor = quiver_expansion_factor

        # Two-dimensional array in the form [[x1min, x1max], [x2min, x2max], ...] etc
        self.axes_limits = np.array(axes_limits)

        # axes_points = number of points along each axis if quiver_expansion_factor = 0
        # self.axes_points = axes_points * (1 + self.quiver_expansion_factor) ==> expands vector field beyond FOV
        # whilst preserving as much as possible the spacing between individual vectors.
        # Another possible approach would be to explicitly define the spacing between vectors, but this method
        # could cause performance issues if large axis limits are required and the vector spacing is not adjusted
        # accordingly.
        self.axes_points = int(axes_points * (1 + self.quiver_expansion_factor))

        # TODO: explain
        self.mesh_density = mesh_density

        self.max_trajectories = (
            max_trajectories  # Maximum number of trajectories that can be visualised
        )
        self.trajectory_count = 0  # Trajectory increment variable

        (
            R,
            Rprime,
        ) = (
            self.generate_meshes()
        )  # Returns R (coordinate grids) and Rprime (slope grids)
        quiver_data = {}

        for label, mesh, prime_mesh, axlims in zip(
            self.system.system_coords, R, Rprime, self.axes_limits
        ):
            axmin, axmax = tuple(axlims)
            quiver_data[label] = (mesh, prime_mesh, axmin, axmax)

        self.quiver_data = quiver_data

        # Set to True only by toggle_nullclines method
        self.nullclines_init = False

        # List of references to the contour sets returned by plt.contour
        self.nullcline_contour_sets = None

        # Set to True only by toggle_fixed_points method
        self.fixed_points_init = False

        # list of references to fixed point markers
        self.fixed_point_markers = None

        display_vars = self.system.system_coords

        for var in display_vars:
            if not (var in self.system.system_coords):
                return

        # Display vars are the system variables to be plotted.
        # Given a system with coords [x, y], display_vars can take 4 forms:
        # 1. ["x"], 2. ["y"], 3. ["x", "y"], 4. ["y", "x"]
        # In the one-dimensional cases, the quiverplot will be t vs x, or t vs y.
        # In the two-dimensional cases, the variables plotted on a given axis depend on the order of display_vars.
        # If display_vars = ["y", "x"] the y variable is plotted on the x-axis, and x on the y-axis. Trippy, I know.
        self.display_vars = display_vars

        X, U, xmin, xmax = self.quiver_data[display_vars[0]]
        Y, V, ymin, ymax = self.quiver_data[display_vars[1]]

        self.ax.set_xlim(xmin, xmax)
        self.ax.set_ylim(ymin, ymax)

        # Sets up quiver plot
        self.quiver = self.ax.quiver(
            self.reduce_array_density(X, self.axes_points),
            self.reduce_array_density(Y, self.axes_points),
            self.reduce_array_density(U, self.axes_points),
            self.reduce_array_density(V, self.axes_points),
            pivot="middle",
            angles="xy",
        )

        self.trajectory = self.ax.plot(0, 0)  # Need an initial 'trajectory'

        self.draw()

    # TODO: Can we de-duplicate the onclick methods?
    # onlick used in both dimension classes BUT needs to point at different trajectory pointing methods.
    def onclick(self, event: matplotlib.backend_bases.MouseEvent) -> None:
        """
        Function called upon mouse click event
        """
        # Only works if mouse click is on axis and the maximum number of trajectories has not been reached
        if (
            event.inaxes == self.ax
            and self.trajectory_count < self.max_trajectories
            and event.dblclick
        ):
            self.add_trajectory(event)

    def add_trajectory(self, event: matplotlib.backend_bases.MouseEvent) -> None:

        # Mouse click coordinates
        x_event = event.xdata
        y_event = event.ydata

        # Plots a red "x" on the position of the user's click
        self.ax.plot(x_event, y_event, ls="", marker="x", c="#FF0000")

        # Trajectory production and plotting
        # eval_point is the point on the quiverplot that has been clicked by the user. However, the coordinates are made
        # consistent with the ordering of the system coordinates. For example, on a graph with y vs x, the x_event variable
        # will correspond to a value on x-axis, which represents the y variable of the system. Similarly with the y_event variable
        # representing the x variable of the system. In this case, eval_point = (y_event, x_event) such that the coordinates
        # are in the order (x, y) for the SOE to solve and evaluate.
        eval_point = self.derivative_expression_resolve(
            self.display_vars, self.dimensions, (x_event, y_event)
        )
        solution_f = self.system.solve((0, self.time_f), r0=eval_point)
        solution_r = self.system.solve((0, self.time_r), r0=eval_point)

        for sol in (solution_f, solution_r):
            if sol.success:
                # sol.y has shape (2, n_points) for a 2-D system
                # print(len(sol.t))
                x = sol.y[self.system.system_coords.index(self.display_vars[0]), :]
                y = sol.y[self.system.system_coords.index(self.display_vars[1]), :]
                self.trajectory = self.ax.plot(x, y, c="#0066FF")
                self.fig.canvas.draw()
            else:
                print(sol.message)

        self.trajectory_count += 1
