import numpy as np
import matplotlib.pyplot as plt

from equations import SystemOfEquations


class PhaseSpacePlotter(object):
    """
    Accepts a system of equations (equations.SystemOfEqutions object) and produces
    a phase plot. Individual trajectories evaluated upon click event.
    """
    def __init__(self, system, fw_time_lim, bw_time_lim, max_trajectories=10, quiver_expansion_factor=0.2):

        self.system = system # SOE object

        self.quiver_expansion_factor = quiver_expansion_factor # Factor to expand quiverplot to ensure all visible regions plotted
        
        self.time_f = fw_time_lim # Time at which to stop forward trajectory evaluation
        self.time_r = bw_time_lim # Time at which to stop backward trajectory evaluation

        self.max_trajectories = max_trajectories # Maximum number of trajectories that can be visualised
        self.trajectory_count = 0 # Trajectory increment variable
      
    def show_plot(self, display_vars, axes_limits):

        def one_or_two_dimensions(display_vars, axes_limits, dimensions):

            xmin, xmax = tuple(axes_limits[0])
            ymin, ymax = tuple(axes_limits[1])

            self.ax = self.fig.add_subplot(111)
            self.ax.set_xlim(xmin, xmax)
            self.ax.set_ylim(ymin, ymax)
            
            # Initialise button click event on local figure object
            self.cid = self.fig.canvas.mpl_connect("button_press_event", self.onclick)

            # Defines X and Y points and evaluates the derivatives at each point
            X, Y = np.meshgrid(np.linspace(xmin * (1 + self.quiver_expansion_factor), xmax * (1 + self.quiver_expansion_factor), 15),
                               np.linspace(ymin * (1 + self.quiver_expansion_factor), ymax * (1 + self.quiver_expansion_factor), 15))

            # If only single dimension plotted, time on the x-axis of the plot. dt/dt = 1, hence U is a mesh of ones.
            # V is the variable's derivative mesh, as is normally the case for a quiverplot
            if dimensions == 1:
                U = np.ones(X.shape)
                V = self.system.phasespace_eval(display_vars, (Y,))

            # If 2D system visualised, U and V are the usual meshes of variable derivatives at the respective points
            # in phase space.
            elif dimensions == 2:
                # For a system with system coords [w, x, y, z], eval_vector will be a NumPy array with coordinates
                # [w, x, y, z]
                eval_vector = self.derivative_expression_resolve(display_vars, dimensions, (X, Y))
                U, V = self.system.phasespace_eval(display_vars, eval_vector)
        
            # Sets up quiver plot
            self.quiver = self.ax.quiver(X, Y, U, V, pivot="middle")
            self.trajectory = self.ax.plot(0, 0) # Need an initial 'trajectory'

        #TODO: Three dimensional plotting
        def three_dimensions(display_vars, axes_limits):
            pass
        
        for var in display_vars:
            if not(var in self.system.system_coords): return 

        self.fig = plt.figure()
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
            one_or_two_dimensions(display_vars, axes_limits, self.dimensions)

        elif self.dimensions == 3:
            three_dimensions(display_vars, axes_limits)       

        plt.show()

    def onclick(self, event):
        """
        Function called upon mouse click event
        """
        # Only works if mouse click is on axis and the maximum number of trajectories has not been reached
        if not (event.inaxes == self.ax and self.trajectory_count < self.max_trajectories):
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

def one_D_example():
    phase_coords = ['x']
    eqns = ['x^2']
    params = {'a':1, 'b':0}
    t_f = 20
    t_r = -20

    sys = SystemOfEquations(phase_coords, eqns, params=params)
    plotter = PhaseSpacePlotter(sys, t_f, t_r)
    plotter.show_plot(['x'], np.array(((0, 10), (0, 2))))

def two_D_example():
    phase_coords = ['x', 'y']
    eqns = [
        'ax + by',
        'cx + dy'
    ]
    params = {
        'a': -1,
        'b': 5,
        'c': -4,
        'd': -2
    }
    t_f = 5
    t_r = -5

    sys = SystemOfEquations(phase_coords, eqns, params=params)
    plotter = PhaseSpacePlotter(sys, t_f, t_r)
    plotter.show_plot(['x', 'y'], np.array(((-10, 10), (-10, 10))))

if __name__ == "__main__":
    one_D_example()
    two_D_example()