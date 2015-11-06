import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui
from pyqtgraph.dockarea import *
import numpy as np
import random



class Monitor(QtGui.QMainWindow):
    def __init__(self, parent=None):

        self._DEBUGUER = 1
        QtGui.QMainWindow.__init__(self, parent)
        # set the main window
        self.resize(1000, 800)
        self.setWindowTitle('VIEWLER ARISTARKO')

        #CONTROL VARIABLES
        self.len = 100
        self.focus = False
        self.events = []  # list for store events
        self.plots = []  # list of plots
        self.ini = False
        self.fin = False

        #set dock area as central widget
        self.area = DockArea()
        self.setCentralWidget(self.area)  # inserto el pg como una widget central.

        #create docks and add them into dock area
        self.d1 = Dock("Controls", size=(200, 50), closable=True)
        self.d2 = Dock("Plots", size=(600, 480))
        #self.d3 = Dock("FOCUS", size=(400, 400), closable=True)
        self.area.addDock(self.d1, 'left')
        self.area.addDock(self.d2)

        #create a layout for dock 1. I am going to introduce more widgets
        self.w1 = pg.LayoutWidget()
        self.w2 = pg.LayoutWidget()
        self.w3 = pg.LayoutWidget()

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
        self.label1 = QtGui.QLabel("Zoom", )
        self.slider1 = QtGui.QSlider()
        self.slider1.setOrientation(QtCore.Qt.Horizontal)
        self.slider1.setRange(0, 99)
        self.slider1.setValue(1)

        #pyqtgraph
        self.win = pg.GraphicsWindow()
        self.win.resize(600, 600)
        self.win.setWindowTitle('VIEWLER ARISTARKO')
        #self.win2 = pg.GraphicsWindow()
        #self.win2.setWindowTitle('eventos')


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
        self.plots.append(self.p1)

        #creating curve for EDA
        self.curve1 = self.p1.plot(pen=(255, 0, 0), clickable=True)
        #self.curve1.sigPointsClicked.connect(self.plotClicked)
        #creating data vector
        self.eda = np.zeros(self.len)


        #PLOTS DEL EMG
        self.win.nextRow()
        self.p2 = self.win.addPlot(title="Electromyogram")
        #set the range of Xdata
        self.p2.setRange(xRange=[-self.len, 0])
        self.p2.setLimits(xMax=0)
        self.plots.append(self.p2)
        #creating curve for EDA
        self.curve2 = self.p2.plot(pen=(0, 0, 255))
        #creating data vector
        self.emg = np.zeros(self.len)

        #PLOTS DEL HRV
        self.win.nextRow()
        self.p3 = self.win.addPlot(title="Electrocardiogram")
        #set the range
        self.p3.setRange(xRange=[-self.len, 0])
        self.p3.setLimits(xMax=0)
        self.plots.append(self.p3)
        #creating curve for HRV
        self.curve3 = self.p3.plot(pen=(0, 255, 0))
        #creating data vector
        self.ecg = np.zeros(self.len)

        #PLOTS DEL SKT
        self.win.nextRow()
        self.p4 = self.win.addPlot(title="Skin Temperature")
        #set the range
        self.p4.setRange(xRange=[-self.len, 0])
        self.p4.setLimits(xMax=0)
        self.plots.append(self.p4)
        #creating curve for SKT
        self.curve4 = self.p4.plot(pen=(0, 255, 255))
        # #creating data vector
        self.skt = np.zeros(self.len)


        ##########################################################
        ####   EVENTS
        ##########################################################

        #PLOTS DE EVENTOS
        #self.e1 = self.win2.addPlot()
        #self.e1.setRange(xRange=[-self.len, 0])
        #self.e1.setLimits(xMax=0)
        #self.win2.nextRow()
        #self.e2 = self.win2.addPlot()
        #self.e2.setRange(xRange=[-self.len, 0])
        #self.e2.setLimits(xMax=0)
        #self.win2.nextRow()
        #self.e3 = self.win2.addPlot()
        #self.e3.setRange(xRange=[-self.len, 0])
        #self.e3.setLimits(xMax=0)
        #self.p5 = self.win.addPlot(title="EVENTS")
        #self.p5.setRange(xRange=[-self.len, 0])
        #self.p5.setLimits(xMax=0)


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
        #self.area = pg.LinearRegionItem(values=[0,1], orientation=pg.LinearRegionItem.Vertical, movable=False)
        #self.area2 = pg.LinearRegionItem(values=[0,1], orientation=pg.LinearRegionItem.Vertical, movable=False)

        #self.p5.addItem(self.area)
        #self.p5.addItem(self.area2)

        #self.area.setRegion((-50, -25))
        #self.area2.setRegion((-50, -30))

        #solo para debuguear
        if self._DEBUGUER:
            self.timer = pg.QtCore.QTimer()
            self.timer.timeout.connect(self.update_all)
            self.timer.start(50)

            #self.timer2 = pg.QtCore.QTimer()
            #self.timer2.timeout.connect(self.add_region_image)
            #self.timer2.start(5000)

            #self.timer3 = pg.QtCore.QTimer()
            #self.timer3.timeout.connect(self.add_region_button)
            #self.timer3.start(3000)

            #self.timer4 = pg.QtCore.QTimer()
            #self.timer4.timeout.connect(self.add_region_button_2)
            #self.timer4.start(7500)

    def update_all(self, data1=None, data2=None, data3=None, data4=None, data5=None):

        if self._DEBUGUER:
            data1 = random.randint(1, 100)
            data2 = random.randint(1, 100)
            data3 = random.randint(1, 100)
            data4 = random.randint(1, 100)
            data5 = random.randint(0, 1)
            self.update_eda_data(data1)
            self.update_emg_data(data2)
            self.update_ecg_data(data3)
            self.update_skt_data(data4)
            self.process_current_event(data5)
            self.update_region_queue()


        else:

            self.update_eda_data(data1)
            self.update_emg_data(data2)
            self.update_ecg_data(data3)
            self.update_skt_data(data4)
            self.process_current_event(data5)
            self.update_region_queue()




    def add_region_image(self):

        event = pg.LinearRegionItem((0, 0), brush=[0, 255, 255], movable=False)
        self.e1.addItem(event, ignoreBounds=True)
        #self.events.append(event)
        return event

    def add_region_button(self):

        event = pg.LinearRegionItem((0, -10), brush=[255, 255, 0], movable=False)
        self.e2.addItem(event, ignoreBounds=True)
        self.events.append(event)

    def add_region_button_2(self):

        event = pg.LinearRegionItem((0, -30), brush=[255, 0, 255], movable=False)
        self.e3.addItem(event, ignoreBounds=True)
        self.events.append(event)

    def process_current_event(self, data):

        self.fin = self.ini
        self.ini = data

        if self.ini == True and self.fin == False:
            self.image = self.add_region_image()

        elif self.ini == True and self.fin == True:
            min, max = self.image.getRegion()
            min -=1
            self.image.setRegion((min, max))

        elif self.ini == False and self.fin == True:
            self.events.append(self.image)

    def update_region_queue(self):

        aux = self.events

        for item in aux:
            minX, maxX = item.getRegion()
            if maxX < -self.len:
                #TODO: quitar redundancia
                self.events.remove(item)
                self.e1.removeItem(item)
                #self.e2.removeItem(item)
                #self.e3.removeItem(item)
            minX -= 1
            maxX -= 1
            item.setRegion((minX, maxX))


    def update_eda_data(self, data):

        # EDA
        self.eda = np.roll(self.eda, -1)  # shift data in the array one sample left
        self.eda[-1] = data
        self.curve1.setData(self.eda)
        self.curve1.setPos(-self.len, 0)  # marca para que sepa que tiene que coger 100 negativos

    def update_emg_data(self, data):

        # EMG
        self.emg = np.roll(self.emg, -1)  # shift data in the array one sample left
        self.emg[-1] = data
        self.curve2.setData(self.emg)
        self.curve2.setPos(-self.len, 0)  # marca para que sepa que tiene que coger 100 negativos

    def update_ecg_data(self, data):

        # ECG
        self.ecg = np.roll(self.ecg, -1)  # shift data in the array one sample left
        self.ecg[-1] = data
        self.curve3.setData(self.ecg)
        self.curve3.setPos(-self.len, 0)  # marca para que sepa que tiene que coger 100 negativos

    def update_skt_data(self, data):

        # SKT
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
            print -self.len
            self.e1.setRange(xRange=[-self.len - 100, 0])  # TODO: arreglar esto
            self.e1.setLimits(xMax=0)
            self.e2.setRange(xRange=[-self.len - 100, 0])  # TODO: arreglar esto
            self.e2.setLimits(xMax=0)
            self.e3.setRange(xRange=[-self.len - 100, 0])  # TODO: arreglar esto
            self.e3.setLimits(xMax=0)

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
        self.close()

    def onClick(self, event):

        items = self.win.scene().items(event.scenePos())[2]

        if not self.focus:

            if items in self.p:
                plot = self.p[self.p.index(items)]  # averiguo que plot es
                self.p.remove(plot)  # lo quito de la lista
                # elimino y adding el resto

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
        # QtGui.QApplication.instance().exec_()
        app = QtGui.QApplication(sys.argv)
        a = Monitor()
        a.show()
        sys.exit(app.exec_())