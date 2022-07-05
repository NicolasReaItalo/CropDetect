
# A crude wrapper to call the ffprobe utility on a video file
# The file path is set to the default binary location on MacOs but you can specify an
# alternate location as an argument

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
                return test["streams"][0]["codec_long_name"]
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
                a = test["streams"][0]["time_base"]
            return int(a.split('/')[1])
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
                return int(test["streams"][0]["nb_frames"])
    else:
        return False
