from PyQt4.QtGui import *
import sys
import MainWindow as mw

if __name__ == '__main__':
    app = QApplication(sys.argv)
    screen = mw.MainWindowApplication()
    sys.exit(app.exec_())