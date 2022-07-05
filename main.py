import os

from fbs_runtime.application_context.PySide2 import ApplicationContext
from PySide2 import QtWidgets, QtCore

import sys

from package.ffprobe import is_video
from package.videocheck import Job_File

# Main logic<
job_list = []


class Window(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.ffmpeg_path = "."
        self.ffprobe_path = "."

        # MAIN LAYOUT
        self.disposition = QtWidgets.QGridLayout()
        # LEFT LIST OF JOBS
        self.job_list_widget = QtWidgets.QListWidget()

        # SCROLLABLE PANEL FOR JOBS SETUP AND DESCRIPTION
        self.panel = QtWidgets.QScrollArea()
        self.panel_widget = QtWidgets.QWidget()
        self.panel_vbox = QtWidgets.QVBoxLayout()
        self.panel.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.panel.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.panel.setWidgetResizable(True)
        self.panel.setWidget(self.panel_widget)

        # WIDGETS
        self.add_job_button = QtWidgets.QPushButton("Add Job")
        self.remove_button = QtWidgets.QPushButton("Remove Job")
        self.start_button = QtWidgets.QPushButton("START")

        self.panel_widget.setLayout(self.panel_vbox)

        for job in job_list:
            self.job_list_widget.addItem(job)

        # Connections

        self.job_list_widget.itemClicked.connect(self.JobClicked)
        self.start_button.clicked.connect(self.start)
        self.add_job_button.clicked.connect(self.press_add_job_button)
        self.remove_button.clicked.connect(self.remove_job)

        ### Final disposition
        self.disposition.addWidget(self.job_list_widget, 0, 0, 3, 5)
        self.disposition.addWidget(self.panel, 0, 4, 3, 5)
        self.disposition.addWidget(self.add_job_button, 4, 0, 1, 1)
        self.disposition.addWidget(self.remove_button, 4, 1, 1, 1)
        self.disposition.addWidget(self.start_button, 4, 2, 1, 1)

        self.main_widget = QtWidgets.QWidget()
        self.main_widget.setLayout(self.disposition)
        self.setCentralWidget(self.main_widget)
        self.setCentralWidget(self.main_widget)

        self.resize(1200, 700)
        self.setWindowTitle('Mazurka')
        self.show()

    def JobClicked(self):
        item = self.job_list_widget.currentItem().text()
        ##clear all widgets
        clearLayout(self.panel_vbox)
        self.generate_report_layout()

    def start(self):
        for job in job_list:
            if not job.done:
                job.analyse_video()
                job.generate_html_report()
                job.generate_csv()
                job.generate_edl()
        self.refresh_job_list_widget()

    def remove_job(self):
        if len(job_list) > 0:
            del job_list[self.job_list_widget.currentRow()]
        self.refresh_job_list_widget()
        clearLayout(self.panel_vbox)

    def refresh_job_list_widget(self):
        cancel_label = "State :Canceled"
        done_label = "State :Completed "
        todo_label = "State : No executed yet "

        self.job_list_widget.clear()
        for job in job_list:
            state = ""
            if job.done and job.complete:
                state = done_label

            if not job.done:
                state = todo_label
            if job.done and not job.complete:
                state = cancel_label

            if job.job_type == "File":
                filename = os.path.basename(job.video_path)
                self.job_list_widget.addItem(f"# {filename}\n"
                                             f"{state}")

    def generate_report_layout(self):
        cancel_label = "State :Canceled"
        done_label = "State :Completed "

        clearLayout(self.panel_vbox)
        job = job_list[self.job_list_widget.currentRow()]
        titre = QtWidgets.QLabel(os.path.basename(job.video_path))
        titre.setStyleSheet("font-size: 29px;")

        # dummy code for test

        if not job.done:
            state = "Status : To do"
            status = QtWidgets.QLabel(state)
            status.setStyleSheet("font-size: 16px; color: #02e894")

        if job.done and job.complete:
            state = done_label
            status = QtWidgets.QLabel(state)
            status.setStyleSheet("font-size: 16px; color: #02e894")

        if job.done and not job.complete:
            state = cancel_label
            status = QtWidgets.QLabel(state)
            status.setStyleSheet("font-size: 16px; color: #c95d5d")

        self.panel_vbox.addWidget(titre)
        self.panel_vbox.addWidget(status)

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
        job_list.append(job)
        self.refresh_job_list_widget()


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
    stylesheet = appctxt.get_resource('SpyBot.qss')

    appctxt.app.setStyleSheet(open(stylesheet).read())
    window.show()
    exit_code = appctxt.app.exec_()  # 2. Invoke appctxt.app.exec_()
    sys.exit(exit_code)
