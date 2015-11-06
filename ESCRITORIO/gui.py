#from PyQt4 import QtCore, QtGui
import sys
import time

from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph as pg
from pyqtgraph.dockarea import *

from ESCRITORIO.monitor2 import Monitor
from ports import serial_ports
from bolutec import BLE
from QLed import QLed


try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s


class MainGui2(QtGui.QMainWindow):
    def __init__(self, parent=None):
        QtGui.QMainWindow.__init__(self, parent)
        #set the main window
        self.resize(700, 400)
        self.setWindowTitle('MONITOR ARISTARKO')
        menubar = self.menuBar()
        self.statusBar()

        #CONTROL VARIABLES

        self.patient = {'name': '',
                        'surname': ''}

        self.fname = ''  # path del log
        self.f = ''



        ###### SET FRAMES
        #set dock area as central widget
        self.area = DockArea()
        self.setCentralWidget(self.area)  # inserto el pg como una widget central.

        #create docks and add them into dock area
        self.d1 = Dock("BLE CONNECTION", size=(100, 50), closable=True)
        self.d2 = Dock("CONTROLS", size=(200, 200))
        self.d3 = Dock("PATIENT INFO", size=(400, 100), closable=True)
        self.d4 = Dock("MAIN", size=(400, 200), closable=True)
        self.d5 = Dock("STATUS", size=(400, 200), closable=True)



        self.area.addDock(self.d1, 'left')
        self.area.addDock(self.d2, 'bottom')
        self.area.addDock(self.d5, 'bottom')
        self.area.addDock(self.d3, 'bottom')
        self.area.addDock(self.d4, 'right')

        #BLUETHOOTH LE
        self. ble = ''

        #MONITOR
        self.monitor = Monitor()

        ########################################
        #MENUS
        #######################################
        fileMenu = menubar.addMenu('&File')
        newMenu = fileMenu.addAction('New Patient')
        loadMenu = fileMenu.addAction('Load Patient')

        ######################################
        # create progress bar
        ######################################
        self.pb = QtGui.QProgressBar(self.statusBar())
        self.statusBar().addPermanentWidget(self.pb)
        self.statusBar().showMessage(self.tr("Parsing eventlog data..."))
        self.pb.setValue(50)


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
        ### DOCK2. BOTONES
        ##################################################
        self.w2 = pg.LayoutWidget()  # creo el layout
        self.d2.addWidget(self.w2)   # lo add al dock1

        monitorButton = QtGui.QPushButton('MONITOR')
        self.w2.addWidget(monitorButton, row=0, col=0)
        historicButton = QtGui.QPushButton('VIEWLER')
        self.w2.addWidget(historicButton, row=0, col=1)
        Button3 = QtGui.QPushButton('TODO')
        self.w2.addWidget(Button3, row=1, col=0)
        Button4 = QtGui.QPushButton('TODO')
        self.w2.addWidget(Button4, row=1, col=1)
        Button5 = QtGui.QPushButton('RECORDING')
        self.w2.addWidget(Button5, row=2, col=0, colspan=2)


        #signals
        self.connectButton.clicked.connect(self.ble_connect)
        monitorButton.clicked.connect(self.monitor_view)
        self.connect(newMenu, QtCore.SIGNAL('triggered()'), self.newDialog)
        self.connect(loadMenu, QtCore.SIGNAL('triggered()'), self.loadDialog)

        #################################################
        # DOCK3. PATIENT INFO
        #################################################

        self.w3 = pg.LayoutWidget()  # creo el layout
        self.d3.addWidget(self.w3)   # lo add al dock1
        name = QtGui.QLabel('Name:')
        self.name_label = QtGui.QLabel('')
        self.w3.addWidget(name, row=0, col=0)
        self.w3.addWidget(self.name_label, row=0, col=1)
        surname = QtGui.QLabel('Surname:')
        self.surname_label = QtGui.QLabel('')
        self.w3.addWidget(surname, row=0, col=2)
        self.w3.addWidget(self.surname_label, row=0, col=3)

        ##################################################
        #   DOCK 5. STATUS LEDS
        ##################################################

        self.led1 = QLed(self, onColour=QLed.Green, shape=QLed.Circle)
        self.led2 = QLed(self, onColour=QLed.Green, shape=QLed.Circle)
        self.led3 = QLed(self, onColour=QLed.Red, shape=QLed.Round)
        self.led4 = QLed(self, onColour=QLed.Red, shape=QLed.Round)

        self.w4 = pg.LayoutWidget()  # creo el layout
        self.d5.addWidget(self.w4)   # lo add al dock1

        self.w4.addWidget(QtGui.QLabel('WEARABLE: '), row=0, col=0)
        self.w4.addWidget(self.led1, row=0, col=1)
        self.w4.addWidget(QtGui.QLabel('DATABASE: '), row=0, col=2)
        self.w4.addWidget(self.led2, row=0, col=3)
        self.w4.addWidget(QtGui.QLabel('RECORDING FILE: '), row=1, col=0)
        self.w4.addWidget(self.led3, row=1, col=1)
        self.w4.addWidget(QtGui.QLabel('RECORDING DATABASE: '), row=1, col=2)
        self.w4.addWidget(self.led4, row=1, col=3)

        #QTHREADS
        self.worker = worker()
        self.connect(self.worker, QtCore.SIGNAL("thread_readdata()"), self.read_data, QtCore.Qt.DirectConnection)

    def newDialog(self):

        date = newDialog.getData()
        self.name_label.setText(date[0])
        self.surname_label.setText(date[1])
        if self.name_label.text():
            self.fname = './patients/' + self.name_label.text() + self.surname_label.text()
            self.f = open(self.fname, 'a')
            #cambiar LED a conectado

    def loadDialog(self):

        '''
        load the logfile into the variable self.data
        :return:
        '''

        self.fname = QtGui.QFileDialog.getOpenFileName(self, 'Open Log', '.\patients')
        if self.fname:  # si devuelve algo
            self.f = open(self.fname, 'a')
            #encender LED


    def ble_connect(self):
        #TODO:#cambia el boton de color#cambia variable de estado a connected
        #crea un objeto de BLE
        #scanea dispositivos
        if self.connectButton.isChecked():  # activamos
            ##TODO: Arreglar este lio con el BLE.
            #devices = self.ble.get_devices()
            #if not self.ble.get_state():
            #    self.ble.connect_device(devices)
            if not self.ble:
                self.ble = BLE('COM11', 9600)
                self.led1.toggleValue()
            if self.fname:
                try:
                    self.f = open(self.fname, 'a')
                except IOError:
                    print "ya esta abierto"

            self.worker.start()
            pass
        else:
            if self.worker.isRunning():
                self.worker.terminate()
                if self.fname:
                    try:
                        self.f.close()
                    except IOError:
                        print "ya esta cerrado"

    def read_data(self):

        # esto va por un hilo independiente
        #TODO: PAsar el ble a bytes
        #leo datos del device
        raw_data = self.ble.read_data()

        #los grabo en log
        if self.f:
            self.led2.toggleValue()
            self.f.write(raw_data)

        #actualizo el monitor
        raw_data = map(float, raw_data.split(','))
        self.monitor.update_all(raw_data[0], raw_data[1], raw_data[2], raw_data[3])

    def monitor_view(self):
        self.monitor.show()


    def closeEvent(self, event):

        quit_msg = "Are you sure you want to exit the program?"
        reply = QtGui.QMessageBox.question(self, 'Message',
                     quit_msg, QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)

        if reply == QtGui.QMessageBox.Yes:
            self.f.close()  # cierro el fichero
            self.ble.disconnect()  #desconecto el wearable
            event.accept()
        else:
            event.ignore()



################  THREADS##########################
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

########################DIALOGS

class newDialog(QtGui.QDialog):
    def __init__(self, parent = None):
        super(newDialog, self).__init__(parent)

        self.form = QtGui.QFormLayout()
        self.form.setHorizontalSpacing(0)

        self.line1 = QtGui.QLineEdit()
        self.line2 = QtGui.QLineEdit()
        self.form.addRow('Name: ', self.line1)
        self.form.addRow('Surname: ', self.line2)

        self.setLayout(self.form)
        self.setGeometry(300, 300, 400, 0)
        self.setWindowTitle('New Patient')

         # OK and Cancel buttons
        buttons = QtGui.QDialogButtonBox(
            QtGui.QDialogButtonBox.Ok | QtGui.QDialogButtonBox.Cancel,
            QtCore.Qt.Horizontal, self)

        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        self.form.addRow(buttons)

    def returndata(self):
        return [self.line1.text(), self.line2.text()]

    @staticmethod
    def getData(parent=None):
        dialog = newDialog(parent)
        result = dialog.exec_()
        date = dialog.returndata()
        return date




if __name__ == "__main__":


    app = QtGui.QApplication(sys.argv)
    myapp = MainGui2()
    myapp.show()
    sys.exit(app.exec_())
