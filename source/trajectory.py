import numpy as np
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from equations import SystemOfEquations
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigCanvas

class PhaseSpacePlotter(FigCanvas):
    """
    Accepts a system of equations (equations.SystemOfEqutions object) and produces
    a phase plot. Individual trajectories evaluated upon click event.

    For now, can handle up to three-dimensional systems. An arbitrary number of dimensions
    may require a lot of work.
    """
    def __init__(self, system, fw_time_lim, bw_time_lim, axes_limits, max_trajectories=10, quiver_expansion_factor=0.2,
                axes_points=20, mesh_density=200):

        self.system = system # SOE object
        self.quiver_expansion_factor = quiver_expansion_factor # Factor to expand quiverplot to ensure all visible regions plotted
        self.fig = Figure() 
        self.ax = self.fig.add_subplot(111)
        self.xmin, self.xmax = axes_limits[0]
        self.ymin, self.ymax = axes_limits[1]
        self.ax.set_xlim(self.xmin, self.xmax)
        self.ax.set_ylim(self.ymin, self.ymax)
        
        object.__init__(self)
        FigCanvas.__init__(self, self.fig)

        # Initialise button click event on local figure object
        self.cid = self.fig.canvas.mpl_connect("button_press_event", self.onclick)

        self.time_f = fw_time_lim # Time at which to stop forward trajectory evaluation
        self.time_r = bw_time_lim # Time at which to stop backward trajectory evaluation
        
        self.quiver_expansion_factor = quiver_expansion_factor # Factor to expand quiverplot to ensure all visible regions plotted
        self.axes_limits = np.array(axes_limits) # Two-dimensional array in the form [[x1min, x1max], [x2min, x2max], ...] etc

        # axes_points = number of points along each axis if quiver_expansion_factor = 0
        # self.axes_points = axes_points * (1 + self.quiver_expansion_factor) ==> expands vector field beyond FOV
        # whilst preserving as much as possible the spacing between individual vectors.
        # Another possible approach would be to explicitly define the spacing between vectors, but this method
        # could cause performance issues if large axis limits are required and the vector spacing is not adjusted
        # accordingly.
        self.axes_points = int(axes_points * (1 + self.quiver_expansion_factor))

        # TODO: explain
        self.mesh_density = mesh_density

        self.max_trajectories = max_trajectories # Maximum number of trajectories that can be visualised
        self.trajectory_count = 0 # Trajectory increment variable

        R, Rprime = self.generate_meshes() # Returns R (coordinate grids) and Rprime (slope grids)
        quiver_data = {}

        if self.system.dims == 1:
            quiver_data["t"] = (R[0], Rprime[0], self.time_r, self.time_f)
            quiver_data[self.system.system_coords[0]] = (R[1], Rprime[1], self.axes_limits[0][0], self.axes_limits[0][1])

        elif self.system.dims in (2, 3):
            for label, mesh, prime_mesh, axlims in zip(self.system.system_coords, R, Rprime, self.axes_limits):
                axmin, axmax = tuple(axlims)
                quiver_data[label] = (mesh, prime_mesh, axmin, axmax)

        self.quiver_data = quiver_data

        # Set to True once nullclines are first created and plotted
        # See "toggle_nullclines" method
        self.nullclines_init = False

        # List of references to the contour sets returned by plt.contour
        self.nullcline_contour_sets = None


    def generate_meshes(self):
        """
        Returns R and Rprime, lists of mesh grids for coordinate positions and phase
        space slopes respectively
        """
        if self.system.dims == 1:
            tmin, tmax = self.get_calc_limits((self.time_r, self.time_f))
            xmin, xmax = self.get_calc_limits(self.axes_limits[0])

            R = np.meshgrid(np.linspace(tmin, tmax, self.mesh_density), 
                            np.linspace(xmin, xmax, self.mesh_density))

            # Split the Rprime declaration into two lines for clarity
            dependent_primes = self.system.phasespace_eval(t=None, r=np.array([R[1]]))[0]
            Rprime = [np.ones(R[0].shape), dependent_primes]

        elif self.system.dims == 2:
            xmin, xmax = self.get_calc_limits(self.axes_limits[0])
            ymin, ymax = self.get_calc_limits(self.axes_limits[1])

            R = np.meshgrid(np.linspace(xmin, xmax, self.mesh_density),
                            np.linspace(ymin, ymax, self.mesh_density))

        elif self.system.dims == 3:
            xmin, xmax = self.get_calc_limits(self.axes_limits[0])
            ymin, ymax = self.get_calc_limits(self.axes_limits[1])
            zmin, zmax = self.get_calc_limits(self.axes_limits[2])

            R = np.meshgrid(np.linspace(xmin, xmax, self.mesh_density),
                            np.linspace(ymin, ymax, self.mesh_density),
                            np.linspace(zmin, zmax, self.mesh_density))

        if self.system.dims in (2, 3):
            Rprime = self.system.phasespace_eval(t=None, r=R)

        return R, Rprime
             
    def get_calc_limits(self, lims):
        """
        Returns the limits to be used in the mesh grid generation expanded with the
        self.quiver_expansion_factor variable
        """
        extension = np.abs(lims[1] - lims[0]) * self.quiver_expansion_factor * 0.5
        min_lim = lims[0] - extension
        max_lim = lims[1] + extension
        return min_lim, max_lim

    def update_system(self, system):
        self.ax.cla() # clears axis
        self.system = system # SOE object
        
        # later on, set axis limits
        # self.xmin, self.xmax = ...
        # self.ymin, self.ymax = ...
        # self.ax.set_xlim(self.xmin, self.xmax)
        # self.ax.set_ylim(self.ymin, self.ymax)
        
        self.trajectory_count = 0
        self.nullclines_init = False
        self.nullcline_contour_sets = None
    
        # Defines X and Y points and evaluates the derivatives at each point
        X, Y = np.meshgrid(
            np.linspace(self.xmin * (1 + self.quiver_expansion_factor), self.xmax * (1 + self.quiver_expansion_factor), 15),
            np.linspace(self.ymin * (1 + self.quiver_expansion_factor), self.ymax * (1 + self.quiver_expansion_factor), 15)
        )
        U, V = self.system.phasespace_eval(t=None, r=np.array([X, Y]))
 
        # Sets up quiver plot
        self.quiver = self.ax.quiver(X, Y, U, V, pivot="middle")
        self.trajectory = self.ax.plot(0, 0) # Need an initial 'trajectory'

        self.draw()
        
    def show_plot(self, display_vars):

        def one_or_two_dimensions(display_vars, dimensions):

            # Initialise button click event on local figure object
            self.cid = self.fig.canvas.mpl_connect("button_press_event", self.onclick)
       
            if dimensions == 1:
                X, U, xmin, xmax = self.quiver_data["t"]
                Y, V, ymin, ymax = self.quiver_data[display_vars[0]]

            if dimensions == 2:
                X, U, xmin, xmax = self.quiver_data[display_vars[0]]
                Y, V, ymin, ymax = self.quiver_data[display_vars[1]]

            self.ax.set_xlim(xmin, xmax)
            self.ax.set_ylim(ymin, ymax)

            # Sets up quiver plot
            self.quiver = self.ax.quiver(self.reduce_array_density(X, self.axes_points), 
                                         self.reduce_array_density(Y, self.axes_points), 
                                         self.reduce_array_density(U, self.axes_points), 
                                         self.reduce_array_density(V, self.axes_points), 
                                         pivot="middle", angles="xy")

            self.trajectory = self.ax.plot(0, 0) # Need an initial 'trajectory'

        #TODO: Three dimensional plotting
        def three_dimensions(display_vars, axes_limits):
            pass
        
        self.ax.cla() # clears axis

        for var in display_vars:
            if not(var in self.system.system_coords): return 

        # Display vars are the system variables to be plotted. 
        # Given a system with coords [x, y], display_vars can take 4 forms:
        # 1. ["x"], 2. ["y"], 3. ["x", "y"], 4. ["y", "x"]
        # In the one-dimensional cases, the quiverplot will be t vs x, or t vs y.
        # In the two-dimensional cases, the variables plotted on a given axis depend on the order of display_vars.
        # If display_vars = ["y", "x"] the y variable is plotted on the x-axis, and x on the y-axis. Trippy, I know.
        self.display_vars = display_vars
        self.dimensions = len(self.display_vars)

        if self.dimensions < 1 or self.dimensions > 3:
            raise ValueError("Must be between 1 and 3 variables to display")

        elif self.dimensions in (1, 2):
            one_or_two_dimensions(display_vars, self.dimensions)

        elif self.dimensions == 3:
            three_dimensions(display_vars, axes_limits)       

        self.draw()

    def onclick(self, event):
        """
        Function called upon mouse click event
        """
        #if event.dblclick: 
        #    print("\nActivated")
        #    print(event.inaxes == self.ax)
        #    print(self.trajectory_count, self.max_trajectories)
        #    print(event.dblclick)

        # Only works if mouse click is on axis and the maximum number of trajectories has not been reached
        if not (event.inaxes == self.ax and self.trajectory_count < self.max_trajectories and event.dblclick):
            return
            
        # Mouse click coordinates
        x_event = event.xdata
        y_event = event.ydata

        self.ax.plot(x_event, y_event, ls="", marker="x", c="#FF0000") # Plots a red "x" on the position of the user's click

        # Seperate blocks of code for handling one and two dimensions are required as, from an SOE point of view, they are
        # fundamentally different, as t is not a system variable in the same way that, for example, x is.
        if self.dimensions == 2:
            # Trajectory production and plotting

            # eval_point is the point on the quiverplot that has been clicked by the user. However, the coordinates are made
            # consistent with the ordering of the system coordinates. For example, on a graph with y vs x, the x_event variable
            # will correspond to a value on x-axis, which represents the y variable of the system. Similarly with the y_event variable
            # representing the x variable of the system. In this case, eval_point = (y_event, x_event) such that the coordinates
            # are in the order (x, y) for the SOE to solve and evaluate.
            eval_point = self.derivative_expression_resolve(self.display_vars, self.dimensions, (x_event, y_event))
            solution_f = self.system.solve((0, self.time_f), r0=eval_point)
            solution_r = self.system.solve((0, self.time_r), r0=eval_point)

            for sol in (solution_f, solution_r):
                if sol.success:
                    # sol.y has shape (2, n_points) for a 2-D system
                    # print(len(sol.t))
                    x = sol.y[self.system.system_coords.index(self.display_vars[0]),:]
                    y = sol.y[self.system.system_coords.index(self.display_vars[1]),:]
                    self.trajectory = self.ax.plot(x, y, c="#0066FF")
                    self.fig.canvas.draw()
                else: print(sol.message)
        
        elif self.dimensions == 1:
            # Recall that in a 1D scenario, the x_event variable is essentially the inital time of the trajectory
            solution_f = self.system.solve((x_event, self.time_f), r0=[y_event])
            solution_r = self.system.solve((x_event, self.time_r), r0=[y_event])
            for sol, t in zip((solution_f, solution_r), (self.time_f, self.time_r)):
                if sol.success:
                    y = sol.y[0, :]
                    if x_event != t: x = np.linspace(x_event, t, y.size)
                    elif x_event == t: x = x_event
                    self.trajectory = self.ax.plot(x, y, c="#0066FF")
                    self.fig.canvas.draw()
                else:
                    print(sol.message)

        self.trajectory_count += 1

    def derivative_expression_resolve(self, display_vars, dimensions, positions):
        """
        Function to resolve the coordinates of an argument to the order of
        coordinates in an equations.SystemOfEquations object
        """
        eval_seq = []
        
        if dimensions in (2, 3):
            for var in self.system.system_coords:
                if not(var in display_vars): eval_seq.append(0)
                
                elif var in display_vars:
                    eval_seq.append(positions[display_vars.index(var)])
        
        elif dimensions == 1:
            eval_seq.append(self.system.system_coords[0])

        return np.array(eval_seq)
    
    def plot_nullclines(self):
        """
        Plots the nullclines for the current 2-D system.
        """

        if self.dimensions == 1:
            X, *_ = self.quiver_data["t"]
            Y, V, *_ = self.quiver_data[self.system.system_coords[0]]
            contours_y = self.ax.contour(X, Y, V, levels=[0], colors='yellow')
            return [contours_y]

        elif self.dimensions == 2:
            X, U, *_ = self.quiver_data[self.system.system_coords[0]]
            Y, V, *_ = self.quiver_data[self.system.system_coords[1]]
            contours_x = self.ax.contour(X, Y, U, levels=[0], colors='red')
            contours_y = self.ax.contour(X, Y, V, levels=[0], colors='yellow')
            return [contours_x, contours_y]
    
    def toggle_nullclines(self):
        """
        Toggles nullcline visibility on plot
        """

        if not self.nullclines_init:
            self.nullcline_contour_sets = self.plot_nullclines()
            #self.plot_nullclines()
            self.nullclines_init = True
        else:
            for contour in self.nullcline_contour_sets:
                # The QuadContourSet object usually has a collections (list) attribute
                # with a single LineCollection object in it
                nc = contour.collections[0]
                nc.set_visible(not nc.get_visible())
        
        self.draw()

    def reduce_array_density(self, array, axes_points):
        """
        Accepts a square, 2D Numpy array (array) and an integer variable (axes_points).
        Returns a less dense, 2D, square Numpy array with a size of (at least) axes_points squared.
        """
        if len(array.shape) == 2 and array.shape[0] == array.shape[1]:
            step = int(array.shape[0]/axes_points)
            return array[::step, ::step]


