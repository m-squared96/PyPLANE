import numpy as np

from PyPLANE.equations import SystemOfEquations
from PyPLANE.trajectory import PhaseSpace2D
from PyPLANE.gallery import Gallery


def psp_by_dimensions(dims) -> PhaseSpace2D:

    if dims == 1:
        return one_dimensional_default()
    if dims == 2:
        return two_dimensional_default()
    # TODO what do we do in other dimensions?


def one_dimensional_default() -> dict:

    gallery_1D = Gallery("resources/gallery_1D.json", 1)
    default_sys = "Example system - sine wave"
    sys_params = gallery_1D.get_system(default_sys)
    return sys_params


def two_dimensional_default() -> dict:

    gallery_2D = Gallery("resources/gallery_2D.json", 2)
    default_sys = "Van der Pol's Equation"
    sys_params = gallery_2D.get_system(default_sys)
    return sys_params
