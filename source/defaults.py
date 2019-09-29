import numpy as np

from equations import SystemOfEquations
from trajectory import PhaseSpacePlotter


def psp_by_dimensions(dims):

    if dims == 1:
        return one_dimensional_default()
    if dims == 2:
        return two_dimensional_default()


def one_dimensional_default():

    phase_coords = ["x"]
    eqns = ["sin(x)"]
    params = {"a": 1, "b": 0}
    t_f = 20
    t_r = -20

    xmin = -10
    xmax = 10
    ymin = -10
    ymax = 10

    sys = SystemOfEquations(phase_coords, eqns, params=params)
    return PhaseSpacePlotter(
        sys, t_f, t_r, np.array(((0, 10), (0, 10))), quiver_expansion_factor=0.2
    )


def two_dimensional_default():

    phase_coords = ["x", "y"]
    eqns = ["ax - y + b(x^2-y^2) + axy", "x - cy - d(x^2-y^2) + cxy"]
    params = {"a": 2, "b": 3, "c": 3, "d": 3}
    t_f = 50
    t_r = -50

    xmin = -10
    xmax = 10
    ymin = -10
    ymax = 10

    sys = SystemOfEquations(phase_coords, eqns, params=params)
    return PhaseSpacePlotter(sys, t_f, t_r, np.array(((xmin, xmax), (ymin, ymax))))


default_1D = {
    "system_coords": ["x"],
    "ode_expr_strings": ["a*sin(bx)"],
    "params": {"a": 1, "b": 1},
    "t_f": 20,
    "t_r": -20,
    "axes_limits": ((-10, 10), (-10, 10)),
    "xmin": -10,
    "xmax": 10,
    "ymin": -10,
    "ymax": 10,
}

default_2D = {
    "system_coords": ["x", "y"],
    "ode_expr_strings": ["ax - y + b(x^2-y^2) + axy", "x - cy - d(x^2-y^2) + cxy"],
    "params": {"a": 2, "b": 3, "c": 3, "d": 3},
    "t_f": 10,
    "t_r": -10,
    "axes_limits": ((-10, 10), (-10, 10)),
    "xmin": -10,
    "xmax": 10,
    "ymin": -10,
    "ymax": 10,
}
