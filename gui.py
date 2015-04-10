#from PyQt4 import QtCore, QtGui
from pyqtgraph.Qt import QtGui, QtCore
from main_window import Ui_MainWindow
import pyqtgraph as pg
import numpy as np
from pyqtgraph.dockarea import *
from monitor2 import Monitor
from screen import Screen
from historic import Historic
import sys
from ports import serial_ports
from ble import BLE
import threading
import time
from multiprocessing import Queue, Process
import os

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s


class MainGui(QtGui.QMainWindow, Ui_MainWindow):

    def __init__(self, parent=None):

        DEBUG = 1
        super(MainGui, self).__init__(parent)
        #QtGui.QMainWindow.__init__(self, parent)

        #setup the user interface from designer
        #self.ui = Ui_MainWindow()
        self.setupUi(self)
        #define signals
        self.attitude_button.clicked.connect(self.onHistoric)
        self.connect_button.clicked.connect(self.onConnect)
        #para el monitor
        #self.view = pg.GraphicsView()
        #self.setCentralWidget(self.view)

        #MONITOR
        self.monitor = Monitor(self)  # object from monitor
        self.historico = Historic(self)
        self.screen = Screen(self)  #

        #SCREEN
        #self.screen = Screen(self)

        if DEBUG:

            self.timer = QtCore.QTimer()
            self.timer.timeout.connect(self.read_data_from_device)
            self.timer.start(1)

    def onConnect(self):
        self.monitor.show()

    def onHistoric(self):
        self.historico.show()

    def read_data_from_device(self):
        #coje data de BLE
        #actualiza el monitor
        data = np.random.normal()
        self.monitor.update_all(data, data, data, data)

    def run_monitor(self):
        pass


class MainGui2(QtGui.QMainWindow):
    def __init__(self, parent=None):
        QtGui.QMainWindow.__init__(self, parent)
        #set the main window
        self.resize(1000, 800)
        self.setWindowTitle('MONITOR ARISTARKO')
        self.menuBar()
        self.statusBar()
        #CONTROL VARIABLES

        #set dock area as central widget
        self.area = DockArea()
        self.setCentralWidget(self.area)  # inserto el pg como una widget central.

        #create docks and add them into dock area
        self.d1 = Dock("BLE CONNECTION", size=(100, 50), closable=True)
        self.d2 = Dock("CONTROLS", size=(200, 300))
        self.d3 = Dock("FOCUS", size=(400, 300), closable=True)
        self.d4 = Dock("MAIN", size=(400, 200), closable=True)

        self.area.addDock(self.d1, 'left')
        self.area.addDock(self.d2, 'bottom')
        self.area.addDock(self.d3, 'bottom')
        self.area.addDock(self.d4, 'right')

        #BLUETHOOTH LE
        self. ble = BLE('COM11', 9600)

        #MONITOR
        self.monitor = Monitor()

        ########################################
        #DOCK 1
        #######################################
        #layout for dock1, BLE
        self.w1 = pg.LayoutWidget()  # creo el layout
        self.d1.addWidget(self.w1)   # lo add al dock1

        #widgets
        labelPort = QtGui.QLabel('Port:')
        self.w1.addWidget(labelPort, row=0, col=0)
        comboBoxPort = QtGui.QComboBox(self)
        #comboBoxPort.setGeometry(QtCore.QRect(0, 0, 50, 24))
        comboBoxPort.setEditable(False)
        self.w1.addWidget(comboBoxPort, row=1, col=0)
        [comboBoxPort.addItem(i) for i in serial_ports()]
        labelBaud = QtGui.QLabel('BaudRate:')
        self.w1.addWidget(labelBaud, row=0, col=1)
        comboBoxBaud = QtGui.QComboBox(self)
        #comboBoxBaud.setGeometry(QtCore.QRect(0, 0, 50, 24))
        comboBoxBaud.setEditable(False)
        self.w1.addWidget(comboBoxBaud, row=1, col=1)
        baudlist = ['1200', '2400', '4800', '9600', '19200', '57600', '115200']
        [comboBoxBaud.addItem(i) for i in baudlist]
        self.connectButton = QtGui.QPushButton('CONNECT')
        self.connectButton.setCheckable(True)
        scanButton = QtGui.QPushButton('SCAN PORTS')
        self.w1.addWidget(self.connectButton, row=2, col=1)
        self.w1.addWidget(scanButton, row=2, col=0)

        ##################################################
        ### DOCK2
        ##################################################
        self.w2 = pg.LayoutWidget()  # creo el layout
        self.d2.addWidget(self.w2)   # lo add al dock1

        monitorButton = QtGui.QPushButton('MONITOR')
        self.w2.addWidget(monitorButton, row=0, col=0)

        #signals
        self.connectButton.clicked.connect(self.ble_connect)
        monitorButton.clicked.connect(self.monitor_view)

        #QTHREADS
        self.worker = worker()
        self.connect(self.worker, QtCore.SIGNAL("thread_readdata()"), self.read_data, QtCore.Qt.DirectConnection)


    def ble_connect(self):
        #TODO:#cambia el boton de color#cambia variable de estado a connected
        #crea un objeto de BLE
        #scanea dispositivos
        if self.connectButton.isChecked():  # activamos
        #TODO: Arreglar este lio con el BLE.
        #devices = self.ble.get_devices()
        #if not self.ble.get_state():
        #    self.ble.connect_device(devices)
            self.worker.start()
        else:
            if self.worker.isRunning():
                self.worker.terminate()

    def read_data(self):
        #TODO: PAsar el ble a bytes
        raw_data = self.ble.read_data()
        raw_data = map(float, raw_data.split(','))
        self.monitor.update_all(raw_data[0], raw_data[1], raw_data[2], raw_data[3])

    def monitor_view(self):
        self.monitor.show()




class worker(QtCore.QThread):
    def __init__(self, parent=None):
        super(worker, self).__init__(parent)
        self.running = False


    def run(self):
        print'hola'
        #time.sleep(10)
        self.running = True
        while self.running:
            self.emit(QtCore.SIGNAL("thread_readdata()"))
            time.sleep(0.1)




if __name__ == "__main__":


    app = QtGui.QApplication(sys.argv)
    myapp = MainGui2()
    myapp.show()
    sys.exit(app.exec_())
