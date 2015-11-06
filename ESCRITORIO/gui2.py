# from PyQt4 import QtCore, QtGui
import sys
import subprocess
from multiprocessing import Queue

from pyqtgraph.Qt import QtGui, QtCore
#import MySQLdb
import serial

from main_frame import Ui_MainWindow
from load_experiment_frame import Ui_Dialog
from database_connect_frame import Ui_database_Dialog
from ESCRITORIO.monitor2 import Monitor
from screen import Screen
from ports import serial_ports
from QLed import QLed


try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s


#TODO LIST:
# Ajustar imagenes a pantalla

class MainGui2(QtGui.QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):

        super(MainGui2, self).__init__(parent)
        self.setupUi(self)  # cargamos la ui


        #CONTROL VARIABLES
        self.patient = []  # almacena info del paciente  # TODO: change by dict
        self.fname = ''  # path del log
        self.f = ''
        self.Q = Queue()  # para actualizar el monitor
        self.Q2 = Queue()  # para actualizar la base de datos
        self.data_event = 0

        #CONTROL EXPERIMENTO
        self.images = []
        self.duration = 0
        self.silence = 0
        self.experiment_duration = 0


        # BLE
        self.ble = serial.Serial()  # declaro el puerto

        #MONITOR
        self.monitor = Monitor()

        #SCREEN
        self.screen = Screen()

        #DATABASE
        self.db = None
        self.cur = None

        ###################################
        # DOCK1
        ###################################
        [self.port_combobox.addItem(i) for i in serial_ports()]

        ######################################
        #MAINFRAME
        #######################################

        #LEDS
        self.pc_led = QLed()
        self.pc_led.setOnColour(QLed.Green)
        self.pc_led.setOffColour(QLed.Red)

        self.experiment_led = QLed()
        self.experiment_led.setOffColour(QLed.Red)
        self.experiment_led.setOnColour(QLed.Green)

        self.patient_led = QLed()
        self.patient_led.setOffColour(QLed.Red)
        self.patient_led.setOnColour(QLed.Green)

        self.recording_led = QLed()
        self.recording_led.setOffColour(QLed.Red)
        self.recording_led.setOnColour(QLed.Blue)

        self.gridLayout_2.addWidget(self.pc_led, 0, 1, 1, 1)
        self.gridLayout_2.addWidget(self.experiment_led, 1, 1, 1, 1)
        self.gridLayout_2.addWidget(self.patient_led, 2, 1, 1, 1)
        self.gridLayout_2.addWidget(self.recording_led, 3, 1, 1, 1)

        #IMAGE
        #qpix = QtGui.QPixmap('flor.jpeg')
        #qpix = qpix.scaled(300, 300, QtCore.Qt.KeepAspectRatio)
        #self.central_image.setPixmap(qpix)
        #PROGRESS BAR
        #self.progressBar.setValue(0)
        self.setCentralWidget(self.monitor)

        ######################################
        #TABLE PATIENT INFO
        #######################################
        self.fillPatientTable()

        #SIGNALS
        self.connect(self.actionMonitor, QtCore.SIGNAL('triggered()'), self.monitor_view)
        self.connect(self.actionScreen, QtCore.SIGNAL('triggered()'), self.screen_view)
        self.connect(self.actionProcessing, QtCore.SIGNAL('triggered()'), self.viewler_view)
        self.connect_button.clicked.connect(self.pc_connect)
        self.scandevices_button.clicked.connect(self.scan_bluethoot_devices)
        self.pair_device_button.clicked.connect(self.pair_bluethoot_devices)
        self.run_button.clicked.connect(self.run_device)

        self.connect(self.actionNew_Patient, QtCore.SIGNAL('triggered()'), self.newDialog)
        self.connect(self.actionLoad_Patient, QtCore.SIGNAL('triggered()'), self.loadDialog)
        self.connect(self.actionNew_Experiment, QtCore.SIGNAL('triggered()'), self.newExperimentDialog)
        self.connect(self.actionLoad_experiment, QtCore.SIGNAL('triggered()'), self.loadExperimentDialog)
        self.connect(self.actionConnectDatabase, QtCore.SIGNAL('triggered()'), self.connectDatabase)
        self.connect(self.freq_comboBox, QtCore.SIGNAL("currentIndexChanged(const QString&)"), self.changeFrequency)

        #QTHREADS
        self.worker = worker()
        self.connect(self.worker, QtCore.SIGNAL("thread_readdata()"), self.read_data, QtCore.Qt.DirectConnection)
        self.worker2 = worker2()
        self.connect(self.worker2, QtCore.SIGNAL("thread_loopmonitor()"), self.monitor_loop, QtCore.Qt.DirectConnection)
        self.worker3 = worker3()
        self.connect(self.worker3, QtCore.SIGNAL("thread_writedatabase()"), self.newDataDB, QtCore.Qt.DirectConnection)

        #QTIMERS FOR RUNNING EXPERIMENT
        self.timer = QtCore.QTimer()
        self.connect(self.timer, QtCore.SIGNAL('timeout()'), self.run_experiment)


    def run_experiment(self):

        if self.images:
            #for screen
            image = self.images.pop(0)
            self.screen.update_image(image)
            self.data_event = 1 if self.data_event == 0 else 0
            #for main_frame
            qpix = QtGui.QPixmap(image)
            qpix = qpix.scaled(300, 300, QtCore.Qt.KeepAspectRatio)
            self.central_image.setPixmap(qpix)
            if not self.progressBar.isEnabled():
                self.progressBar.setEnabled()
            self.progressBar.setValue((float(len(self.images)) / self.experiment_duration) * 100)

            if image == '':  # viene silencio
                self.timer.stop()
                self.timer.start(self.duration * 1000)
            else:
                self.timer.stop()
                self.timer.start(self.duration * 1000)

        else:
            self.screen.close()
            self.timer.stop()
            self.experiment_led.setValue(0)


    def monitor_loop(self):

        raw_data = self.Q.get()
        print raw_data
        try:
            #TODO: Una vez checked, no vuelve a actualizar los plots!!
            self.monitor.update_all(raw_data[0], raw_data[1], raw_data[2], self.data_event)
        except:
            print 'hola'
            pass

    def viewler_view(self):

        if self.actionProcessing.isChecked():
            self.new_gui = subprocess.Popen("python "+ 'historic.py')
        else:
            if self.new_gui:
                del self.new_gui

    def screen_view(self):

        if self.actionScreen.isChecked():
            if not self.timer.isActive():
                self.timer.start(1)
                self.screen.show()
                self.screen.showFullScreen()
        else:
            if self.timer.isActive():
                self.timer.stop()
                self.screen.close()

    def monitor_view(self):

        if self.actionMonitor.isChecked():
            self.monitor.show()
            self.worker2.start()

        else:

            self.monitor.close()
            self.worker2.terminate()


    def pc_connect(self):

        if self.connect_button.isChecked():  # activamos

            self.ble.port = str(self.port_combobox.currentText())
            self.ble.baudrate = int(self.baud_comboBox.currentText())
            self.ble.timeout = 1
            self.ble.open()
            self.pc_led.setValue(1)
        else:
            self.ble.close()
            self.pc_led.setValue(0)

    def run_device(self):

        if self.connect_button.isChecked():

            if self.run_button.isChecked():
                self.worker.start()

            else:
                self.worker.terminate()

    def scan_bluethoot_devices(self):

        """
        :return:
        dictionary with the found devices and their respective MAC address
        """
        #self.textBrowser.append('Scanning for Bluethooth devices...')
        devices = dict()
        self.ble.write('AT+INQ+\r\n')
        ack = '+INQE'
        answer = ''
        while ack not in answer:  # ack not in answer
            answer += self.ble.read(50)
            print answer
            #TODO: modify for detecting severals BLE
            if '+INQ:' in answer:  # device found in answer
                num = answer[answer.find(':') + 1]
                mac = answer[answer.find(' ') + 1:answer.find(' ') + 15]
                devices[num] = mac

        print devices
        #[self.devices_comboBox.addItem(i) for i in devices.values()]
        #if devices:
        #    self.textBrowser.append('Bluethooth devices found')
        #else:
        #    self.textBrowser.append('Bluethooth devices not found: ')

    def pair_bluethoot_devices(self):
        """

        :param device: dictionary with number and MAC of device to connect
        :return: string containing CONNECTED + MAC device
        """
        if self.pair_device_button.isChecked():
            device = str(self.devices_comboBox.currentText())
            #self.textBrowser.append('connecting with ' + device)
            command = 'AT+CONN' + '0' + '\r\n'  # pq es 0??!!:indice de la mac
            print command
            self.ble.write(command)
            ack = '+CONNECTED>>' + device
            answer = ''
            while ack not in answer:
                answer += self.ble.read(50)
            #self.textBrowser.append('device ' + device + 'connected!!')

    def read_data(self):

        # esto va por un hilo independiente
        #TODO: PAsar el ble a bytes
        #TODO: Hacer la comunicacion sincrona
        #leo datos del device

        try:
            raw_data = self.ble.readline()  # lectura asincrona
            #los grabo en log
            if self.f:
                self.f.write(raw_data[:-1] + ',' + str(self.data_event) + '\n')
                self.recording_led.toggleValue()

            #pongo en cola para actualizar monitor
            raw_data = map(float, raw_data.split(','))
            self.Q.put(raw_data)
            #pongo en cola para actualizar base de datos
            if self.worker3.isRunning():
                self.Q2.put(raw_data)

        except:
            print('no se ha podido leer')

    def connectDatabase(self):
        db_info = connectDatabase.getData()
        if db_info:

            self.db = MySQLdb.connect(host=str(db_info[0]),
                                      user=str(db_info[1]),
                                      passwd=str(db_info[2]),
                                      db=str(db_info[3]))

            self.cur = self.db.cursor()
            self.worker3.start()
            print('database connected')

    def newDataDB(self):
        print self.Q2.get()

    def newPatientDB(self):

        if self.cur and self.patient:
            if True:
                self.cur.execute("""INSERT INTO pacientes VALUES ('%s','%s','%s','%d',%'s')""",
                                (str(self.patient[0]), str(self.patient[1]), str(self.patient[2]),
                                int(self.patient[3]), str(self.patient[4])))

                self.db.commit()
            #except:

            #    print ('no se ha escrito en db')
            #    self.db.rollback()



    def newExperimentDialog(self):

        self.duration, self.silence, self.images = newExperiment.getExperiment()

        if self.images:
            self.experiment_led.toggleValue()
            self.experiment_duration = len(self.images)

    def loadExperimentDialog(self):
        fname = QtGui.QFileDialog.getOpenFileName(self, 'Open Experiment', '.\experiments')
        with open(fname, 'r') as myFile:
            for line in myFile:
                if line[0] == 'I':
                    self.images.append(line[1:-1])
                elif line[0] == 'S':
                    self.silence = int(line[1:-1])
                elif line[0] == 'D':
                    self.duration = int(line[1:-1])

        if self.images:
            self.experiment_led.toggleValue()
            self.experiment_duration = len(self.images)





    def newDialog(self):

        self.patient = newDialog.getData()
        if self.patient:
            #para fichero
            self.fname = './patients/' + self.patient[0] + ' ' + self.patient[1]
            self.f = open(self.fname, 'a')
            self.f.write(','.join(map(str, self.patient)))
            self.f.write('\n')
            self.patient.append(self.fname)
            self.fillPatientTable()
            self.patient_led.toggleValue()
            #para base de datos
            self.newPatientDB()

    def fillPatientTable(self):

        for i, data in enumerate(self.patient):
            item = QtGui.QTableWidgetItem(data)
            item.setFlags(QtCore.Qt.ItemIsEnabled)
            self.patient_table.setItem(i, 0, item)


    def loadDialog(self):

        self.fname = QtGui.QFileDialog.getOpenFileName(self, 'Open Log', '.\patients')
        if self.fname:  # si devuelve algo
            self.f = open(self.fname)  # abro fichero
            self.patient = self.f.readline().split(',')  # leo datos del fichero (first linea)
            self.patient.append(self.fname)
            self.f.close()
            self.f = open(self.fname, 'a')  # cierro y vuelvo a abrir en moddo append
            self.fillPatientTable()  #imprimo info del paciente
            self.patient_led.setValue(1)

    def changeFrequency(self):

        value = str(self.freq_comboBox.currentText())
        print value
        self.ble.write_data(value)
        print 'todo ok'

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

    def keyPressEvent(self, event):
        if type(event) == QtGui.QKeyEvent and event.key() == QtCore.Qt.Key_A:
            self.data_event = 1
            print self.data_event

        if type(event) == QtGui.QKeyEvent and event.key() == QtCore.Qt.Key_S:
            self.data_event = 0
            print self.data_event

