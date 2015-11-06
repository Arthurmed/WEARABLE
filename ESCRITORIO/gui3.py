

import sys
import subprocess
from pyqtgraph.Qt import QtGui, QtCore
from main_frame_2 import Ui_MainWindow
from ESCRITORIO.monitor3 import Monitor
import socket
import datetime
import time

from QLed import QLed


try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s



class MainGui2(QtGui.QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):

        super(MainGui2, self).__init__(parent)
        self.setupUi(self)  # cargamos la ui


        #CONTROL VARIABLES
        self.patient = []  # almacena info del paciente  # TODO: change by dict
        self.fname = ''  # path del log
        self.f = ''
        self.descarga_disco = False  # variable para controlar la descarga a disco


        #reservado para la conexion
        self.s = None

        #####################################
        #STATUS BAR
        ######################################

        #LEDS
        self.pc_led = QLed()
        self.pc_led.setOnColour(QLed.Green)
        self.pc_led.setOffColour(QLed.Red)

        self.patient_led = QLed()
        self.patient_led.setOffColour(QLed.Red)
        self.patient_led.setOnColour(QLed.Green)

        self.recording_led = QLed()
        self.recording_led.setOffColour(QLed.Red)
        self.recording_led.setOnColour(QLed.Blue)

        self.connect_messages = QtGui.QLabel('Desconectado')
        self.recording_messages = QtGui.QLabel('stop')
        self.patient_messages = QtGui.QLabel('None')

        self.statusbar.addWidget(QtGui.QLabel('Server Connection: '))
        self.statusbar.addWidget(self.connect_messages)
        self.statusbar.addWidget(self.pc_led)

        self.statusbar.addWidget(QtGui.QLabel('Patient Registering: '))
        self.statusbar.addWidget(self.patient_messages)
        self.statusbar.addWidget(self.patient_led)

        self.statusbar.addWidget(QtGui.QLabel('Recording: '))
        self.statusbar.addWidget(self.recording_messages)
        self.statusbar.addWidget(self.recording_led)


        ######################################
        #MAINFRAME
        #######################################
        #CENTRAR APLICACION MONITOR

        self.monitor = Monitor()
        self.setCentralWidget(self.monitor)

        #SIGNALS

        self.connect_button.clicked.connect(self.pc_connect)
        self.run_button.clicked.connect(self.run_device)
        self.reset_button.clicked.connect(self.reset_wearable)

        self.connect(self.actionNew_Patient, QtCore.SIGNAL('triggered()'), self.newDialog)
        self.connect(self.actionLoad_Patient, QtCore.SIGNAL('triggered()'), self.loadDialog)
        self.connect(self.freq_comboBox, QtCore.SIGNAL("currentIndexChanged(const QString&)"), self.changeFrequency)

        #QTHREADS
        self.worker = worker()
        self.connect(self.worker, QtCore.SIGNAL("thread_readdata()"), self.read_data, QtCore.Qt.DirectConnection)

        #QTIMERS FOR DOWNLOAD DATO TO DISC
        self.timer = QtCore.QTimer()
        self.connect(self.timer, QtCore.SIGNAL('timeout()'), self.activateVolcado)

    def viewler_view(self):

        if self.actionProcessing.isChecked():
            self.new_gui = subprocess.Popen("python "+ 'historic.py')
        else:
            if self.new_gui:
                del self.new_gui

    def pc_connect(self):

        if self.connect_button.isChecked():  # activamos

            try:
                #SERVER
                self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.s.settimeout(None)
                self.s.connect(("192.168.1.16", 8888))  # conectamos con servidor
                self.connect_button.setText('DISCONNECT')
                self.pc_led.setValue(1) # activamos el led
                a = self.s.getpeername()
                self.connect_messages.setText('Conectado con: ' + str(a))

            except socket.error, e:
                QtGui.QMessageBox.critical(self, "ERROR DE CONEXION", str(e[1]), QtGui.QMessageBox.Ok)




        else:

            self.s.close()
            del self.s
            self.connect_button.setText('CONNECT')
            self.pc_led.setValue(0)
            self.connect_messages.setText('Desconectado del server')

    def run_device(self):

        if self.connect_button.isChecked():

            if self.run_button.isChecked():
                self.run_button.setText('STOP')
                self.s.send('RUN')
                self.worker.start()  # quizas este no deberia pararlo, ya paro el server
                self.timer.start(10000)

            else:
                self.run_button.setText('START')
                self.s.send('STOP')
                self.worker.terminate()
                self.timer.stop()


    def activateVolcado(self):

        self.descarga_disco = True
        print('activando el volcado')

    def read_data(self):

        try:
            #TODO: hay que controlar el tamanio de datos?
            raw = self.s.recv(1024) # lectura asincrona de un dato

            if int(raw) < 2 ** 15:  # desecho datos incongruentes por efecto del buffer

                t = str(datetime.datetime.now().time())  # cojo el tiempo del sistema

                print(raw)
                self.monitor.update_eda_data(int(raw))  # actualizo el monitor

                #los grabo en log
                if self.f:
                    self.f.write(t + ',' + raw + '\n')
                    self.recording_led.toggleValue()

                #descargo memoria y grabo en disco cada 10 segundos. Falg controlado por timer
                if self.descarga_disco and self.f:
                    self.f.close()
                    self.f = open(self.fname, 'a')
                    self.descarga_disco = False

        except:
            print('no se ha podido leer')

    def reset_wearable(self):

        if self.s:
            ret = QtGui.QMessageBox.warning(self, "Advertencia",
            "Estas seguro que quieres RESETEAR el WEARABLE?",
            QtGui.QMessageBox.Ok, QtGui.QMessageBox.Cancel)
            if ret == QtGui.QMessageBox.Ok:
                self.s.send('RESET')




    def newDialog(self):

        self.patient = newDialog.getData()
        if self.patient:
            #para fichero
            self.fname = './patients/' + self.patient[0] + ' ' + self.patient[1]
            self.f = open(self.fname, 'a')
            info = ' '.join(map(str, self.patient))
            self.f.write(info)  # escribo info a fichero
            self.f.write('\n')

            #adding to status bar

            self.patient_messages.setText(info)
            self.patient_led.toggleValue()



    def loadDialog(self):

        self.fname = QtGui.QFileDialog.getOpenFileName(self, 'Open Log', '.\patients')
        if self.fname:  # si devuelve algo
            self.f = open(self.fname)  # abro fichero
            self.patient = self.f.readline().split(' ')  # leo datos del fichero (first linea)
            self.patient.append(self.fname)  # los pongo en la variable del sistema
            self.patient_messages.setText(' '.join(map(str, self.patient)))  # pongo el nombre en la barra
            self.recording_led.setValue(1)  # activo el led
            self.f.close()  # cierro el fichero
            self.f = open(self.fname, 'a')  # cierro y vuelvo a abrir en moddo append

    def changeFrequency(self):

        #TODO para cambiar la fecuancia de muestreo.
        value = str(self.freq_comboBox.currentText())
        print "FREQ," + value
        self.s.send("FREQ," + value)

    def closeEvent(self, event):

        quit_msg = "Are you sure you want to exit the program?"
        reply = QtGui.QMessageBox.question(self, 'Message',
                                           quit_msg, QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)

        if reply == QtGui.QMessageBox.Yes:
            self.f.close()  # cierro el fichero
            event.accept()
        else:
            event.ignore()


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



if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    myapp = MainGui2()
    myapp.show()
    sys.exit(app.exec_())
