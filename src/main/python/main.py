############################################ LICENCE ##################################################################

#This file is part of CropDetect.

#CropDetect is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

#CropDetect is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty
# of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

# see <https://www.gnu.org/licenses/>. 4
#
############################################ LICENCE ##################################################################

import os

import subprocess as sp
import pathlib
from fbs_runtime.application_context.PySide2 import ApplicationContext
from PySide2 import QtWidgets, QtCore, QtGui

import sys

from package.ffprobe import is_video
from package.videocheck import Job_File



VERSION = "1.0"


class Window(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.ffmpeg_path = "."
        self.ffprobe_path = "."
        self.job_list = []

        # MAIN LAYOUT
        self.disposition = QtWidgets.QGridLayout()
        # LEFT LIST OF JOBS
        self.job_list_widget = QtWidgets.QListWidget()
        self.job_list_widget.setMinimumWidth(450)
        self.job_list_widget.setFixedWidth(450)
        self.job_list_widget.setAcceptDrops(True)
        # TOP RIGHT : header with job infos
        self.header_panel = QtWidgets.QWidget()

        # SCROLLABLE PANEL FOR JOBS SETUP
        self.panel = QtWidgets.QScrollArea()
        self.panel_widget = QtWidgets.QWidget()
        self.panel_vbox = QtWidgets.QVBoxLayout()
        self.panel.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.panel.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.panel.setWidgetResizable(True)
        self.panel.setWidget(self.panel_widget)

        # WIDGETS
        self.add_job_button = QtWidgets.QPushButton("Add Job")
        self.remove_button = QtWidgets.QPushButton("Remove Job")
        self.start_button = QtWidgets.QPushButton("START")

        self.panel_widget.setLayout(self.panel_vbox)

        for job in self.job_list:
            self.job_list_widget.addItem(job)

        self.init_vbox_panel()
        self.init_header_panel()
        self.refresh_vbox_panel()

        # Connections

        self.job_list_widget.currentItemChanged.connect(self.JobClicked)
        self.start_button.clicked.connect(self.start)
        self.add_job_button.clicked.connect(self.press_add_job_button)
        self.remove_button.clicked.connect(self.remove_job)

        ### Final disposition
        self.disposition.addWidget(self.job_list_widget, 0, 0, 4, 3)
        self.disposition.addWidget(self.panel, 1, 3, 3, 5)
        self.disposition.addWidget(self.header_panel, 0, 3, 1, 5)
        self.disposition.addWidget(self.add_job_button, 4, 0, 1, 1)
        self.disposition.addWidget(self.remove_button, 4, 1, 1, 1)
        self.disposition.addWidget(self.start_button, 4, 7, 1, 1)


        self.main_widget = QtWidgets.QWidget()
        self.main_widget.setLayout(self.disposition)
        self.setCentralWidget(self.main_widget)
        self.setCentralWidget(self.main_widget)
        self.resize(1200, 800)
        self.setWindowTitle(f'CropDetect : black bars detection - by Nicolas Rea - Version {VERSION}')
        self.show()

    def dropEvent(self, e):
        """
        Drop files directly onto the widget
        File locations are stored in fname
        :param e:
        :return:
        """
        if e.mimeData().hasUrls:
            e.setDropAction(QtCore.Qt.CopyAction)
            e.accept()
            # Workaround for OSx dragging and dropping
            for url in e.mimeData().urls():
              fname = str(url.toLocalFile())
              print(fname)
        else:
            e.ignore()





    def JobClicked(self):
        self.refresh_header_panel()
        self.refresh_vbox_panel()

    def start(self):
        for job in self.job_list:
            if not job.done:
                job.analyse_video()
                job.generate_html_report()
                job.generate_csv()
                job.generate_edl()
        self.refresh_job_list_widget()
        self.refresh_vbox_panel()
        self.job_list_widget.setCurrentRow(-1)

    def remove_job(self):
        if len(self.job_list) > 0:
            del self.job_list[self.job_list_widget.currentRow()]
        self.refresh_job_list_widget()
        self.refresh_vbox_panel()
        self.refresh_header_panel()

    def refresh_job_list_widget(self):
        cancel_label = "❗️ Canceled"
        done_label = "✅ Completed "
        todo_label = "ℹ️ Not executed yet "

        self.job_list_widget.clear()
        for job in self.job_list:
            state = ""
            if job.done and job.complete:
                state = done_label

            if not job.done:
                state = todo_label
            if job.done and not job.complete:
                state = cancel_label

            filename = os.path.basename(job.video_path)
            self.job_list_widget.addItem(f"\n ▶️️  {filename}\n {state}\n")
        if len(self.job_list) > 0:
            self.job_list_widget.setCurrentRow(0)

    def init_header_panel(self):
        ## HEADER  WIDGETS INIT
        self.header = QtWidgets.QWidget(self)
        self.header.setMaximumHeight(250)
        self.header.setMinimumHeight(250)
        self.header_vbox_layout = QtWidgets.QVBoxLayout()
        self.header_filename = QtWidgets.QLabel("click on job to display information")
        self.header_filename.setStyleSheet("font-size: 19px;")
        self.header_filename.setFixedHeight(22)
        self.header_status = QtWidgets.QLabel("Status : - ")
        self.header_status.setStyleSheet("font-size: 14px;")
        self.header_codec = QtWidgets.QLabel("Codec : - ")
        self.header_framerate = QtWidgets.QLabel("Framerate : - ")
        self.header_resolution = QtWidgets.QLabel("Resolution : - ")
        self.header_duration = QtWidgets.QLabel("Duration : - ")
        self.header_report_button = QtWidgets.QPushButton("Open Report")
        self.header_report_button.setMaximumWidth(120)
        self.header_report_button.setDisabled(True)

        self.header_vbox_layout.addWidget(self.header_filename)
        self.header_vbox_layout.addWidget(self.header_codec)
        self.header_vbox_layout.addWidget(self.header_framerate)
        self.header_vbox_layout.addWidget(self.header_resolution)
        self.header_vbox_layout.addWidget(self.header_duration)
        self.header_vbox_layout.addWidget(self.header_status)
        self.header_vbox_layout.addWidget(self.header_report_button)

        self.header_panel.setLayout(self.header_vbox_layout)

        self.header_report_button.clicked.connect(self.press_open_report)

    def init_vbox_panel(self):

        # Choose report folder widgets
        self.choose_report_label = QtWidgets.QLabel("By default the report will be created in the same folder as the "
                                                    "source video file")
        self.choose_report_label.setStyleSheet("font-style : italic;")
        self.choose_report_label.setStyleSheet("color: #ABB2B9;")
        self.choose_report_button = QtWidgets.QPushButton("Choose Report Folder")
        self.choose_report_button.setMaximumWidth(150)
        self.choose_report_layout = QtWidgets.QHBoxLayout()
        self.choose_report_layout.addWidget(self.choose_report_button)
        self.choose_report_layout.addWidget(self.choose_report_label)
        self.choose_report_widget = QtWidgets.QWidget()
        self.choose_report_widget.setLayout(self.choose_report_layout)

        # skip first frames widget elements
        self.skip_frames_widget = QtWidgets.QWidget()
        self.skip_frames_layout = QtWidgets.QHBoxLayout()
        self.skip_frames_layout.setSpacing(10)
        self.firstframes_skip_edit = QtWidgets.QSpinBox()
        self.firstframes_skip_edit.setRange(0, 999999)
        self.firstframes_skip_edit.setMaximumWidth(80)
        self.skip_label = QtWidgets.QLabel("Skip analysis on first :")
        self.skip_label.setMaximumWidth(140)
        self.skip_frames_layout.addWidget(self.skip_label)
        self.skip_frames_layout.addWidget(self.firstframes_skip_edit)
        self.skip_frames_layout.addWidget(QtWidgets.QLabel("frames"))
        self.skip_frames_widget.setLayout(self.skip_frames_layout)

        # skip last frames widget elements
        self.lastframes_skip_edit = QtWidgets.QSpinBox()
        self.lastframes_skip_edit.setRange(0, 999999)
        self.lastframes_skip_edit.setMaximumWidth(80)
        self.skip_label = QtWidgets.QLabel("And on last :")
        self.skip_label.setMaximumWidth(140)
        self.skip_frames_layout.addWidget(self.skip_label)
        self.skip_frames_layout.addWidget(self.lastframes_skip_edit)
        self.skip_frames_layout.addWidget(QtWidgets.QLabel("frames"))
        self.skip_frames_widget.setLayout(self.skip_frames_layout)

        # TOP OFFSET
        self.top_offset_widget = QtWidgets.QWidget()
        self.top_offset_layout = QtWidgets.QHBoxLayout()
        self.top_offset_edit = QtWidgets.QSpinBox()
        self.top_offset_edit.setRange(0, 9999)
        self.top_offset_edit.setMaximumWidth(80)

        self.top_offset_layout.addWidget(self.top_offset_edit)
        self.top_offset_widget.setLayout(self.top_offset_layout)

        # HORIZONTAL OFFSET
        self.horizontal_offset_widget = QtWidgets.QWidget()
        self.horizontal_offset_layout = QtWidgets.QHBoxLayout()

        self.left_offset_edit = QtWidgets.QSpinBox()
        self.left_offset_edit.setRange(0, 9999)
        self.left_offset_edit.setMaximumWidth(80)

        self.right_offset_edit = QtWidgets.QSpinBox()
        self.right_offset_edit.setRange(0, 9999)
        self.right_offset_edit.setMaximumWidth(80)

        self.horizontal_offset_layout.addWidget(self.right_offset_edit)
        self.horizontal_offset_layout.addWidget(self.left_offset_edit)
        self.horizontal_offset_widget.setLayout(self.horizontal_offset_layout)


        # BOTTOM OFFSET
        self.bottom_offset_widget = QtWidgets.QWidget()
        self.bottom_offset_layout = QtWidgets.QHBoxLayout()
        self.bottom_offset_edit = QtWidgets.QSpinBox()
        self.bottom_offset_edit.setRange(0, 9999)
        self.bottom_offset_edit.setMaximumWidth(80)

        self.bottom_offset_layout.addWidget(self.bottom_offset_edit)
        self.bottom_offset_widget.setLayout(self.bottom_offset_layout)



        # Source color space selection
        self.color_space_widget = QtWidgets.QWidget()
        self.color_space_layout = QtWidgets.QHBoxLayout()
        self.color_space_selector = QtWidgets.QComboBox()
        self.color_space_selector.addItem("REC 709 (gamma 2,4)")
        self.color_space_selector.addItem("P3 DCI (gamma 2,6)")
        self.color_space_selector.addItem("P3 D65 (gamma 2,6)")
        self.color_space_selector.addItem("DCI XYZ")
        self.color_space_selector.setEnabled(False)

        color_space_label = QtWidgets.QLabel("Source color space :")
        color_space_label.setMaximumWidth(150)
        color_space_label.setEnabled(False)
        #self.color_space_layout.addWidget(color_space_label)
       # self.color_space_layout.addWidget(self.color_space_selector)
       # self.color_space_widget.setLayout(self.color_space_layout)



        self.panel_vbox.addWidget(self.choose_report_widget)
        self.panel_vbox.addWidget(QtWidgets.QLabel(" "*65 +"_________________________________"))

        self.panel_vbox.addWidget(self.skip_frames_widget)

        self.panel_vbox.addWidget(QtWidgets.QLabel(" "*65 +"_________________________________"))
        self.panel_vbox.addWidget(QtWidgets.QLabel("TOP/BOTTOM/RIGHT/LEFT offsets ( in pixel ) :"))
        self.panel_vbox.addWidget(self.top_offset_widget)
        self.panel_vbox.addWidget(self.horizontal_offset_widget)
        self.panel_vbox.addWidget(self.bottom_offset_widget)
        self.panel_vbox.addWidget(QtWidgets.QLabel(" "*65 +"_________________________________"))
        self.panel_vbox.addWidget(self.color_space_widget)

        # CONNECTIONS
        self.choose_report_button.clicked.connect(self.press_report_folder)
        self.firstframes_skip_edit.valueChanged.connect(self.skip_start_value_changed)
        self.lastframes_skip_edit.valueChanged.connect(self.skip_end_value_changed)
        self.top_offset_edit.valueChanged.connect(self.top_offset_changed)
        self.bottom_offset_edit.valueChanged.connect(self.bottom_offset_changed)
        self.left_offset_edit.valueChanged.connect(self.left_offset_changed)
        self.right_offset_edit.valueChanged.connect(self.right_offset_changed)



    def refresh_header_panel(self):
        if len(self.job_list) == 0 :
            self.header_report_button.setDisabled(True)
            self.header_filename.setText("click on job to display information")
            self.header_filename.setStyleSheet("font-size: 19px;")
            self.header_status.setText("Status : - ")
            self.header_status.setStyleSheet("color: #AEB6BF; font-size: 14px;")
            self.header_codec.setText("Codec : - ")
            self.header_duration.setText("Duration : - ")
            self.header_resolution.setText("Resolution : - ")
            self.header_framerate.setText("Framerate : - ")



        else:

            job = self.job_list[self.job_list_widget.currentRow()]

            state = ""
            if job.done and job.complete:
                state = f" Analysis complete : {len(job.issue_list)} issue(s) found"
                self.header_report_button.setDisabled(False)
                self.header_status.setStyleSheet("color: #328930; font-size: 14px;")
            if not job.done:
                state = "Analysis not executed yet "
                self.header_status.setStyleSheet("color: #AEB6BF; font-size: 14px;")
                self.header_report_button.setDisabled(True)

            if job.done and not job.complete:
                state = f"Analysis not complete - canceled by user : : {len(job.issue_list)} issue(s) found"
                self.header_report_button.setDisabled(False)
                self.header_status.setStyleSheet("color: #DC7633; font-size: 14px;")

            # HEADER GENERATION
            filename = os.path.basename(job.video_path)
            self.header_filename.setText(filename)
            if len(filename) >= 40:
                self.header_filename.setStyleSheet("font-size: 12px;")
            else:
                self.header_filename.setStyleSheet("font-size: 19px;")
            self.header_codec.setText(f"Codec : {job.codec}")
            self.header_framerate.setText(f"Framerate : {job.framerate} frames.s")
            self.header_resolution.setText(f'Resolution : {job.x_res}x{job.y_res} pixels')
            self.header_duration.setText(f"Duration : {job.end_frame} frames")
            self.header_status.setText(f"Status : {state}")

    def refresh_vbox_panel(self):
        if len(self.job_list) == 0:
            self.choose_report_button.setEnabled(False)
            self.choose_report_label.setEnabled(False)
            self.choose_report_label.setText("By default the report folder will be created on Desktop")
            self.firstframes_skip_edit.setEnabled(False)
            self.lastframes_skip_edit.setEnabled(False)
            self.right_offset_edit.setEnabled(False)
            self.left_offset_edit.setEnabled(False)
            self.top_offset_edit.setEnabled(False)
            self.bottom_offset_edit.setEnabled(False)
            return
        job = self.job_list[self.job_list_widget.currentRow()]
        self.choose_report_button.setEnabled(True)
        self.choose_report_label.setEnabled(True)
        self.choose_report_label.setText(job.report_path)
        self.firstframes_skip_edit.setEnabled(True)
        self.firstframes_skip_edit.setValue(job.start_frame_offset)
        self.lastframes_skip_edit.setEnabled(True)
        self.lastframes_skip_edit.setValue(job.end_frame_offset)
        self.top_offset_edit.setEnabled(True)
        self.top_offset_edit.setValue(job.top_offset)
        self.bottom_offset_edit.setEnabled(True)
        self.bottom_offset_edit.setValue(job.bottom_offset)
        self.right_offset_edit.setEnabled(True)
        self.right_offset_edit.setValue(job.right_offset)
        self.left_offset_edit.setEnabled(True)
        self.left_offset_edit.setValue(job.left_offset)







    def press_add_job_button(self):
        job = Job_File()
        # Choosing video file to analyse
        f = QtWidgets.QFileDialog.getOpenFileUrl(self, "Select Video File")
        file_path = f[0].toLocalFile()
        # update the binaries path
        job.ffmpeg_path = self.ffmpeg_path
        job.ffprobe_path = self.ffprobe_path

        if is_video(file_path, self.ffprobe_path):
            job.load_video_file(file_path)
        else:
            error = QtWidgets.QMessageBox()
            error.setText(f"This is not a valid Video File:{file_path}")
            error.exec_()
            return

        # append job
        self.job_list.append(job)
        self.refresh_job_list_widget()

    def press_open_report(self):
        job = self.job_list[self.job_list_widget.currentRow()]
        path = pathlib.Path(job.report_path)

        command = f'open "{path.__str__()}"'
        try:
            proc = sp.check_output(command, shell=True)
            return
        except sp.CalledProcessError:
            return False

    def press_report_folder(self):
        job = self.job_list[self.job_list_widget.currentRow()]
        # Choosing a directory to save the report
        job.report_path = str(QtWidgets.QFileDialog.getExistingDirectory(self, "Select Directory"))
        self.choose_report_label.setText(job.report_path)


    def skip_start_value_changed(self):
        job = self.job_list[self.job_list_widget.currentRow()]
        job.start_frame_offset = self.firstframes_skip_edit.value()

    def skip_end_value_changed(self):
        job = self.job_list[self.job_list_widget.currentRow()]
        job.end_frame_offset = self.lastframes_skip_edit.value()

    def top_offset_changed(self):
        job = self.job_list[self.job_list_widget.currentRow()]
        job.top_offset = self.top_offset_edit.value()

    def bottom_offset_changed(self):
        job = self.job_list[self.job_list_widget.currentRow()]
        job.bottom_offset = self.bottom_offset_edit.value()

    def right_offset_changed(self):
        job = self.job_list[self.job_list_widget.currentRow()]
        job.right_offset = self.right_offset_edit.value()

    def left_offset_changed(self):
        job = self.job_list[self.job_list_widget.currentRow()]
        job.left_offset = self.left_offset_edit.value()






# utility function
def clearLayout(layout):
    while layout.count():
        child = layout.takeAt(0)
        if child.widget():
            child.widget().deleteLater()


if __name__ == '__main__':
    appctxt = ApplicationContext()  # 1. Instantiate ApplicationContext
    window = Window()

    # ressources : ffprobe and ffmpeg binaries + ui stylesheet
    window.ffmpeg_path = appctxt.get_resource("ffmpeg")
    window.ffprobe_path = appctxt.get_resource("ffprobe")
    stylesheet = appctxt.get_resource('Style.qss')

    appctxt.app.setStyleSheet(open(stylesheet).read())
    window.show()
    exit_code = appctxt.app.exec_()  # 2. Invoke appctxt.app.exec_()
    sys.exit(exit_code)
