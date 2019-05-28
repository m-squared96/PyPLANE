import numpy as np
import matplotlib.pyplot as plt

import equations


class PhaseSpacePlotter(object):

    def __init__(self, ax, trajectory_length, xaxis_lims=(-10, 10), yaxis_lims=(-10, 10),
                max_trajectories=10):

        self.fig = ax.figure
        self.ax = ax
        self.xaxis_lims = xaxis_lims
        self.yaxis_lims = yaxis_lims
        self.cid = self.fig.canvas.mpl_connect("button_press_event", self.onclick)
        self.trajectory_length = trajectory_length
        self.max_trajectories = max_trajectories
        self.trajectory_count = 0

        X, Y = np.meshgrid(np.arange(self.xaxis_lims[0], self.xaxis_lims[1], 1), np.arange(self.yaxis_lims[0], self.yaxis_lims[1], 1))
        U, V = xprime(X, Y), yprime(X, Y)

        self.quiver = self.ax.quiver(X, Y, U, V, pivot="middle")
        self.trajectory = self.ax.plot(0, 0)

        plt.show()

    def onclick(self, event):
        
        if event.inaxes == self.ax and self.trajectory_count <= self.max_trajectories:

            x_event = event.xdata
            y_event = event.ydata

            solution = parameter_placeholder(x_event, y_event)
            self.trajectory = self.ax.plot(solution[:, 0], solution[:, 1])
            self.fig.canvas.draw()
            self.trajectory_count += 1

def xprime(x, y):
    return -1*x + 5*y

def yprime(x, y):
    return -4*x + -2*y

def parameter_placeholder(x_init, y_init):

    phase_coords = ['x', 'y']
    eqns = [
        'ax + by',
        'cx + dy'
    ]
    params = {'a': -1, 'b': 5, 'c': -4, 'd': -2}
    r0 = [x_init, y_init]
    t = np.linspace(0, 40, 5000)

    sys = equations.SystemOfEquations(phase_coords, eqns, params=params)
    print(sys)
    sol = sys.solve(t, r0)

    return sol

def example():
    fig = plt.figure()
    ax = fig.add_subplot(111)
    app = PhaseSpacePlotter(ax, 5000)

if __name__ == "__main__":
    example()