def call_PSP(system, PSP_args):
    if system == None:
        system = default_system()

    return PhaseSpacePlotter(system, PSP_args['t_f'], PSP_args['t_r'], PSP_args['axes_lims'], quiver_expansion_factor=PSP_args['qef'])


def default_system():
   return SystemOfEquations(['x', 'y'], ['y', '-x'], params={})


#def one_D_example():
#    phase_coords = ['x']
#    eqns = ['sin(x)']
#    params = {'a':1, 'b':0}
#    t_f = 20
#    t_r = -20
#
#    sys = SystemOfEquations(phase_coords, eqns, params=params)
#    plotter = PhaseSpacePlotter(sys, t_f, t_r, np.array(((0, 10), (0, 10))), quiver_expansion_factor=0.2)
#    plotter.show_plot(['x'])
#
#
#def two_D_example():
#    phase_coords = ['x', 'y']
#    eqns = [
#        '2x - y + 3(x^2-y^2) + 2xy',
#        'x - 3y - 3(x^2-y^2) + 3xy'
#    ]
#    params = {
#        'a': -1,
#        'b': 5,
#        'c': -4,
#        'd': -2
#    }
#    t_f = 5
#    t_r = -5
#
#    sys = SystemOfEquations(phase_coords, eqns, params=params)
#    plotter = PhaseSpacePlotter(sys, t_f, t_r, np.array(((-10, 10), (-10, 10))))
#    # print(plotter.R[0].shape)
#    # print(plotter.Rprime)
#    plotter.show_plot(['x', 'y'])
#
#
#if __name__ == "__main__":
#    one_D_example()
#    two_D_example()