###################################################
################  THREADS##########################
###################################################

class worker(QtCore.QThread):
    def __init__(self, parent=None):
        super(worker, self).__init__(parent)
        self.running = False


    def run(self):
        self.running = True
        while self.running:
            self.emit(QtCore.SIGNAL("thread_readdata()"))
            #time.sleep(0.01)


class worker2(QtCore.QThread):
    def __init__(self, parent=None):
        super(worker2, self).__init__(parent)
        self.running = False

    def run(self):
        while True:
            self.emit(QtCore.SIGNAL("thread_loopmonitor()"))

class worker3(QtCore.QThread):
    def __init__(self, parent=None):
        super(worker3, self).__init__(parent)

    def run(self):
        while True:
            self.emit(QtCore.SIGNAL("thread_writedatabase()"))

################################################################
######################## DIALOGS ################################
################################################################

class newDialog(QtGui.QDialog):
    def __init__(self, parent=None):
        super(newDialog, self).__init__(parent)

        self.form = QtGui.QFormLayout()
        self.form.setHorizontalSpacing(0)

        self.line1 = QtGui.QLineEdit()
        self.line2 = QtGui.QLineEdit()
        self.line3 = QtGui.QLineEdit()
        self.line4 = QtGui.QLineEdit()
        self.line5 = QtGui.QLineEdit()
        self.form.addRow('Name: ', self.line1)
        self.form.addRow('Surname: ', self.line2)
        self.form.addRow('Gender: ', self.line3)
        self.form.addRow('Age: ', self.line4)
        self.form.addRow('Observations: ', self.line5)

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
        return [self.line1.text(), self.line2.text(), self.line3.text(), self.line4.text(), self.line5.text()]

    @staticmethod
    def getData(parent=None):
        dialog = newDialog(parent)
        result = dialog.exec_()
        date = dialog.returndata()
        return date

