from PySide2.QtCore import Slot
from fbs_runtime.application_context.PySide2 import ApplicationContext
from PySide2 import QtWidgets

import sys

from package import videocheck

class StartWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.disposition = QtWidgets.QGridLayout()

    # Widgets instantation
        self.job_list = QtWidgets.QListWidget()
        self.add_button = QtWidgets.QPushButton("Add Job")
        self.remove_button = QtWidgets.QPushButton("Remove Job")
        self.start_button = QtWidgets.QPushButton("START")

    # Widgets positions
        self.disposition.addWidget(self.job_list,0,0,4,6)
        self.disposition.addWidget(self.add_button,4,0,1,1)
        self.disposition.addWidget(self.remove_button,4,1,1,1)
        self.disposition.addWidget(self.start_button,4,5,1,1)

    # slots attributions
        self.start_button.clicked.connect(self.start)

    # Window initialisation
        self.setWindowTitle("Crop Detection version 0.5")
        self.widget = QtWidgets.QWidget()
        self.widget.setLayout(self.disposition)
        self.setCentralWidget(self.widget)
        self.resize(800, 600)

    def start(self):
        print("Button start clicked !")



if __name__ == '__main__':
    appctxt = ApplicationContext()       # 1. Instantiate ApplicationContext
    window = StartWindow()

    window.show()
    exit_code = appctxt.app.exec_()      # 2. Invoke appctxt.app.exec_()
    sys.exit(exit_code)