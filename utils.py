import os
import sys


def resource_path(relative):
    if getattr(sys, "frozen", False):
        base = sys._MEIPASS
    else:
        base = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base, relative)


def get_ffmpeg_path():
    bundled = resource_path("ffmpeg")
    if os.path.isfile(bundled):
        return bundled
    return "ffmpeg"


def get_ffprobe_path():
    bundled = resource_path("ffprobe")
    if os.path.isfile(bundled):
        return bundled
    return "ffprobe"
