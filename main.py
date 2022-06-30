import os

from fbs_runtime.application_context.PySide2 import ApplicationContext
from PySide2 import QtWidgets, QtCore, QtWebEngineWidgets

import sys

from package import timecode
from package.videocheck import is_video, Job_File

#### DUMMY CODE
LOREM = "Lorem ipsum dolor sit amet consectetur adipisicing elit. Maxime mollitia,\n" \
        "molestiae quas vel sint commodi repudiandae consequuntur voluptatum laborum\n" \
        "numquam blanditiis harum quisquam eius sed odit fugiat iusto fuga praesentium\n" \
        "optio, eaque rerum! Provident similique accusantium nemo autem. Veritatis\n" \
        "obcaecati tenetur iure eius earum ut molestias architecto voluptate aliquam\n" \
        "ihil, eveniet aliquid culpa officia aut! Impedit sit sunt quaerat, odit,\n" \
        "tenetur error, harum nesciunt ipsum debitis quas aliquid. Reprehenderit,\n" \
        "quia. Quo neque error repudiandae fuga? Ipsa laudantium molestias eos \n" \
        "sapiente officiis modi at sunt excepturi expedita sint? Sed quibusdam\n" \
        "recusandae alias error harum maxime adipisci amet laborum. Perspiciatis\n " \
        "minima nesciunt dolorem! Officiis iure rerum voluptates a cumque velit \n" \
        "quibusdam sed amet tempora. Sit laborum ab, eius fugit doloribus tenetur \n" \
        "fugiat, temporibus enim commodi iusto libero magni deleniti quod quam \n" \
        "consequuntur! Commodi minima excepturi repudiandae velit hic maxime\n" \
        "doloremque. Quaerat provident commodi consectetur veniam similique ad \n" \
        "earum omnis ipsum saepe, voluptas, hic voluptates pariatur est explicabo \n" \
        "fugiat, dolorum eligendi quam cupiditate excepturi mollitia maiores labore \n" \
        "suscipit quas? Nulla, placeat. Voluptatem quaerat non architecto ab laudantium\n" \
        "modi minima sunt esse temporibus sint culpa, recusandae aliquam numquam \n" \
        "totam ratione voluptas quod exercitationem fuga. Possimus quis earum veniam\n " \
        "quasi aliquam eligendi, placeat qui corporis!\n"




# ##Main logic<
job_list = []






class Window(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.ffmpeg_path = "."
        self.ffprobe_path = "."

# MAIN LAYOUT
        self.disposition = QtWidgets.QGridLayout()
# LEFT LIST OF JOBS
        self.job_list_widget =  QtWidgets.QListWidget()

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
## Dummy code to populate list widget
        for job in job_list:
            self.job_list_widget.addItem(job)


### Connections

        self.job_list_widget.itemClicked.connect(self.JobClicked)
        self.start_button.clicked.connect(self.start)
        self.add_job_button.clicked.connect(self.press_add_job_button)
        self.remove_button.clicked.connect(self.remove_job)

### Final disposition
        self.disposition.addWidget(self.job_list_widget, 0, 0, 3, 5)
        self.disposition.addWidget(self.panel,0,4,3,5)
        self.disposition.addWidget(self.add_job_button,4,0,1,1)
        self.disposition.addWidget(self.remove_button,4,1,1,1)
        self.disposition.addWidget(self.start_button,4,2,1,1)


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

        #dummy code for test


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
        path = f[0].toLocalFile()
        if is_video(path):
            job.load_video_file(path)
        else:
            error = QtWidgets.QMessageBox()
            error.setText(f"This is not a valid Video File:{path}")
            error.exec_()
            return
        # update the binaries path
        job.ffmpeg_path = self.ffmpeg_path
        job.ffprobe_path = self.ffprobe_path
        # append job
        job_list.append(job)
        self.refresh_job_list_widget()





## utility function
def clearLayout(layout):
  while layout.count():
    child = layout.takeAt(0)
    if child.widget():
      child.widget().deleteLater()






if __name__ == '__main__':
    appctxt = ApplicationContext()       # 1. Instantiate ApplicationContext
    window = Window()

 # ressources : ffprobe and ffmpeg bianries + ui stylesheet
    window.ffmpeg_path = appctxt.get_resource("ffmpeg")
    ffprobe_path = appctxt.get_resource("ffprobe")
    stylesheet = appctxt.get_resource('SpyBot.qss')




    appctxt.app.setStyleSheet(open(stylesheet).read())
    window.show()
    exit_code = appctxt.app.exec_()      # 2. Invoke appctxt.app.exec_()
    sys.exit(exit_code)