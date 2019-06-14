"""
Create a sample canvas that used to plot in the main window
"""


from trajectory import PhaseSpacePlotter
from equations import SystemOfEquations

class DefaultCanvas(PhaseSpacePlotter):
    
    def __init__(self):
        self.default_system = SystemOfEquations(["x", "y"], ["y*sin(x)", "-x"], params={})
        super().__init__(self.default_system, 5, -5)