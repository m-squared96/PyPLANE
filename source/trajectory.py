import numpy as np
import matplotlib.pyplot as plt

from equations import SystemOfEquations


class PhaseSpacePlotter(object):
    """
    Accepts a system of equations (equations.SystemOfEqutions object) and produces
    a phase plot. Individual trajectories evaluated upon click event.
    """
    def __init__(self, system, time_array, xaxis_lims=(-10, 10), yaxis_lims=(-10, 10),
                max_trajectories=10):

        self.system = system # SOE object
        self.fig = plt.figure() 
        self.ax = self.fig.add_subplot(111)
        self.xmin, self.xmax = xaxis_lims
        self.ymin, self.ymax = yaxis_lims

        # Initialise button click event on local figure object
        self.cid = self.fig.canvas.mpl_connect("button_press_event", self.onclick)

        self.time = time_array # Time steps for trajectory evaluation
        self.max_trajectories = max_trajectories # Maximum number of trajectories that can be visualised
        self.trajectory_count = 0 # Trajectory increment variable

        # Defines X and Y points and evaluates the derivatives at each point
        X, Y = np.meshgrid(np.arange(self.xmin, self.xmax, 1), np.arange(self.ymin, self.ymax, 1))
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

            # Trajectory production and plotting
            solution = self.system.solve(self.time, r0=np.array([x_event, y_event]))
            self.trajectory = self.ax.plot(solution[:, 0], solution[:, 1])
            self.fig.canvas.draw()
            self.trajectory_count += 1


def example():
    phase_coords = ['x', 'y']
    eqns = [
        'ax + by',
        'cx + dy'
    ]
    params = {'a': -1, 'b': 5, 'c': -4, 'd': -2}
    t = np.linspace(0, 40, 5000)

    sys = SystemOfEquations(phase_coords, eqns, params=params)
    plotter = PhaseSpacePlotter(sys, t)

if __name__ == "__main__":
    example()