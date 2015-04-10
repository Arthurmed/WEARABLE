import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui
from pyqtgraph.dockarea import *
import numpy as np
import math
import time


class Historic(QtGui.QMainWindow):
    def __init__(self, parent=None):

        DEBUGUER = 0
        QtGui.QMainWindow.__init__(self, parent)
        self.resize(1000, 800)
        self.setWindowTitle('HISTORICO ARISTARKO')

        #CONTROL VARIABLES
        #TODO: mejor meter en un dictionary
        self.data = np.array([])

        #set dock area as central widget
        self.area = DockArea()
        self.setCentralWidget(self.area)  # inserto el pg como una widget.

        #create docks and add them into dock area
        self.d1 = Dock("Controls", size=(200, 50), closable=True)
        self.d2 = Dock("Plots", size=(600, 480))
        #self.d3 = Dock("FOCUS", size=(400, 400), closable=True)
        self.area.addDock(self.d1, 'left')
        self.area.addDock(self.d2)

        #create a layout for dock 1. I am going to introduce more widgets
        self.w1 = pg.LayoutWidget()

        ###########################################
        #create widgets and move into each dock
        ###########################################

        #open file action
        openfile = QtGui.QAction(QtGui.QIcon('open.png'), 'Open Log', self)
        openfile.setShortcut('Ctrl+O')
        openfile.setStatusTip('Open new File')
        openfile.triggered.connect(self.showDialog)

        # menu bar
        menubar = self.menuBar()  # activo la barra de menu
        fileMenu = menubar.addMenu('&File')  # adding the menu
        fileMenu.addAction(openfile)  #le pongo la action

        ##########################################
        #graphics
        ##########################################

        self.win = pg.GraphicsWindow()
        self.win.resize(600, 600)
        self.win.setWindowTitle('ARISTARKO MONITOR')
        self.d2.addWidget(self.win)  #adding a dock2
        self.p1 = self.win.addPlot()
        self.win.nextRow()
        self.p2 = self.win.addPlot()

        #regions
        self.region = pg.LinearRegionItem()
        self.region.setZValue(10)
        self.p2.addItem(self.region, ignoreBounds=True)
        self.p1.setAutoVisible(y=True)
        self.region.setRegion([1000, 2000])

        #controls
        self.button = QtGui.QPushButton('PLOT')
        self.w1.addWidget(self.button, row=0, col=0)
        self.d1.addWidget(self.w1)

        #SIGNALS
        self.button.clicked.connect(self.plotSignals)
        self.region.sigRegionChanged.connect(self.updateRange)
        self.p1.sigRangeChanged.connect(self.updateRegion)

    def showDialog(self):

        '''
        load the logfile into the variable self.data
        :return:
        '''

        fname = QtGui.QFileDialog.getOpenFileName(self, 'Open Log', '.\patients')
        f = open(fname, 'r')

        with f:
            raw_data = f.read()
            raw_data = raw_data.split('\n')
            #TODO: quitar datos del raw_data
        aa = np.zeros((len(raw_data), 4))

        for i, line in enumerate(raw_data[1:-1]):
            al, fields = aa[i], line.split(',')
            al[0], al[1], al[2], al[3] = \
                float(fields[2]), float(fields[3]), float(fields[4]), float(fields[5])

        self.data = aa

    def plotSignals(self):
        self.p1.plot(self.data[:-2, 1], pen="r")
        self.p1.plot(self.data[:-2, 2], pen="g")
        self.p2.plot(self.data[:-2, 1], pen="r")

    def updateRange(self):
        self.region.setZValue(10)
        minX, maxX = self.region.getRegion()
        self.p1.setXRange(minX, maxX, padding=0)

    def updateRegion(self, window, viewRange):
        rgn = viewRange[0]
        self.region.setRegion(rgn)


if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        #QtGui.QApplication.instance().exec_()
        app = QtGui.QApplication(sys.argv)
        a = Historic()
        a.show()
        sys.exit(app.exec_())