class connectDatabase(QtGui.QDialog, Ui_database_Dialog):

    def __init__(self, parent=None):
        super(connectDatabase, self).__init__(parent)
        self.setupUi(self)

    def returndata(self):
        return [self.lineEdit.text(), self.lineEdit_2.text(),
                self.lineEdit_3.text(), self.lineEdit_4.text()]

    @staticmethod
    def getData(parent=None):
        dialog = connectDatabase(parent)
        dialog.exec_()
        data = dialog.returndata()
        return data

class newExperiment(QtGui.QDialog, Ui_Dialog):

    def __init__(self, parent=None):
        super(newExperiment, self).__init__(parent)
        self.setupUi(self)

        ### SIGNALS
        self.openButton.clicked.connect(self.open_file)
        self.selectButton.clicked.connect(self.add_file)
        self.save_Button.clicked.connect(self.save_experiment)
        self.removeButton.clicked.connect(self.delete_file)
        self.list_one.itemClicked.connect(self.update_left_image)
        self.list_two.itemClicked.connect(self.update_right_image)


    def open_file(self):
        fnames = QtGui.QFileDialog.getOpenFileNames(self, 'Open Images', '.\images')


        for file in fnames:
            print file
            self.list_one.addItem(file)

    def add_file(self):
        items = self.list_one.selectedItems()
        for item in items:
            self.list_two.addItem(item.text())
        self.update_master()

    def delete_file(self):
        items = self.list_two.selectedItems()
        print items
        for item in items:
            self.list_two.takeItem(self.list_two.row(item))
        self.update_master()


    def update_left_image(self, item):

        qpix = QtGui.QPixmap(item.text())
        qpix = qpix.scaled(128, 128, QtCore.Qt.KeepAspectRatio)
        self.image1.setPixmap(qpix)

    def update_right_image(self, item):

        qpix = QtGui.QPixmap(item.text())
        qpix = qpix.scaled(128, 128, QtCore.Qt.KeepAspectRatio)
        self.image2.setPixmap(qpix)

    def update_master(self):

        self.clear_layout()  #borro todos los elementos del layout
        items = []
        for index in xrange(self.list_two.count()):
            items.append(self.list_two.item(index))  # cojo los items de la lista
        row = 0
        col = 0
        max_ele = 10

        for i, item in enumerate(items):
            i += 1
            im = QtGui.QPixmap(item.text())
            im = im.scaled(96, 96, QtCore.Qt.KeepAspectRatio)
            label = QtGui.QLabel()
            label.setPixmap(im)
            self.mastergrid.addWidget(label, row, col)
            col += 1
            if i % max_ele == 0:
                row += 1
                col = 0

    def clear_layout(self):
        for i in reversed(range(self.mastergrid.count())):
            self.mastergrid.itemAt(i).widget().setParent(None)

    def save_experiment(self):
        if self.list_two.count() > 0:
            fileName = QtGui.QFileDialog.getSaveFileName(self, 'Dialog Title', './experiments/', selectedFilter='*.txt')
            if fileName:
                file = open(str(fileName), 'w')
                for index in xrange(self.list_two.count()):
                    item = (self.list_two.item(index))  # cojo los items de la lista
                    file.write('I' + str(item.text()) + '\n')  # escribo en fichero las imagenes
                file.write('D' + str(self.silenciosSlider.value()) + '\n')
                file.write('S' + str(self.imagenesSlider.value()) + '\n')
                file.close()

    def returnData(self):

        duration = self.imagenesSlider.value()
        silence = self.silenciosSlider.value()
        items = []
        for index in xrange(self.list_two.count()):
            items.append(self.list_two.item(index))  # cojo los items de la lista

        files = [item.text() for item in items]

        return duration, silence, files

    @staticmethod
    def getExperiment(parent=None):
        dialog = newExperiment(parent)
        dialog.exec_()
        data = dialog.returnData()
        return data


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    myapp = MainGui2()
    myapp.show()
    sys.exit(app.exec_())
