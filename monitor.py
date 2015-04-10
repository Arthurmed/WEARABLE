
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui
from pyqtgraph.dockarea import *
import numpy as np
import math


class Monitor(QtGui.QMainWindow):
    def __init__(self, parent=None):

        DEBUGUER = 0
        QtGui.QMainWindow.__init__(self, parent)
        self.win = pg.GraphicsWindow()
        self.win.setWindowTitle('ARISTARKO MONITOR')
        self.win.resize(1200, 600)
        self.setCentralWidget(self.win)  # inserto el pg como una widget.

        #CONTROL VARIABLES
        self.len = 1000

        #creo un dock
        self.dock1 = QtGui.QDockWidget('prueba', self)  # creo un dock
        self.addDockWidget(QtCore.Qt.TopDockWidgetArea, self.dock1)

        #add the Dock to the layout
        self.gridLayout = QtGui.QGridLayout() # creo un grid dentro del dock
        self.gridLayout.addWidget(self.dock1, 0, 0, 2, 2)

        self.button = QtGui.QPushButton('hola')  # creo un botton en el dock


        #PLOTS DEL EDA
        self.p1 = self.win.addPlot(title="Electro-Dermal Activity")
        #set the range of Xdata
        self.p1.setRange(xRange=[-self.len, 0])
        self.p1.setLimits(xMax=0)
        #creating curve for EDA
        self.curve1 = self.p1.plot(pen=(255, 0, 0))
        #creating data vector
        self.eda = np.empty(self.len)

        #PLOTS DEL EMG
        self.win.nextRow()
        self.p2 = self.win.addPlot(title="Electromyogram")
        #set the range of Xdata
        self.p2.setRange(xRange=[-self.len, 0])
        self.p2.setLimits(xMax=0)
        #creating curve for EDA
        self.curve2 = self.p2.plot(pen=(0, 0, 255))
        #creating data vector
        self.emg = np.empty(self.len)

        #PLOTS DEL HRV
        self.win.nextRow()
        self.p3 = self.win.addPlot(title="Electrocardiogram")
        #set the range
        self.p3.setRange(xRange=[-self.len, 0])
        self.p3.setLimits(xMax=0)
        #creating curve for HRV
        self.curve3 = self.p3.plot(pen=(0, 255, 0))
        #creating data vector
        self.ecg = np.empty(self.len)

        #PLOTS DEL SKT
        self.win.nextRow()
        self.p4 = self.win.addPlot(title="Skin Temperature")
        #set the range
        self.p4.setRange(xRange=[-self.len, 0])
        self.p4.setLimits(xMax=0)
        #creating curve for SKT
        self.curve4 = self.p4.plot(pen=(0, 255, 255))
        # #creating data vector
        self.skt = np.empty(self.len)


        #solo para debuguear
        if DEBUGUER:
            self.timer = pg.QtCore.QTimer()
            self.timer.timeout.connect(self.update_eda_data)
            self.timer.start(100)

            self.timer2 = pg.QtCore.QTimer()
            self.timer2.timeout.connect(self.update_emg_data)
            self.timer2.start(1)

            self.timer3 = pg.QtCore.QTimer()
            self.timer3.timeout.connect(self.update_ecg_data)
            self.timer3.start(1)

            self.timer4 = pg.QtCore.QTimer()
            self.timer4.timeout.connect(self.update_skt_data)
            self.timer4.start(1000)

    def update_all(self, data1, data2, data3, data4):
        self.update_eda_data(data1)
        self.update_emg_data(data2)
        self.update_ecg_data(data3)
        self.update_skt_data(data4)

    def update_eda_data(self, data):

        #EDA
        self.eda = np.roll(self.eda, -1)  # shift data in the array one sample left
        self.eda[-1] = data
        self.curve1.setData(self.eda)
        self.curve1.setPos(-self.len, 0)  # marca para que sepa que tiene que coger 100 negativos

    def update_emg_data(self, data):

        #EMG
        self.emg = np.roll(self.emg, -1)  # shift data in the array one sample left
        self.emg[-1] = data
        self.curve2.setData(self.emg)
        self.curve2.setPos(-self.len, 0)  # marca para que sepa que tiene que coger 100 negativos

    def update_ecg_data(self, data):

        #ECG
        self.ecg = np.roll(self.ecg, -1)  # shift data in the array one sample left
        self.ecg[-1] = data
        self.curve3.setData(self.ecg)
        self.curve3.setPos(-self.len, 0)  # marca para que sepa que tiene que coger 100 negativos

    def update_skt_data(self, data):

        #SKT
        self.skt = np.roll(self.skt, -1)  # shift data in the array one sample left
        self.skt[-1] = data
        self.curve4.setData(self.skt)
        self.curve4.setPos(-self.len, 0)  # marca para que sepa que tiene que coger 100 negativos



if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        #QtGui.QApplication.instance().exec_()
        app = QtGui.QApplication(sys.argv)
        a = Monitor()
        a.show()
        sys.exit(app.exec_())