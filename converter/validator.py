"""Input validation for the Video to GIF Converter."""

import os
import re
import subprocess

from utils import get_ffmpeg_path


def check_ffmpeg():
    try:
        subprocess.run(
            [get_ffmpeg_path(), "-version"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=5,
        )
        return True
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def validate_video_file(path):
    if not path:
        return False, "No video file selected"
    if not os.path.isfile(path):
        return False, "File does not exist"
    ext = os.path.splitext(path)[1].lower()
    valid_exts = [
        ".mp4", ".mov", ".avi", ".mkv", ".webm",
        ".flv", ".wmv", ".m4v", ".mpeg", ".mpg",
    ]
    if ext not in valid_exts:
        return False, f"Unsupported file type: {ext}"
    return True, "OK"


def validate_output_path(path):
    if not path:
        return False, "No output path specified"
    if not path.endswith(".gif"):
        path += ".gif"
    directory = os.path.dirname(path) or "."
    if not os.path.isdir(directory):
        return False, f"Output directory does not exist: {directory}"
    return True, path


def validate_fps(fps):
    try:
        val = int(fps)
    except (ValueError, TypeError):
        return False, "FPS must be a number"
    if val < 1 or val > 30:
        return False, "FPS must be between 1 and 30"
    return True, val


def validate_time(time_str):
    pattern = r"^(\d{1,2}):(\d{2}):(\d{2})$"
    match = re.match(pattern, time_str.strip())
    if not match:
        return False, "Time must be in HH:MM:SS format"
    h, m, s = int(match.group(1)), int(match.group(2)), int(match.group(3))
    if m > 59 or s > 59:
        return False, "Invalid time values"
    total = h * 3600 + m * 60 + s
    return True, total


def validate_duration(duration_str):
    try:
        val = float(duration_str)
    except (ValueError, TypeError):
        return False, "Duration must be a number"
    if val <= 0:
        return False, "Duration must be greater than 0"
    return True, val


def validate_size(size_str):
    parts = size_str.lower().split("x")
    if len(parts) != 2:
        return False, "Size must be in WxH format (e.g. 640x480)"
    try:
        w, h = int(parts[0]), int(parts[1])
    except ValueError:
        return False, "Width and height must be numbers"
    if w <= 0 or h <= 0:
        return False, "Width and height must be positive"
    if w > 3840 or h > 2160:
        return False, "Maximum size is 3840x2160"
    return True, (w, h)


def validate_start_vs_duration(start_sec, duration_sec, video_duration):
    if start_sec + duration_sec > video_duration:
        return False, "Start + duration exceeds video length"
    return True, "OK"
