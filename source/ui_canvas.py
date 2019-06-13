"""
Create a sample canvas that used to plot in the main window
"""
from matplotlib.backends.backend_qt5agg import(
    FigureCanvasQTAgg as FigCanvas,
    NavigationToolbar2QT as NavToolbar
)

import matplotlib.pyplot as plt
import random

class PlotCanvas(FigCanvas):
    
    def __init__(self):
        fig = plt.figure()
        self.axes = plt.add_subplot(111)
        super().__init__(self, fig)
        
        self.plot()
    
    def plot(self):
        data = [random.randint for i in range(40)]
        self.axes.plot(data)
        self.draw()
        
if __name__ == "__main__":
    test = PlotCanvas()