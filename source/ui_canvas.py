"""
Create a sample canvas that used to plot in the main window
"""
from matplotlib.backends.backend_qt5agg import(
    FigureCanvasQTAgg as FigCanvas,
    NavigationToolbar2QT as NavToolbar
)

import matplotlib.pyplot as plt
from matplotlib.figure import Figure
import random

class PlotCanvas(FigCanvas):
    
    def __init__(self):
        self.fig = Figure()
        self.axes = self.fig.add_subplot(111)
        FigCanvas.__init__(self, self.fig)
        
        self.plot()
    
    def plot(self):
        data = (1, 2, 3, 4, 5)
        self.axes.plot(data)
        self.draw()
        
if __name__ == "__main__":
    test = PlotCanvas()