from pyqtgraph.Qt import QtGui, QtCore
import numpy as np
import pyqtgraph as pg
import serial

#QtGui.QApplication.setGraphicsSystem('raster')
app = QtGui.QApplication([])
#mw = QtGui.QMainWindow()
#mw.resize(800,800)

win = pg.GraphicsWindow(title="RT EMG")
win.resize(600,400)

ser = serial.Serial('COM6', 115200, timeout=0.1)
ser.flush()


# Enable antialiasing for prettier plots
pg.setConfigOptions(antialias=True)

p6 = win.addPlot(title="EMG")
curve = p6.plot(pen='y')
data = np.zeros(1000)
#ptr = 0
def update():
    global curve, data, ptr, p6

    value = ser.readline()
    print value
    data = np.roll(data, -1)  # shift data in the array one sample left
    data[-1] = float(value)
    curve.setData(data)
    #curve.setData(value)
    if ptr == 0:
        p6.enableAutoRange('xy', False)  ## stop auto-scaling after the first data set is plotted
    ptr += 1

timer = QtCore.QTimer()
timer.timeout.connect(update)
timer.start(0.1)

## Start Qt event loop unless running in interactive mode or using pyside.
if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()