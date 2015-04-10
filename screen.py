
from PyQt4 import QtCore, QtGui
import sys


class Screen(QtGui.QMainWindow):

    def __init__(self, parent = None):

        super(Screen, self).__init__(parent)
        self.resize(600, 600)

        self.img = QtGui.QLabel()
        self.setCentralWidget(self.img)
        #dependiendo de lo que queramos se cargaran una lista de imagenes
        self.images = []


    def update_image(self):
        self.img.setPixmap(QtGui.QPixmap(self.images[self.counter]))
        self.counter += 1

    def upload_images(self, imgs):
        self.images = imgs



if __name__ == "__main__":


    app = QtGui.QApplication(sys.argv)
    myapp = Screen()
    myapp.show()
    sys.exit(app.exec_())