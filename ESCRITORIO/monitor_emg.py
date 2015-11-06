import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui
from pyqtgraph.dockarea import *
import numpy as np
import sys
import time
import threading
import random
import serial
import struct



class Monitor_EMG(QtGui.QMainWindow):
    def __init__(self, parent=None):

        self._DEBUGUER = 0
        QtGui.QMainWindow.__init__(self, parent)
        # set the main window
        self.resize(1000, 800)
        self.setWindowTitle('MONITOR EMG')

        #CONTROL VARIABLES
        self.len = 5000
        self.ser = serial.Serial('COM6', 115200, timeout=0.1)
        self.ser.flush()

        #set dock area as central widget
        self.area = DockArea()
        self.setCentralWidget(self.area)  # inserto el pg como una widget central.

        #create docks and add them into dock area
        self.d1 = Dock("Controls", size=(200, 50), closable=True)
        self.d2 = Dock("Plots", size=(600, 480))
        #self.d3 = Dock("events", size=(600, 100))
        #self.d3 = Dock("FOCUS", size=(400, 400), closable=True)
        self.area.addDock(self.d1, 'left')
        self.area.addDock(self.d2)
        #self.area.addDock(self.d3, 'bottom')





        #pyqtgraph
        self.win = pg.GraphicsWindow()
        self.win.resize(600, 600)
        self.win.setWindowTitle('ARISTARKO MONITOR')
        #self.win2 = pg.GraphicsWindow()



        #move gidgets into docks

        #timers
        self.timer = pg.QtCore.QTimer()
        self.timer.timeout.connect(self.update_emg_data)
        self.timer.start(0.1)

        self.timer2 = pg.QtCore.QTimer()
        self.timer2.timeout.connect(self.update_emg_plot)
        self.timer2.start(10)


        ######################################################
        ####################### PLOTS ########################
        ######################################################

        #PLOTS DEL EDA
        self.p1 = self.win.addPlot(title="EMG Test")
        #set the range of Xdata
        self.p1.setRange(xRange=[-self.len, 0])
        self.p1.setLimits(xMax=0)

        #creating curve for EDA
        self.curve1 = self.p1.plot(pen=(255, 0, 0), clickable=True)
        self.emg = np.zeros(self.len)



    def update_emg_data(self):

        # EMG
        try:
            value = self.ser.readline()
            print value

            self.emg = np.roll(self.emg, -1)  # shift data in the array one sample left
            try:
                self.emg[-1] = float(value)
            except:
                print 'no hay dato del mc'
                self.emg[-1] = 0
        except:
            pass



    def update_emg_plot(self):

        self.curve1.setData(self.emg)
        self.curve1.setPos(-self.len, 0)  # marca para que sepa que tiene que coger 100 negativos

    def closeEvent(self, event):
        print 'closing'
        self.close()





app = QtGui.QApplication(sys.argv)
a = Monitor_EMG()
a.show()
sys.exit(app.exec_())


