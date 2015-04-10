
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui
from pyqtgraph.dockarea import *
import numpy as np
import math
import time


class Monitor(QtGui.QMainWindow):
    def __init__(self, parent=None):

        DEBUGUER = 0
        QtGui.QMainWindow.__init__(self, parent)
        #set the main window
        self.resize(1000, 800)
        self.setWindowTitle('MONITOR ARISTARKO')

        #CONTROL VARIABLES
        self.len = 100
        self.focus = False

        #set dock area as central widget
        self.area = DockArea()
        self.setCentralWidget(self.area)  # inserto el pg como una widget central.

        #create docks and add them into dock area
        self.d1 = Dock("Controls", size=(200, 50), closable=True)
        self.d2 = Dock("Plots", size=(600, 480))
        #self.d3 = Dock("FOCUS", size=(400, 400), closable=True)
        self.area.addDock(self.d1, 'left')
        self.area.addDock(self.d2)
        #self.area.addDock(self.d3, 'right')

        #create a layout for dock 1. I am going to introduce more widgets
        self.w1 = pg.LayoutWidget()
        self.w2 = pg.LayoutWidget()

        #create widgets and move into each dock

        #checkboxes
        edacb = QtGui.QCheckBox('EDA', self)
        emgcb = QtGui.QCheckBox('EMG', self)
        ecgcb = QtGui.QCheckBox('ECG', self)
        sktcb = QtGui.QCheckBox('SKT', self)
        edacb.toggle()
        emgcb.toggle()
        ecgcb.toggle()
        sktcb.toggle()


        #slider
        self.label1 = QtGui.QLabel("Longitud",)
        self.slider1 = QtGui.QSlider()
        self.slider1.setOrientation(QtCore.Qt.Horizontal)
        self.slider1.setRange(0, 99)
        self.slider1.setValue(1)

        #pyqtgraph
        self.win = pg.GraphicsWindow()
        self.win.resize(600, 600)
        self.win.setWindowTitle('ARISTARKO MONITOR')
        #self.win2 = pg.GraphicsWindow()


        #locate widgets into layout
        #self.w1.addWidget(self.button, row=0, col=0)
        self.w1.addWidget(self.label1, row=1, col=0)
        self.w1.addWidget(self.slider1, row=1, col=1, colspan=2)
        self.w1.addWidget(edacb, row=2, col=0)
        self.w1.addWidget(emgcb, row=2, col=1)
        self.w1.addWidget(ecgcb, row=2, col=2)
        self.w1.addWidget(sktcb, row=2, col=3)

        #self.w2.addWidget(self.win, row=0, col=0)

        #move gidgets into docks
        self.d1.addWidget(self.w1)
        self.d2.addWidget(self.win)
        #self.d3.addWidget(self.win2)



        ######################################################
        ####################### PLOTS ########################
        ######################################################

        #PLOTS DEL EDA
        self.p1 = self.win.addPlot(name="EDA", title="Electro-Dermal Activity")
        #set the range of Xdata
        self.p1.setRange(xRange=[-self.len, 0])
        self.p1.setLimits(xMax=0)

        #creating curve for EDA
        self.curve1 = self.p1.plot(pen=(255, 0, 0), clickable=True)
        #self.curve1.sigPointsClicked.connect(self.plotClicked)
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

        #PLOTS DEL FOCUS
        #self.win.nextRow()
        #self.p5 = self.win2.addPlot(title="FOCUS", name='FOCUS')
        #self.p5.setRange(xRange=[-self.len, 0])
        #self.p5.setLimits(xMax=0)
        #self.curve5 = self.p5.plot(pen=(0, 255, 255))
        #self.p5.setYLink(self.p1)
        #self.p5.setXLink(self.p1)

        #SIGNALS
        self.slider1.valueChanged.connect(self.scale)
        self.win.scene().sigMouseClicked.connect(self.onClick)
        edacb.stateChanged.connect(self.toggleEda)
        emgcb.stateChanged.connect(self.toggleEmg)
        ecgcb.stateChanged.connect(self.toggleEcg)
        sktcb.stateChanged.connect(self.toggleSkt)
        self.p = [self.p1, self.p2, self.p3, self.p4]

        #TEST
        #self.lay = pg.GraphicsWindow()
        #self.lay.addItem(self.p1)

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

    def scale(self, value):

        print value
        if value * 100 > self.len:
            aux = np.empty(value * 100 - self.len)
            self.eda = np.append(aux, self.eda)
            self.emg = np.append(aux, self.emg)
            self.ecg = np.append(aux, self.ecg)
            self.skt = np.append(aux, self.skt)

        else:
            self.eda = self.eda[0:-value]
            self.emg = self.emg[0:-value]
            self.ecg = self.ecg[0:-value]
            self.skt = self.skt[0:-value]

        self.len = value * 100
        self.p1.setRange(xRange=[-self.len, 0])
        self.p2.setRange(xRange=[-self.len, 0])
        self.p3.setRange(xRange=[-self.len, 0])
        self.p4.setRange(xRange=[-self.len, 0])

    def closeEvent(self, event):
        print 'closing'
        self.destroy()

    def onClick(self, event):

        items = self.win.scene().items(event.scenePos())[2]

        if not self.focus:

            if items in self.p:
                plot = self.p[self.p.index(items)]  # averiguo que plot es
                self.p.remove(plot)  # lo quito de la lista
                #elimino y adding el resto

                for i in self.p:
                    self.win.removeItem(i)
                self.focus = True

        else:
            for i in self.p:
                self.win.nextRow()
                self.win.addItem(i)
            self.focus = False
            self.p.append(items)

    def toggleEda(self, state):

        if state != QtCore.Qt.Checked:
            self.win.removeItem(self.p1)
        else:
            self.win.nextRow()
            self.win.addItem(self.p1)

    def toggleEmg(self, state):

        if state != QtCore.Qt.Checked:
            self.win.removeItem(self.p2)
        else:
            self.win.nextRow()
            self.win.addItem(self.p2)

    def toggleEcg(self, state):

        if state != QtCore.Qt.Checked:
            self.win.removeItem(self.p3)
        else:
            self.win.nextRow()
            self.win.addItem(self.p3)

    def toggleSkt(self, state):

        if state != QtCore.Qt.Checked:
            self.win.removeItem(self.p4)
        else:
            self.win.nextRow()
            self.win.addItem(self.p4)

if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        #QtGui.QApplication.instance().exec_()
        app = QtGui.QApplication(sys.argv)
        a = Monitor()
        a.show()
        sys.exit(app.exec_())