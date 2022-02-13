import cv2
import subprocess as sp
import numpy
import time

from package import timecode

from ffprobe import FFProbe

import os
import json
import datetime
import pandas as pd


def is_video(file):
    """Check if the file referenced is a valid video codec
    :param file : string path to a video file
    """
    if os.path.exists(file):
        metadata = FFProbe(file)
        if len(metadata.streams) > 0:
            if metadata.streams[0].is_video():
                return True
    return False


class CropIssue():
    def __init__(self):
        self.start_frame = 0
        self.end_frame = 0
        self.borders = []
        self.var_image = 10000000




class JobDir():
    def __init__(self):
        self.job_type = "Dir"
        self.dir_path = ""





class Job_File():

    def __init__(self):
        self.job_type = "File"
        self.video_path = ''
        self.report_path = ''
        self.framerate = 0
        self.codec = ''
        self.x_res = 0
        self.y_res = 0
        self.x_inner = 0
        self.y_inner = 0
        self.start_frame = 0
        self.end_frame = 0
        self.complete = False
        self.last_frame_analysed = 0
        self.analyse_duration = ''
        self.tc_offset = 0
        self.start_time = 0
        self.elapsed_time = 0
        self.issue_list = []
        self.dict_report = {
            "img_number": [],
            "is_error_up": [],
            "is_error_right": [],
            "is_error_down": [],
            "is_error_left": [],
            "var_image": []
        }
        self.df_report = []

    def get_resolution(self):
        if os.path.exists(self.video_path):
            metadata = FFProbe(self.video_path)
            return metadata.streams[0].frame_size()
        return False

    def get_framerate(self):
        if os.path.exists(self.video_path):
            metadata = FFProbe(self.video_path)
            return metadata.streams[0].__dict__.get('framerate')
        return False

    def get_duration_frames(self):
        if os.path.exists(self.video_path):
            metadata = FFProbe(self.video_path)
            return metadata.streams[0].frames()
        return False

    def get_codec(self):
        """return the codec of the video referenced in self.video_path
                return False is no file is found"""
        if os.path.exists(self.video_path):
            metadata = FFProbe(self.video_path)
            return metadata.streams[0].codec_description()
        return False

    def get_timecode(self):
        """return the starting tc of the video referenced in self.video_path
        return False is no file is found"""
        if os.path.exists(self.video_path):
            stream = os.popen(f'ffprobe  -show_streams -print_format json {self.video_path}')
            a = stream.read()
            dictionnaire = json.loads(a)
            tc = dictionnaire.get('streams')[-1].get('tags').get('timecode')
            if not tc:
                print('impossible de lire le tc')
                return 0
            return timecode.tc_str_to_frames(tc, self.framerate)
        return False

    def is_video(self):
        """Check if the file referenced in self.video_path is a valid video codec"""
        if os.path.exists(self.video_path):
            metadata = FFProbe(self.video_path)
            if len(metadata.streams) > 0:
                if metadata.streams[0].is_video():
                    return True
        return False

    def analyse_video(self):

        if not self.is_video():
            return False
        self.issue_list = []
        current_frame = 0
        #        self.start_time = time.clock()
        command = ["ffmpeg",
                   '-i', self.video_path,  # fifo is the named pipe
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

            # resizing original image to show progress
            resized = cv2.resize(image, (self.x_res // scale_factor, self.y_res // scale_factor), 1, 1)

            self.write_on_image(resized, f'frame:{str(current_frame)}', 0.5, 20, 40)
            self.write_on_image(resized, f'progres:{(round(current_frame / self.end_frame, 1)) * 100} %', 0.5, 20, 70)
            self.write_on_image(resized,
                                f'Time-Code:{timecode.frame_to_tc_02((current_frame + self.tc_offset), self.framerate)}',
                                0.5, 20, 100)
            self.write_on_image(resized, f'Image:{(current_frame)}', 0.5, 20, 130)

            cv2.imshow(f'{os.path.basename(self.video_path)}: Analyse in progress, press q to stop',
                       resized)

            # cropping the image to get the 4 exterior lines to check

            top_line = image[0:1, 0:self.x_res, :]
            bottom_line = image[self.y_res - 1: self.y_res, 0:self.x_res, :]
            left_line = image[0:self.y_res, 0:1, :]
            right_line = image[0:self.y_res, self.x_res - 1:self.x_res, :]

            test_top = self.test_line_blanking(image, top_line)
            test_right = self.test_line_blanking(image, right_line)
            test_bottom = self.test_line_blanking(image, bottom_line)
            test_left = self.test_line_blanking(image, left_line)

            if (test_top or test_right or test_bottom or test_left):  ## blanking error detected
                self.dict_report["img_number"].append(current_frame)
                self.dict_report["var_image"].append(int(numpy.var(image)))
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

            current_frame += 1

            if cv2.waitKey(1) & 0xFF == ord('q'):
                self.last_frame_analysed = current_frame
                self.elapsed_time = time.clock() - self.start_time
                break
            if current_frame == self.end_frame:
                self.complete = True
                self.last_frame_analysed = current_frame
                self.elapsed_time = time.clock() - self.start_time
                break
        pipe.stdout.flush()
        cv2.destroyAllWindows()
        self.init_df()

    def test_line_blanking(self, image, line):
        b_max = numpy.max(line[:, :, 0])
        g_max = numpy.max(line[:, :, 1])
        r_max = numpy.max(line[:, :, 2])

        if (b_max <= 40 and g_max <= 40 and r_max <= 40):
            var_line = numpy.var(line)
            var_image = numpy.var(image)
            if var_line <= (var_image // 20):
                return True
        return False

    def load_video_file(self, path):
        self.video_path = path
        if not self.is_video():
            self.video_path = ''
            return "Erreur : ce n'est pas un fichier video"

        self.x_res, self.y_res = self.get_resolution()
        self.framerate = self.get_framerate()
        self.end_frame = self.get_duration_frames()
        self.codec = self.get_codec()
        self.tc_offset = self.get_timecode()
        self.report_path = "."

        print(self.generate_header())

    def init_df(self):
        self.df_report = pd.DataFrame(self.dict_report)

    def generate_header(self):
        return f"filename: {os.path.basename(self.video_path)} \n {self.codec} \n framerate: {self.framerate} fps \n resolution(px): {self.x_res}x{self.y_res} \n " \
               f"Duration (h:m:s:i) : {timecode.frame_to_tc_02(self.end_frame, self.framerate)}   / {self.end_frame} frames  \n starting timecode: {timecode.frame_to_tc_02((self.start_frame + self.tc_offset), self.framerate)}"

    def save_snapshot(self, img, image_number):
        snapshot_path = self.report_path + '/report_snapshots'
        if not os.path.isdir(snapshot_path):
            os.makedirs(snapshot_path)

        filename = os.path.basename(self.video_path).split('.')[0]
        filename = filename + f'_{image_number}.png'
        # write timecode on image
        self.write_on_image(img, timecode.frame_to_tc_02((image_number + self.tc_offset), self.framerate), 3,
                            img.shape[1] // 10,
                            img.shape[0] // 10)
        self.write_on_image(img, f'Image:{(image_number)}', 3, img.shape[1] // 3, img.shape[0] // 3)

        path = snapshot_path + '/' + filename
        cv2.imwrite(filename=path, img=img)
        return

    def write_on_image(self, image, content, size, x, y):
        font = cv2.FONT_HERSHEY_SIMPLEX
        position = (x, y)
        fontScale = size
        fontColor = (20, 20, 220)
        lineType = 2
        cv2.putText(image, content, position, font, fontScale, fontColor, lineType)

    def iterate_dataframe(self, df):
        issue_list = []
        for i in range(len(df)):
            current_frame = df.loc[i, "img_number"]
            current_var = df.loc[i, "var_image"]
            if issue_list != []: # there is at least  an issue, let's check if the current image belong to this issue
                if current_frame <= (issue_list[-1].end_frame + 24) and ((current_var >= (issue_list[-1].var_image - (issue_list[-1].var_image//5))) and (current_var <= (issue_list[-1].var_image+issue_list[-1].var_image//5))):
                    issue_list[-1].end_frame = current_frame  # same issue, update the end_frame value
                    if df.loc[i, "is_error_up"] == True:
                        if "UP" not in  issue_list[-1].borders:
                            issue_list[-1].borders.append("UP")
                    if df.loc[i, "is_error_down"] == True:
                        if "DOWN" not in  issue_list[-1].borders:
                            issue_list[-1].borders.append("DOWN")
                    if df.loc[i, "is_error_left"] == True:
                        if "LEFT" not in  issue_list[-1].borders:
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

            if issue_list == []:  #  no issues found previously let's add the first one
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



    def generate_html_report(self):
        self.issue_list = self.iterate_dataframe(self.df_report)
        ##debug
        print(self.issue_list)
        for issue in self.issue_list:
            print(issue.start_frame)
            print(issue.end_frame)
            print(issue.borders)
            print("--------------------")


        ##f debuf
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
        html_file = html_file + f'</tbody></table></div></body><footer></footer></html>'

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
    path = "calibration_dataframe48.mov"
    projet.load_video_file(path)
    projet.analyse_video()
    projet.generate_html_report()
    projet.generate_csv()
