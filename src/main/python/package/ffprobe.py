
# A crude wrapper to call the ffprobe utility on a video file
# The file path is set to the default binary location on MacOs but you can specify an
# alternate location as an argument

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


import json
import pathlib
import subprocess as sp




def ffprobe(video_file, ffprobe_path="/usr/local/bin/ffprobeA"):
    """
    ffprobe runs the ffprobe binary command onto the selected video file
    :param video_file: (string) the video file path
    :param ffprobe_path :(string) path to the ffprobe executable, by default set to a MacOs default location
    :return: a dict containing the ffprobe report
    """
    path = pathlib.Path(video_file)

    command = f'{ffprobe_path} -v quiet -print_format json -show_format -show_streams "{path.__str__()}"'
    try:
        proc = sp.check_output(command, shell=True)
        return json.loads(proc.decode())
    except sp.CalledProcessError:
        return False  # There was an error - command exited with non-zero code


def is_video(file, ffprobe_path="/usr/local/bin/ffprobe"):
    """
    Check if the input file is a video file
    :param file: (string) the video file path
    :param ffprobe_path :(string) path to the ffprobe executable, by default set to a MacOs default location
    :return: Boolean
    """
    test = ffprobe(file, ffprobe_path)
    if test:
        return True
    else:
        print(test)
        return False


def get_codec(file, ffprobe_path="/usr/local/bin/ffprobe"):
    """
    Return the Codec of the video as a string
    :param ffprobe_path: (string) path to the ffprobe executable, by default set to a MacOs default location
    :param file: (string) the video file path
    :return: (string) Codec
    """
    test = ffprobe(file, ffprobe_path)
    if test:
        if test["format"]["nb_streams"] > 0:
            if test["streams"][0]["codec_type"] == "video":
                a = test["streams"][0]["codec_long_name"]
                b = test["streams"][0]["profile"]
                return f"{a} : {b}"
    else:
        return False


def get_framerate(file, ffprobe_path="/usr/local/bin/ffprobe"):
    """
    Return the video file framerate as a float
    :param ffprobe_path: (string) path to the ffprobe executable, by default set to a MacOs default location
    :param file: (string) the video file path
    :return:(float) framerate
    """
    test = ffprobe(file, ffprobe_path)
    if test:
        if test["format"]["nb_streams"] > 0:
            if test["streams"][0]["codec_type"] == "video":
                a = test["streams"][0]["r_frame_rate"]
            return float(a.split('/')[0])
    else:
        return False


def get_resolution(file, ffprobe_path="/usr/local/bin/ffprobe"):
    """
    Return the width and height in pixels of the video file
    :param ffprobe_path: (string) path to the ffprobe executable, by default set to a MacOs default location
    :param file: (string) the video file path
    :return: (int) width, height
    """
    test = ffprobe(file, ffprobe_path)
    if test:
        if test["format"]["nb_streams"] > 0:
            if test["streams"][0]["codec_type"] == "video":
                return int(test["streams"][0]["width"]), int(test["streams"][0]["height"])
    else:
        return False


def get_duration(file, ffprobe_path="/usr/local/bin/ffprobe"):
    """
    Return the duration in frames of the video
    :param ffprobe_path: (string) path to the ffprobe executable, by default set to a MacOs default location
    :param file: (string) the video file path
    :return: (int) frame_number
    """
    test = ffprobe(file, ffprobe_path)
    if test:
        if test["format"]["nb_streams"] > 0:
            if test["streams"][0]["codec_type"] == "video":
                if test["streams"][0]["codec_name"] == "jpeg2000": #in case of DCP mxf
                    return int(test["streams"][0]["duration_ts"])
                else:
                    return int(test["streams"][0]["nb_frames"])
    else:
        return False
