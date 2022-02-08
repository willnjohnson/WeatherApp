import matplotlib
import matplotlib.pyplot as plt
import matplotlib.dates as dates
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

class HistoryGraph:
    def __init__(self):
        self.xValues = []
        self.yValues = []
        self.xLabel = ''
        self.yLabel = ''
        self.canvas = FigureCanvas()

    def setValues(self, values):
        for [a,b] in values:
            d = matplotlib.dates.datestr2num(b)
            self.xValues.append(d)
            self.yValues.append(a)

    def setLabels(self, xLabel, yLabel):
        self.xLabel = xLabel
        self.yLabel = yLabel

    def createGraph(self):
        figure, ax = plt.subplots()
        plt.plot(self.xValues, self.yValues)
        plt.xlabel(self.xLabel)
        plt.ylabel(self.yLabel)
        ax.xaxis.set_major_locator(dates.DayLocator(interval=2))
        ax.xaxis.set_major_formatter(dates.DateFormatter("%d"))
        plt.setp(ax.get_xticklabels(), rotation=30, ha='right')
        self.canvas = FigureCanvas(figure)