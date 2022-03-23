import os

from PySide2.QtCore import Slot
from fbs_runtime.application_context.PySide2 import ApplicationContext
from PySide2 import QtWidgets, QtCore
from pathlib import Path

import sys

from package import timecode
from package.videocheck import is_video, Job_File

##  Main logic<
job_list = []



class StartWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()


        self.disposition = QtWidgets.QGridLayout()

    # Widgets instantation
        self.job_list_widget = QtWidgets.QListWidget()
        self.add_job_button = QtWidgets.QPushButton("Add Job")
        self.remove_button = QtWidgets.QPushButton("Remove Job")
        self.start_button = QtWidgets.QPushButton("START")

        self.job_list_widget.setStyleSheet("QListWidget"
                                  "{"
                                  "border : 2px solid grey;"
                                  "background : white;"
                                  "}"
                                  "QListWidget QScrollBar"
                                  "{"
                                  "background : lightblue;"
                                  "}"
                                    "QListView::item"
                                  "{"
                                  "border : 1px solid grey;"
                                  "}"
                                  "QListView::item:selected"
                                  "{"
                                  "border : 1px solid grey;"
                                  "background : #1873c7"
                                  "}"
                                  )






    # Widgets positions
        self.disposition.addWidget(self.job_list_widget,3,0,1,3)
        self.disposition.addWidget(self.add_job_button, 4, 0, 1, 1)
        self.disposition.addWidget(self.remove_button,4,1,1,1)
        self.disposition.addWidget(self.start_button,4,2,1,1)

    # slots attributions
        self.start_button.clicked.connect(self.start)
        self.add_job_button.clicked.connect(self.press_add_job_button)
        self.remove_button.clicked.connect(self.remove_job)


    # Window initialisation
        self.setWindowTitle("🐝🐝Crop error Detection Version 0.5🐝🐝")
        self.widget = QtWidgets.QWidget()
        self.widget.setLayout(self.disposition)
        self.setCentralWidget(self.widget)
        self.resize(600, 400)

    def start(self):
        for job in job_list:
            if not job.done:
                job.analyse_video()
                job.generate_html_report()
                job.generate_csv()
                job.generate_edl()
        self.refresh_job_list_widget()



    def remove_job(self):
        self.remove_selected_job()
        self.refresh_job_list_widget()



    def refresh_job_list_widget(self):
        cancel_label ="❗Canceled"
        done_label = "✅ Done ! "
        todo_label = "🔲 To Do  "

        self.job_list_widget.clear()
        for job in job_list:
            if job.done and job.complete:
                state = done_label

            if not job.done:
                state = todo_label
            if job.done and not job.complete:
                state = cancel_label

            if job.job_type == "File":
                filename =  os.path.basename(job.video_path)
                self.job_list_widget.addItem(f"{state} ➡️ {filename}\n"
                                             f"                     ▪ {job.x_res}X{job.y_res}px\n"
                                             f"                     ▪ {job.framerate} frames.seconds\n"
                                             f"                     ▪ {job.codec}\n")

            elif job.job_type == "Dir":
                pass

    def alert(self,message):
        self.m = QtWidgets.QMessageBox.about(self,"Attention", message)

    def remove_selected_job(self):
        if len(job_list) > 0:
            del job_list[self.job_list_widget.currentRow()]




    def press_add_job_button(self):
        job = Job_File()
        # Choosing video file to analyse
        f = QtWidgets.QFileDialog.getOpenFileUrl(self, "Select Video File")
        path = f[0].toLocalFile()
        if is_video(path):
            job.load_video_file(path)
        else:
            error = QtWidgets.QMessageBox()
            error.setText(f"This is not a valid Video File:{path}")
            error.exec_()
            return
        # append job
        job_list.append(job)
        self.refresh_job_list_widget()



if __name__ == '__main__':
    appctxt = ApplicationContext()       # 1. Instantiate ApplicationContext
    window = StartWindow()
   # stylesheet = appctxt.get_resource('style.qss')
   # appctxt.app.setStyleSheet(open(stylesheet).read())
    window.show()
    exit_code = appctxt.app.exec_()      # 2. Invoke appctxt.app.exec_()
    sys.exit(exit_code)