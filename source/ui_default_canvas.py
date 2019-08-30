"""
Create a sample canvas that used to plot in the main window
"""


from trajectory import PhaseSpacePlotter
from equations import SystemOfEquations



class DefaultCanvas(PhaseSpacePlotter):

    def __init__(self):
        self.default_system = SystemOfEquations(["x", "y"],
            ["y", "-x"], params={})

        self.display_vars = self.default_system.system_coords
        self.dimensions = len(self.display_vars)

        super().__init__(
            self.default_system)
