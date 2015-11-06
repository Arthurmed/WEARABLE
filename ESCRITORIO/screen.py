
from PyQt4 import QtGui, QtCore
import sys


class Screen(QtGui.QMainWindow):

    def __init__(self, parent = None):

        super(Screen, self).__init__(parent)
        self.resize(600, 600)
        self.img = QtGui.QLabel()
        self.setCentralWidget(self.img)
        #dependiendo de lo que queramos se cargaran una lista de imagenes



    def update_image(self, img):
        self.showFullScreen()
        print self.size()
        pic = QtGui.QPixmap(img)
        pic_scaled = pic.scaled(self.size())
        self.img.setPixmap(pic_scaled)





if __name__ == "__main__":


    app = QtGui.QApplication(sys.argv)
    myapp = Screen()
    myapp.show()
    sys.exit(app.exec_())