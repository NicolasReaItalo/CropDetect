import os

from PySide2.QtCore import Slot
from fbs_runtime.application_context.PySide2 import ApplicationContext
from PySide2 import QtWidgets
from pathlib import Path


import sys

from package import timecode
from package.videocheck import is_video, JobDir, Job_File

##  Main logic<
job_list = []



class StartWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.disposition = QtWidgets.QGridLayout()

    # Widgets instantation
        self.job_list_widget = QtWidgets.QListWidget()
        self.add_button = QtWidgets.QPushButton("Add Job")
        self.remove_button = QtWidgets.QPushButton("Remove Job")
        self.start_button = QtWidgets.QPushButton("START")

    # Widgets positions
        self.disposition.addWidget(self.job_list_widget,0,0,4,6)
        self.disposition.addWidget(self.add_button,4,0,1,1)
        self.disposition.addWidget(self.remove_button,4,1,1,1)
        self.disposition.addWidget(self.start_button,4,5,1,1)

    # slots attributions
        self.start_button.clicked.connect(self.start)
        self.add_button.clicked.connect(self.add_job)
        self.remove_button.clicked.connect(self.remove_job)




    # Window initialisation
        self.setWindowTitle("Crop Detection version 0.5")
        self.widget = QtWidgets.QWidget()
        self.widget.setLayout(self.disposition)
        self.setCentralWidget(self.widget)
        self.resize(800, 600)

    def start(self):
        print("Button start clicked !")

    def add_job(self):
        self.open_file_path_window()
        self.refresh_job_list_widget()

    def remove_job(self):
        print("Button remove_job clicked !")

    def open_file_path_window(self):
        f = QtWidgets.QFileDialog.getOpenFileUrl(self, f"{Path.home()}/Desktop")
        path = f[0].toLocalFile()
        if is_video(path):
            job  = Job_File()
            job.load_video_file(path)
            job_list.append(job)
        else:
            self.alert("Ceci n'est pas un fichier video valide")

    def refresh_job_list_widget(self):
        self.job_list_widget.clear()
        for job in job_list:
            if job.job_type == "File":
                filename =  os.path.basename(job.video_path).split('.')[0]
                self.job_list_widget.addItem(f"{filename} / {job.framerate} FPS / {job.codec} / {job.x_res}X{job.y_res}px  /"
                                             f"Duration {timecode.frame_to_tc_02((job.end_frame), job.framerate)}/  {job.end_frame} frames"
                                             f"/ Report path : {job.report_path}")
            elif job.job_type == "Dir":
                pass

    def alert(self,message):
        self.m = QtWidgets.QMessageBox.about(self,"Attention", message)

if __name__ == '__main__':
    appctxt = ApplicationContext()       # 1. Instantiate ApplicationContext
    window = StartWindow()

    window.show()
    exit_code = appctxt.app.exec_()      # 2. Invoke appctxt.app.exec_()
    sys.exit(exit_code)