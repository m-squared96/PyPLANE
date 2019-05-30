import numpy as np
import matplotlib.pyplot as plt

from equations import SystemOfEquations


class PhaseSpacePlotter(object):
    """
    Accepts a system of equations (equations.SystemOfEqutions object) and produces
    a phase plot. Individual trajectories evaluated upon click event.
    """
    def __init__(self, system, time_array_forward, time_array_reverse, xaxis_lims=(-10, 10), yaxis_lims=(-10, 10),
                max_trajectories=10, quiver_expansion_factor=0.2):

        self.system = system # SOE object
        self.quiver_expansion_factor = quiver_expansion_factor # Factor to expand quiverplot to ensure all visible regions plotted
        self.fig = plt.figure() 
        self.ax = self.fig.add_subplot(111)
        self.xmin, self.xmax = xaxis_lims
        self.ymin, self.ymax = yaxis_lims
        self.ax.set_xlim(self.xmin, self.xmax)
        self.ax.set_ylim(self.ymin, self.ymax)

        # Initialise button click event on local figure object
        self.cid = self.fig.canvas.mpl_connect("button_press_event", self.onclick)

        self.time_f = time_array_forward # Time steps for forward trajectory evaluation
        self.time_r = time_array_reverse # Time steps for reverse trajectory evaluation

        self.max_trajectories = max_trajectories # Maximum number of trajectories that can be visualised
        self.trajectory_count = 0 # Trajectory increment variable

        # Defines X and Y points and evaluates the derivatives at each point
        X, Y = np.meshgrid(np.linspace(self.xmin * (1 + self.quiver_expansion_factor), self.xmax * (1 + self.quiver_expansion_factor), 15),
                np.linspace(self.ymin * (1 + self.quiver_expansion_factor), self.ymax * (1 + self.quiver_expansion_factor), 15))
        U, V = self.system.phasespace_eval(t=None, r=np.array([X, Y]))

        # Sets up quiver plot
        self.quiver = self.ax.quiver(X, Y, U, V, pivot="middle")
        self.trajectory = self.ax.plot(0, 0) # Need an initial 'trajectory'

        plt.show()

    def onclick(self, event):
        """
        Function called upon mouse click event
        """
        # Only works if mouse click is on axis and the maximum number of trajectories has not been reached
        if event.inaxes == self.ax and self.trajectory_count < self.max_trajectories:
            
            # Mouse click coordinates
            x_event = event.xdata
            y_event = event.ydata

            self.ax.plot(x_event, y_event, ls="", marker="x", c="#FF0000")

            # Trajectory production and plotting
            solution_f = self.system.solve(self.time_f, r0=np.array([x_event, y_event]))
            solution_r = self.system.solve(self.time_r, r0=np.array([x_event, y_event]))

            for sol in (solution_f, solution_r):
                self.trajectory = self.ax.plot(sol[:, 0], sol[:, 1], c="#0066FF")
                self.fig.canvas.draw()

            self.trajectory_count += 1

        else:
            pass


def example():
    phase_coords = ['x', 'y']
    eqns = [
        'ax + by',
        'cx + dy'
    ]
    params = {'a': -1, 'b': 5, 'c': -4, 'd': -2}
    t_f = np.linspace(0, 40, 5000)
    t_r = np.linspace(0, -5, 625)

    sys = SystemOfEquations(phase_coords, eqns, params=params)
    plotter = PhaseSpacePlotter(sys, t_f, t_r)

if __name__ == "__main__":
    example()