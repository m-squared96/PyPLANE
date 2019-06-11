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

        self.ax.plot(x_event, y_event, ls="", marker="x", c="#FF0000")

        # Trajectory production and plotting
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
            else:
                print(sol.message)

        self.trajectory_count += 1

    def derivative_expression_resolve(self, display_vars, dimensions, positions):
        eval_seq = []
        for var in self.system.system_coords:
            if not(var in display_vars): eval_seq.append(0)
            
            elif var in display_vars:
                eval_seq.append(positions[display_vars.index(var)])

        return np.array(eval_seq)

def example():
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
    example()