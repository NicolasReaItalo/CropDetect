import os

from PySide2.QtCore import Slot
from fbs_runtime.application_context.PySide2 import ApplicationContext
from PySide2 import QtWidgets, QtCore
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
        self.add_file_button = QtWidgets.QPushButton("Add File")
        self.add_folder_button = QtWidgets.QPushButton("Add Folder")
        self.remove_button = QtWidgets.QPushButton("Remove Job")
        self.start_button = QtWidgets.QPushButton("START")

    # Widgets positions
        self.disposition.addWidget(self.job_list_widget,0,0,4,6)
        self.disposition.addWidget(self.add_file_button, 4, 0, 1, 1)
        self.disposition.addWidget(self.add_folder_button, 4, 1, 1, 1)
        self.disposition.addWidget(self.remove_button,4,2,1,1)
        self.disposition.addWidget(self.start_button,4,5,1,1)

    # slots attributions
        self.start_button.clicked.connect(self.start)
        self.add_file_button.clicked.connect(self.press_add_file_button)
        self.remove_button.clicked.connect(self.remove_job)




    # Window initialisation
        self.setWindowTitle("Crop Detection version 0.5")
        self.widget = QtWidgets.QWidget()
        self.widget.setLayout(self.disposition)
        self.setCentralWidget(self.widget)
        self.resize(900, 400)

    def start(self):
        print("Button start clicked !")
        self.show_new_window()



    def remove_job(self):
        self.remove_selected_job()
        self.refresh_job_list_widget()



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

    def remove_selected_job(self):
        if len(job_list) > 0:
            del job_list[self.job_list_widget.currentRow()]

    def press_add_file_button(self):
        self.w = AddFileWindow()
        self.w.show()





class AddFileWindow(QtWidgets.QWidget):
    """
    This "window" is a QWidget. If it has no parent, it
    will appear as a free-floating window as we want.
    """
    def __init__(self):
        super().__init__()
        layout = QtWidgets.QVBoxLayout()
        self.choose_file_button = QtWidgets.QPushButton("Select video File")
        self.choose_report_button = QtWidgets.QPushButton("Select Report folder")
        self.v_offset = QtWidgets.QSpinBox()

        layout.addWidget(self.choose_file_button)
        layout.addWidget(self.choose_report_button)
        layout.addWidget(self.v_offset)


        self.setLayout(layout)

        self.resize(400,600)




if __name__ == '__main__':
    appctxt = ApplicationContext()       # 1. Instantiate ApplicationContext
    window = StartWindow()

    window.show()
    exit_code = appctxt.app.exec_()      # 2. Invoke appctxt.app.exec_()
    sys.exit(exit_code)