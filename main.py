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
        self.add_file_button = QtWidgets.QPushButton("Add Job")
        self.remove_button = QtWidgets.QPushButton("Remove Job")
        self.start_button = QtWidgets.QPushButton("START")

    # Widgets positions
        self.disposition.addWidget(self.job_list_widget,0,0,4,6)
        self.disposition.addWidget(self.add_file_button, 4, 0, 1, 1)
        self.disposition.addWidget(self.remove_button,4,1,1,1)
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
        for job in job_list:
            job.analyse_video()
            job.generate_html_report()
            job.generate_csv()



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
        self.refresh_job_list_widget()





class AddFileWindow(QtWidgets.QWidget):
    """
    This "window" is a QWidget. If it has no parent, it
    will appear as a free-floating window as we want.
    """
    def __init__(self):
        super().__init__()
        self.job = Job_File()

        self.disposition = QtWidgets.QGridLayout()
        self.choose_file_button = QtWidgets.QPushButton("Select video File")
        self.file_label = QtWidgets.QLabel("")
        self.choose_report_button = QtWidgets.QPushButton("Select Report folder")
        self.report_label = QtWidgets.QLabel("")
        self.vertical_inner_ratio = QtWidgets.QSpinBox()
        self.vertical_inner_ratio_spinbox = QtWidgets.QSpinBox()
        self.vertical_inner_ratio_spinbox.setSuffix("  px")
        self.vertical_inner_ratio_label = QtWidgets.QLabel("Vertical Inner Ratio\nLeave to analyse all picture")
        self.horizontal_inner_ratio_spinbox = QtWidgets.QSpinBox()
        self.horizontal_inner_ratio_spinbox.setSuffix("  px")
        self.horizontal_inner_ratio_label = QtWidgets.QLabel("Horizontal Inner Ratio\nLeave to analyse all picture")
        self.cancel_button = QtWidgets.QPushButton("cancel")
        self.ok_button = QtWidgets.QPushButton("   Ok   ")


        self.disposition.addWidget(self.choose_file_button,0,0,1,1)
        self.disposition.addWidget(self.file_label,0,1,1,4)
        self.disposition.addWidget(self.choose_report_button,1,0,1,1)
        self.disposition.addWidget(self.report_label, 1, 1, 1, 4)
        self.disposition.addWidget(self.vertical_inner_ratio_spinbox ,2,0,1,1)
        self.disposition.addWidget(self.vertical_inner_ratio_label ,2,1,1,1)
        self.disposition.addWidget(self.horizontal_inner_ratio_spinbox ,3,0,1,1)
        self.disposition.addWidget(self.horizontal_inner_ratio_label ,3,1,1,1)
        self.disposition.addWidget(self.cancel_button ,4,0,1,1)
        self.disposition.addWidget(self.ok_button ,4,1,1,1)

        self.setLayout(self.disposition)

        self.choose_file_button.clicked.connect(self.open_file_path_window)
        self.choose_report_button.clicked.connect(self.open_folder_path_window)
        self.cancel_button.clicked.connect(self.press_cancel_button)
        self.ok_button.clicked.connect(self.press_ok_button)

        self.resize(550,220)


    def open_file_path_window(self):
        f = QtWidgets.QFileDialog.getOpenFileUrl(self, "Select Folder")
        path = f[0].toLocalFile()
        if is_video(path):
            self.job.load_video_file(path)
            self.horizontal_inner_ratio_spinbox.setMaximum(self.job.x_res)
            self.horizontal_inner_ratio_spinbox.setValue(self.job.x_res)
            self.vertical_inner_ratio_spinbox.setMaximum(self.job.y_res)
            self.vertical_inner_ratio_spinbox.setValue(self.job.y_res)
            self.file_label.setText(self.job.video_path)
        else:
            error = QtWidgets.QMessageBox()
            error.setText("This is not a valid Video File.")
            error.exec_()


    def open_folder_path_window(self):
        f = QtWidgets.QFileDialog.getExistingDirectory(self, 'Select Folder')
        report_path = f
        self.job.report_path = report_path
        self.report_label.setText(self.job.report_path)

    def press_cancel_button(self):
        self.close()

    def press_ok_button(self):
        if (self.job.video_path != "") and (self.job.report_path != ""):
            job_list.append(self.job)
            self.close()

    def refresh_spinbox(self):
        pass


if __name__ == '__main__':
    appctxt = ApplicationContext()       # 1. Instantiate ApplicationContext
    window = StartWindow()

    window.show()
    exit_code = appctxt.app.exec_()      # 2. Invoke appctxt.app.exec_()
    sys.exit(exit_code)