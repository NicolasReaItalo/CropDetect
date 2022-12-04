############################################ LICENCE ##################################################################

#This file is part of CropDetect.

#CropDetect is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

#CropDetect is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty
# of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

#You should have received a copy of the GNU General Public License along with Foobar.
# If not, see <https://www.gnu.org/licenses/>. 4
#
############################################ LICENCE ##################################################################


import cv2
import subprocess as sp
import numpy
import time
import os
import datetime
import pandas as pd
import pathlib

from package.ffprobe import is_video, get_framerate, get_duration, get_codec, get_resolution
from package import timecode


LUMA_TRESHOLD = 25  # these thresholds are a bit empirical, found these sweet spots with trial and error
VAR_TRESHOLD = 15











class CropIssue():
    def __init__(self):
        self.start_frame = 0
        self.end_frame = 0
        self.borders = []
        self.var_image = 10000000


class Job_File():

    def __init__(self):
        self.video_path = ''
        self.report_path = '.'
        self.framerate = 0
        self.codec = ''
        self.x_res = 0
        self.y_res = 0
        self.start_frame = 0
        self.start_frame_offset = 0
        self.end_frame = 0
        self.end_frame_offset = 0
        self.done = False
        self.complete = False
        self.last_frame_analysed = 0
        self.analyse_duration = ''
        self.tc_offset = 0
        self.start_time = 0
        self.elapsed_time = 0
        self.top_offset = 0
        self.bottom_offset = 0
        self.right_offset = 0
        self.left_offset = 0
        self.issue_list = []
        self.dict_report = {
            "img_number": [],
            "is_error_up": [],
            "is_error_right": [],
            "is_error_down": [],
            "is_error_left": [],
            "var_image": []
        }
        self.df_report = pd.DataFrame
        self.ffmpeg_path = ""  # fallback value, to be overridden by the fbs wrapper in main.py
        self.ffprobe_path = ""  # fallback value, to be overridden by the fbs wrapper in main.py
        self.error_log = []


    def load_video_file(self, path):
        self.video_path = path
        if not is_video(self.video_path, self.ffprobe_path):
            self.video_path = ''
            return False
        self.end_frame = get_duration(self.video_path, self.ffprobe_path)
        self.x_res, self.y_res = get_resolution(self.video_path, self.ffprobe_path)
        self.framerate = get_framerate(self.video_path, self.ffprobe_path)
        self.end_frame = get_duration(self.video_path, self.ffprobe_path)
        self.codec = get_codec(self.video_path, self.ffprobe_path)
        self.tc_offset = 0
        self.report_path = str(pathlib.Path.home() / 'Desktop')

    def analyse_video(self):

        # create the report folder
        if self.report_path == ".":
            report_folder = pathlib.Path(os.path.dirname(self.video_path))
        else:
            report_folder = pathlib.Path(self.report_path)

        report_folder_name = self.create_report_folder_name()
        report_path = report_folder / report_folder_name
        report_path.mkdir(parents=True, exist_ok=True)
        self.report_path = str(report_path)

        self.issue_list = []
        current_frame = 0
        #        self.start_time = time.clock()
        command = [self.ffmpeg_path,
                   '-i', self.video_path,
                   '-pix_fmt', 'bgr24',  # opencv requires bgr24 pixel format.
                   '-vcodec', 'rawvideo',
                   '-an', '-sn',  # we want to disable audio processing (there is no audio)
                   '-f', 'image2pipe', '-']
        pipe = sp.Popen(command, stdout=sp.PIPE, bufsize=10 ** 8)

        if self.x_res > 2048:
            scale_factor = 4
        else:
            scale_factor = 2

        font = cv2.FONT_HERSHEY_SIMPLEX

        while True:
            # Capture frame-by-frame
            raw_image = pipe.stdout.read(self.x_res * self.y_res * 3)

            image = numpy.frombuffer(raw_image, dtype='uint8')
            image = image.reshape((self.y_res, self.x_res, 3))

            # if the image is over the range of the first frames to analyse
            if current_frame >= self.start_frame_offset:

                # resizing original image to show progress
                resized = cv2.resize(image, (self.x_res // scale_factor, self.y_res // scale_factor), 1, 1)

                self.write_on_image(resized, f'frame:{str(current_frame)}', 0.5, 20, 40)
                self.write_on_image(resized, f'progress:{(round(current_frame / self.end_frame, 2)) * 100} %', 0.5, 20,
                                    70)
                self.write_on_image(resized,
                                    f'Time-Code:{timecode.frame_to_tc_02((current_frame + self.tc_offset), self.framerate)}',
                                    0.5, 20, 100)
                # showing the current image to the user
                cv2.imshow(f'{os.path.basename(self.video_path)}: Analysis in progress, press q to stop',
                           resized )

                # crop external lines
                top_line = image[0 + self.top_offset:1 + self.top_offset, 0 + self.left_offset:self.x_res - self.right_offset]
                bottom_line = image[self.y_res - 1 - self.bottom_offset:self.y_res - self.bottom_offset,
                              0 + self.left_offset:self.x_res - self.right_offset]
                left_line = image[0 + self.top_offset:self.y_res - self.bottom_offset,  self.left_offset:self.left_offset+ 1 ]
                right_line = image[0 + self.top_offset:self.y_res - self.bottom_offset,
                             self.x_res - 1 - self.right_offset:self.x_res - self.right_offset]

                test_top = self.test_line_blanking( top_line)
                test_right = self.test_line_blanking( right_line)
                test_bottom = self.test_line_blanking(bottom_line)
                test_left = self.test_line_blanking( left_line)

                if (test_top or test_right or test_bottom or test_left):  ## blanking error detected
                    self.dict_report["img_number"].append(current_frame)
                    self.dict_report["var_image"].append(int(numpy.var(cv2.cvtColor(image, cv2.COLOR_BGR2GRAY))))
                    if test_top:
                        self.dict_report["is_error_up"].append(True)
                    else:
                        self.dict_report["is_error_up"].append(False)

                    if test_right:
                        self.dict_report["is_error_right"].append(True)
                    else:
                        self.dict_report["is_error_right"].append(False)

                    if test_bottom:
                        self.dict_report["is_error_down"].append(True)
                    else:
                        self.dict_report["is_error_down"].append(False)

                    if test_left:
                        self.dict_report["is_error_left"].append(True)
                    else:
                        self.dict_report["is_error_left"].append(False)

                    self.save_snapshot(image, current_frame)

            else:  ## the image wil not be analysed but still be displayed
                resized = cv2.resize(image, (self.x_res // scale_factor, self.y_res // scale_factor), 1, 1)
                self.write_on_image(resized, 'ANALYSIS SKIPPED ON THIS IMAGE', 0.5, 20, 40)
                # showing the current image to the user
                cv2.imshow(f'{os.path.basename(self.video_path)}: Analysis in progress, press q to stop', resized)

            current_frame += 1

            if cv2.waitKey(1) & 0xFF == ord('q'):
                self.last_frame_analysed = current_frame
                self.elapsed_time = time.clock() - self.start_time
                self.done = True
                break
            if current_frame == (self.end_frame - self.end_frame_offset):
                self.done = True
                self.complete = True
                self.last_frame_analysed = current_frame
                self.elapsed_time = time.clock() - self.start_time
                break
        pipe.stdout.flush()
        cv2.destroyAllWindows()

        self.init_df()  # saving every error frames into a dataframe
        self.issue_list = self.iterate_dataframe(self.df_report)  # iterate through the dataframe to generate a shot
        # by shot issue list

    def test_line_blanking(self, line):
        b_max = numpy.max(line[:, :, 0])
        g_max = numpy.max(line[:, :, 1])
        r_max = numpy.max(line[:, :, 2])


        if (b_max <= LUMA_TRESHOLD and g_max <= LUMA_TRESHOLD and r_max <= LUMA_TRESHOLD):

            nb_line = cv2.cvtColor(line, cv2.COLOR_BGR2GRAY)
            var_line = numpy.var(nb_line)
            if var_line <= VAR_TRESHOLD:
                return True
        return False

    def create_report_folder_name(self):
        base_filename = os.path.basename(self.video_path).split('.')[0]

        if len(base_filename) > 40:
            base_filename = base_filename[0:40]
        t = datetime.datetime.now()
        timestamp = t.strftime("%y%m%d")
        return f"{base_filename}____{timestamp}"

    def save_snapshot(self, img, image_number):
        snapshot_path = self.report_path + '/report_snapshots'
        if not os.path.isdir(snapshot_path):
            os.makedirs(snapshot_path)

        filename = os.path.basename(self.video_path).split('.')[0]
        filename = filename + f'_{image_number}.png'
        # write timecode on image
        self.write_on_image(img, timecode.frame_to_tc_02((image_number), self.framerate), 3,
                            img.shape[1] // 10,
                            img.shape[0] // 10)
        self.write_on_image(img, f'Image:{(image_number)}', 3, img.shape[1] // 3, img.shape[0] // 3)

        if img.shape[1] <= 1920:
            scale_factor = 3
        else:
            scale_factor = 6

        resized = cv2.resize(img, (self.x_res // scale_factor, self.y_res // scale_factor), 1, 1)
        path = snapshot_path + '/' + filename
        cv2.imwrite(filename=path, img=resized)
        return

    def write_on_image(self, image, content, size, x, y):
        font = cv2.FONT_HERSHEY_SIMPLEX
        position = (x, y)
        fontScale = size
        fontColor = (20, 20, 220)
        lineType = 2
        cv2.putText(image, content, position, font, fontScale, fontColor, lineType)

    def init_df(self):
        self.df_report = pd.DataFrame(self.dict_report)

    def iterate_dataframe(self, df):
        issue_list = []
        for i in range(len(df)):
            current_frame = df.loc[i, "img_number"]
            current_var = df.loc[i, "var_image"]
            if issue_list != []:  # there is at least  an issue, let's check if the current image belong to this issue
                if current_frame <= (issue_list[-1].end_frame + 48) and (
                        (current_var >= (issue_list[-1].var_image // 2)) and (
                        current_var <= (issue_list[-1].var_image * 2))):
                    issue_list[-1].end_frame = current_frame  # same issue, update the end_frame value
                    if df.loc[i, "is_error_up"] == True:
                        if "UP" not in issue_list[-1].borders:
                            issue_list[-1].borders.append("UP")
                    if df.loc[i, "is_error_down"] == True:
                        if "DOWN" not in issue_list[-1].borders:
                            issue_list[-1].borders.append("DOWN")
                    if df.loc[i, "is_error_left"] == True:
                        if "LEFT" not in issue_list[-1].borders:
                            issue_list[-1].borders.append("LEFT")
                    if df.loc[i, "is_error_right"] == True:
                        if "RIGHT" not in issue_list[-1].borders:
                            issue_list[-1].borders.append("RIGHT")

                else:  # it's a new issue
                    issue = CropIssue()
                    issue.start_frame = current_frame
                    issue.end_frame = current_frame
                    if df.loc[i, "is_error_up"] == True:
                        issue.borders.append("UP")
                    if df.loc[i, "is_error_down"] == True:
                        issue.borders.append("DOWN")
                    if df.loc[i, "is_error_left"] == True:
                        issue.borders.append("LEFT")
                    if df.loc[i, "is_error_right"] == True:
                        issue.borders.append("RIGHT")
                    issue_list.append(issue)
                issue_list[-1].var_image = current_var

            if issue_list == []:  # no issues found previously let's add the first one
                issue = CropIssue()
                issue.start_frame = current_frame
                issue.end_frame = current_frame
                issue.var_image = current_var
                if df.loc[i, "is_error_up"] == True:
                    issue.borders.append("UP")
                if df.loc[i, "is_error_down"] == True:
                    issue.borders.append("DOWN")
                if df.loc[i, "is_error_left"] == True:
                    issue.borders.append("LEFT")
                if df.loc[i, "is_error_right"] == True:
                    issue.borders.append("RIGHT")
                issue_list.append(issue)

        return issue_list

    def generate_edl(self):
        file = os.path.basename(self.video_path).split('.')[0]
        edl_name = f'{file}_markers.edl'
        edl_path = f'{self.report_path}/{edl_name}'
        edl_content = f'TITLE: {file}\n'
        edl_content = edl_content + f'FCM: NON-DROP FRAME\n\n'
        issue_number = 1

        for issue in self.issue_list:
            if issue_number >= 10:
                if issue_number >= 100:
                    edl_issue = f'{issue_number}'
                else:
                    edl_issue = f'0{issue_number}'
            else:
                edl_issue = f'00{issue_number}'

            edl_content = edl_content + f'{edl_issue}  {edl_issue}      V     C        ' \
                                        f'{timecode.frame_to_tc_02(issue.start_frame, self.framerate)} {timecode.frame_to_tc_02(issue.end_frame, self.framerate)} ' \
                                        f'{timecode.frame_to_tc_02(issue.start_frame, self.framerate)} {timecode.frame_to_tc_02(issue.end_frame, self.framerate)}  \n'

            edl_content = edl_content + f' |C:ResolveColorRed |M:{issue_number}-{str(issue.borders)} |D:{(issue.end_frame - issue.start_frame) + 2}\n\n'

            issue_number += 1

        with open(edl_path, "w") as edl:
            edl.write(edl_content)
            edl.close()
        return

    def generate_html_report(self):

        file = os.path.basename(self.video_path).split('.')[0]
        report_path = f'{self.report_path}/{file}_report.html'

        html_file = '<!DOCTYPE html><html><head><meta charset="utf-8"><style type="text/css">@page {size: A4 portrait;}\
        body {font: 20px Helvetica, sans-serif;color: #4d4d4d;background-color:  #ffffff;}h1 {font: 40px Helvetica,\
        sans-serif;color: #423535;text-align: center;}p {text-align: center;}code {color: #423535;}div {\
        background-color: #8c8c8c;width: 1000px;border: none;padding: 10px;\
        margin: 20px;}table,td {table-layout: fixed;width: 235px;padding: 5px;}\
        thead,tfoot {background-color: #8c8c8c;color: #4d4d4d;font: 20px Helvetica, sans-serif;text-align: center;}\
        th{font: 25px Helvetica, sans-serif;color: #4d4d4d;padding: 15px;}tr {text-align: center;padding: 15px;}\
        tr:nth-child(even) {background-color: #595959;color: #fff;}tr:nth-child(odd)  {background-color: #d9d9d9;\
         color:#404040;}.img_thumbnail{width: 235px;}.issue-header {background-color: #8c8c8c;}\
         .logo{align-content: center;width: 100px;}\
         </style><title>Blanking detector Report</title></head><header><div>\
         <h1>Blanking detection report<br></h1></div></header><body>'

        html_file = html_file + f' <div>  <ul><li>file checked :  <code>{os.path.basename(self.video_path)}</code></li>\
                                <li>date :  <code>{datetime.datetime.now()}</code></li>\
                                <li>codec :  <code>{self.codec}</code></li>\
                                <li>definition : <code>{self.x_res}x{self.y_res}</code></li>\
                                <li>framerate : <code>{self.framerate}</code></li>\
                                <li>Duration:  <code>{timecode.frame_to_tc_02((self.end_frame), self.framerate)}</code></li>\
                                </ul></div>'

        if not self.complete:
            html_file = html_file + f'<div><p style ="font: 20px Helvetica, sans-serif;color:#BE1D11; text-align: center;">\
                                      Alert : analysis not complete - Interrupted by user \
                                      at {timecode.frame_to_tc_02(self.last_frame_analysed, self.framerate)}</p></div>'

        if self.issue_list != []:
            html_file = html_file + f'<div><p style="color: white;"> {self.last_frame_analysed} frames checked in {self.elapsed_time} s \
                                <p style="color: #BE1D11;"> {len(self.issue_list)} issues detected</p></p></div>'
        else:
            html_file = html_file + f'<div><p style="color: white;"> {self.last_frame_analysed} frames checked in {self.elapsed_time} s \
                                            <p style="color: green;"> {len(self.issue_list)} issues detected</p></p></div>'

        html_file = html_file + f'<div><table><thead><tr><td class="issue-header">Snapshot</td>\
                                <td class="issue-header">Issue type</td><td class="issue-header">Timecode(In/Out)</td>\
                                <td class="issue-header">Details</td></tr></thead><tbody>'

        for issue in self.issue_list:
            snapshot_path = f'./report_snapshots/{os.path.basename(self.video_path).split(".")[0]}' + f'_{issue.start_frame}.png'
            html_file = html_file + f' <tr><td><a href="{snapshot_path}"><img src="{snapshot_path}"class="img_thumbnail">\
                                 </a></td><td>Black lines detected</td><td>{timecode.frame_to_tc_02((issue.start_frame + self.tc_offset), self.framerate)}\
                                 <br>{timecode.frame_to_tc_02((issue.end_frame + self.tc_offset), self.framerate)}</td><td>{issue.borders}</td></tr>'
        html_file = html_file + f'</tbody></table></div></body><footer> Written by Nicolas Rea<br> ' \
                                f'Check <a href="https://github.com/NicolasReaItalo/CropDetect">' \
                                f'https://github.com/NicolasReaItalo/CropDetect</a> for source code.</footer></html>'

        with open(report_path, "w") as report:
            report.write(html_file)
            report.close()
        return

    def generate_csv(self):
        file = os.path.basename(self.video_path).split('.')[0]
        report_path = f'{self.report_path}/{file}_report.csv'
        self.df_report.to_csv(report_path)


if __name__ == '__main__':
    projet = Job_File()
    projet.ffmpeg_path = "/usr/local/bin/ffmpeg"
    projet.ffprobe_path = "/usr/local/bin/ffprobe"
    projet.load_video_file("/Users/user/Documents/DEF/Version_0-5/test_ffprobe/test-23.mov")
    projet.analyse_video()
    projet.generate_html_report()
    projet.generate_csv()
    projet.generate_edl()
