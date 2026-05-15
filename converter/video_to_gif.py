"""Core video-to-GIF conversion logic."""

import os
import re
import subprocess
import threading

from utils import get_ffmpeg_path, get_ffprobe_path


def get_video_duration(video_path):
    cmd = [
        get_ffprobe_path(),
        "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        video_path,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
    if result.returncode != 0:
        raise RuntimeError(f"ffprobe failed: {result.stderr.strip()}")
    return float(result.stdout.strip())


def convert_to_gif(
    input_path,
    output_path,
    start_time,
    duration,
    fps,
    width,
    height,
    progress_callback=None,
    speed=1.0,
    max_colors=128,
    dither="bayer",
):
    if not output_path.endswith(".gif"):
        output_path += ".gif"

    start_str = f"{int(start_time // 3600):02d}:{int((start_time % 3600) // 60):02d}:{int(start_time % 60):02d}"

    vf_parts = []
    if speed != 1.0:
        vf_parts.append(f"setpts={1/speed:.4f}*PTS")
    vf_parts.append(
        f"scale={width}:{height}:force_original_aspect_ratio=decrease,"
        f"pad={width}:{height}:(ow-iw)/2:(oh-ih)/2:color=black,"
        f"fps={fps}"
    )
    vf = ",".join(vf_parts)

    cmd = [
        get_ffmpeg_path(),
        "-y",
        "-ss", start_str,
        "-i", input_path,
        "-t", str(duration),
        "-vf", f"{vf},split[s0][s1];[s0]palettegen=max_colors={max_colors}[p];[s1][p]paletteuse=dither={dither}",
        "-loop", "0",
        output_path,
    ]

    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    duration_pattern = re.compile(r"Duration:\s+(\d{2}):(\d{2}):(\d{2})\.(\d{2})")
    time_pattern = re.compile(r"time=(\d{2}):(\d{2}):(\d{2})\.(\d{2})")

    total_duration = None
    stderr_lines = []

    while True:
        line = process.stderr.readline()
        if not line:
            break
        stderr_lines.append(line)

        if total_duration is None:
            dm = duration_pattern.search(line)
            if dm:
                h, m, s, _ = int(dm.group(1)), int(dm.group(2)), int(dm.group(3)), int(dm.group(4))
                total_duration = h * 3600 + m * 60 + s + _ / 100

        tm = time_pattern.search(line)
        if tm and total_duration and total_duration > 0 and progress_callback:
            h, m, s, _ = int(tm.group(1)), int(tm.group(2)), int(tm.group(3)), int(tm.group(4))
            current = h * 3600 + m * 60 + s + _ / 100
            progress = min(current / total_duration * 100, 99)
            progress_callback(progress)

    process.wait()

    if process.returncode != 0:
        stderr_text = "\n".join(stderr_lines[-5:])
        raise RuntimeError(f"ffmpeg failed:\n{stderr_text}")

    if progress_callback:
        progress_callback(100)


def convert_async(
    input_path,
    output_path,
    start_time,
    duration,
    fps,
    width,
    height,
    progress_callback=None,
    done_callback=None,
    speed=1.0,
    max_colors=128,
    dither="bayer",
):
    def _run():
        try:
            convert_to_gif(
                input_path, output_path, start_time, duration,
                fps, width, height, progress_callback, speed,
                max_colors, dither,
            )
            if done_callback:
                done_callback(True, "Conversion complete!")
        except Exception as e:
            if done_callback:
                done_callback(False, str(e))

    thread = threading.Thread(target=_run, daemon=True)
    thread.start()
    return thread
