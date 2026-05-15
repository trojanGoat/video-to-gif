"""Video and GIF preview components."""

import os
import subprocess
import threading
from PIL import Image
import customtkinter as ctk

from ui.theme import THEME


class VideoPreview(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        colors = THEME["colors"]
        sizes = THEME["sizes"]
        spacing = THEME["spacing"]
        super().__init__(
            master,
            fg_color=colors["bg_card"],
            corner_radius=sizes["border_radius"],
            **kwargs,
        )

        self.video_path = None
        self.video_duration = 0
        self.frames = []
        self.current_frame = 0
        self.playing = False
        self.fps = 10
        self._after_id = None
        self._stop_event = threading.Event()

        self.inner = ctk.CTkFrame(self, fg_color="transparent")
        self.inner.pack(fill="both", expand=True, padx=spacing["inner_pad_x"], pady=spacing["inner_pad_y"])

        self.title_label = ctk.CTkLabel(
            self.inner,
            text="Video Preview",
            font=(THEME["fonts"]["label_bold"][0], THEME["fonts"]["label_bold"][1], "bold"),
            text_color=colors["text_primary"],
            anchor="w",
        )
        self.title_label.pack(fill="x", pady=(0, spacing["gap_sm"]))

        self.canvas_label = ctk.CTkLabel(
            self.inner,
            text="",
            font=(THEME["fonts"]["preview"][0], THEME["fonts"]["preview"][1]),
            text_color=colors["text_muted"],
        )
        self.canvas_label.pack(fill="both", expand=True, pady=(0, spacing["gap_sm"]))

        self.controls_frame = ctk.CTkFrame(self.inner, fg_color="transparent")
        self.controls_frame.pack(fill="x")

        self.play_btn = ctk.CTkButton(
            self.controls_frame,
            text="Play",
            width=60,
            height=30,
            font=(THEME["fonts"]["button"][0], 12),
            fg_color=colors["accent"],
            hover_color=colors["accent_hover"],
            text_color="#ffffff",
            corner_radius=6,
            command=self._toggle_play,
        )
        self.play_btn.pack(side="left")

        self.time_label = ctk.CTkLabel(
            self.controls_frame,
            text="00:00.0 / 00:00.0",
            font=(THEME["fonts"]["value"][0], 11),
            text_color=colors["text_muted"],
        )
        self.time_label.pack(side="left", padx=(spacing["gap_md"], 0))

        self.frame_slider = ctk.CTkSlider(
            self.controls_frame,
            from_=0,
            to=100,
            number_of_steps=100,
            height=12,
            fg_color=colors["progress_bg"],
            progress_color=colors["accent"],
            button_color=colors["accent"],
            button_hover_color=colors["accent_hover"],
        )
        self.frame_slider.set(0)
        self.frame_slider.pack(side="left", fill="x", expand=True, padx=(spacing["gap_md"], 0))
        self.frame_slider.configure(command=self._on_slider_change)

    def load_video(self, path, duration):
        self._stop_event.set()
        self._stop_event = threading.Event()
        self.video_path = path
        self.video_duration = duration
        self.frames = []
        self.current_frame = 0
        self._stop_play()

        try:
            if self.winfo_exists():
                self.title_label.configure(text=f"Video Preview: {os.path.basename(path)}")
                self._set_status("Extracting frames...")
        except Exception:
            pass

        thread = threading.Thread(target=self._extract_frames, daemon=True)
        thread.start()

    def _safe_after(self, callback, delay=0):
        try:
            if self.winfo_exists():
                self.after(delay, callback)
        except Exception:
            pass

    def _extract_frames(self):
        try:
            num_frames = 30
            interval = self.video_duration / num_frames if self.video_duration > 0 else 1

            self._safe_after(lambda: self.frame_slider.configure(to=num_frames - 1))

            for i in range(num_frames):
                if self._stop_event.is_set():
                    return
                timestamp = i * interval
                frame = self._extract_frame(timestamp)
                if frame:
                    self.frames.append(frame)

            if self.frames:
                self._safe_after(lambda: self._show_frame(0))
                self._safe_after(lambda: self._set_status(f"{len(self.frames)} frames loaded"))
            else:
                self._safe_after(lambda: self._set_status("No frames extracted"))
        except Exception as e:
            self._safe_after(lambda: self._set_status(f"Error: {e}"))

    def _extract_frame(self, timestamp):
        cmd = [
            "ffmpeg",
            "-ss", str(timestamp),
            "-i", self.video_path,
            "-vframes", "1",
            "-f", "image2pipe",
            "-vcodec", "png",
            "-",
        ]
        try:
            result = subprocess.run(cmd, capture_output=True, timeout=10)
            if result.returncode == 0 and result.stdout:
                img = Image.open(__import__("io").BytesIO(result.stdout))
                img.thumbnail((480, 270))
                return img
        except Exception:
            pass
        return None

    def _show_frame(self, index):
        try:
            if not self.winfo_exists():
                return
            if 0 <= index < len(self.frames):
                self.current_frame = index
                frame = self.frames[index]
                ctk_img = ctk.CTkImage(light_image=frame, dark_image=frame, size=frame.size)
                self.canvas_label.configure(image=ctk_img, text="")
                self.frame_slider.set(index)
                time_str = self._format_time(index * (self.video_duration / len(self.frames)) if self.frames else 0)
                total_str = self._format_time(self.video_duration)
                self.time_label.configure(text=f"{time_str} / {total_str}")
        except Exception:
            pass

    def _toggle_play(self):
        if self.playing:
            self._stop_play()
        else:
            self._start_play()

    def _start_play(self):
        if not self.frames or not self.winfo_exists():
            return
        self.playing = True
        self.play_btn.configure(text="Pause")
        self._play_next()

    def _stop_play(self):
        self.playing = False
        if self.winfo_exists():
            self.play_btn.configure(text="Play")
        if self._after_id:
            self.after_cancel(self._after_id)
            self._after_id = None

    def _play_next(self):
        if not self.playing or not self.frames or not self.winfo_exists():
            return
        self._show_frame(self.current_frame)
        next_frame = (self.current_frame + 1) % len(self.frames)
        self.current_frame = next_frame
        interval = (self.video_duration / len(self.frames)) * 1000 / self.fps if self.fps > 0 else 100
        try:
            if self.winfo_exists():
                self._after_id = self.after(int(interval), self._play_next)
        except Exception:
            pass

    def _on_slider_change(self, value):
        if self.frames:
            self._show_frame(int(value))

    def _format_time(self, seconds):
        mins = int(seconds // 60)
        secs = seconds % 60
        return f"{mins:02d}:{secs:04.1f}"

    def _set_status(self, text):
        try:
            if self.winfo_exists():
                self.time_label.configure(text=text)
        except Exception:
            pass

    def get_current_time(self):
        if self.frames and self.video_duration > 0:
            return self.current_frame * (self.video_duration / len(self.frames))
        return 0


class GifPreview(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        colors = THEME["colors"]
        sizes = THEME["sizes"]
        spacing = THEME["spacing"]
        super().__init__(
            master,
            fg_color=colors["bg_card"],
            corner_radius=sizes["border_radius"],
            **kwargs,
        )

        self.gif_path = None
        self.frames = []
        self.durations = []
        self.current_frame = 0
        self.playing = False
        self._after_id = None

        self.inner = ctk.CTkFrame(self, fg_color="transparent")
        self.inner.pack(fill="both", expand=True, padx=spacing["inner_pad_x"], pady=spacing["inner_pad_y"])

        self.title_label = ctk.CTkLabel(
            self.inner,
            text="GIF Preview",
            font=(THEME["fonts"]["label_bold"][0], THEME["fonts"]["label_bold"][1], "bold"),
            text_color=colors["text_primary"],
            anchor="w",
        )
        self.title_label.pack(fill="x", pady=(0, spacing["gap_sm"]))

        self.canvas_label = ctk.CTkLabel(
            self.inner,
            text="Converted GIF will appear here",
            font=(THEME["fonts"]["preview"][0], THEME["fonts"]["preview"][1]),
            text_color=colors["text_muted"],
        )
        self.canvas_label.pack(fill="both", expand=True, pady=(0, spacing["gap_sm"]))

        self.controls_frame = ctk.CTkFrame(self.inner, fg_color="transparent")
        self.controls_frame.pack(fill="x")

        self.play_btn = ctk.CTkButton(
            self.controls_frame,
            text="Play",
            width=60,
            height=30,
            font=(THEME["fonts"]["button"][0], 12),
            fg_color=colors["accent"],
            hover_color=colors["accent_hover"],
            text_color="#ffffff",
            corner_radius=6,
            command=self._toggle_play,
            state="disabled",
        )
        self.play_btn.pack(side="left")

        self.status_label = ctk.CTkLabel(
            self.controls_frame,
            text="No GIF yet",
            font=(THEME["fonts"]["value"][0], 11),
            text_color=colors["text_muted"],
        )
        self.status_label.pack(side="left", padx=(spacing["gap_md"], 0))

    def load_gif(self, path):
        self.gif_path = path
        self.frames = []
        self.durations = []
        self.current_frame = 0
        self._stop_play()

        try:
            gif = Image.open(path)
            if not self.winfo_exists():
                return
            self.title_label.configure(text=f"GIF Preview: {os.path.basename(path)}")

            frame_num = 0
            while True:
                try:
                    gif.seek(frame_num)
                    img = gif.copy()
                    img.thumbnail((480, 270))
                    self.frames.append(img)
                    duration = gif.info.get("duration", 100)
                    self.durations.append(duration)
                    frame_num += 1
                except EOFError:
                    break

            if not self.winfo_exists():
                return
            if self.frames:
                self._show_frame(0)
                try:
                    self.play_btn.configure(state="normal")
                    self.status_label.configure(text=f"{len(self.frames)} frames")
                except Exception:
                    pass
                self._start_play()
        except Exception as e:
            try:
                if self.winfo_exists():
                    self.status_label.configure(text=f"Error loading GIF: {e}")
            except Exception:
                pass

    def _show_frame(self, index):
        try:
            if not self.winfo_exists():
                return
            if 0 <= index < len(self.frames):
                self.current_frame = index
                frame = self.frames[index]
                ctk_img = ctk.CTkImage(light_image=frame, dark_image=frame, size=frame.size)
                self.canvas_label.configure(image=ctk_img, text="")
        except Exception:
            pass

    def _toggle_play(self):
        if self.playing:
            self._stop_play()
        else:
            self._start_play()

    def _start_play(self):
        if not self.frames or not self.winfo_exists():
            return
        self.playing = True
        self.play_btn.configure(text="Pause")
        self._play_next()

    def _stop_play(self):
        self.playing = False
        if self.winfo_exists():
            self.play_btn.configure(text="Play")
        if self._after_id:
            self.after_cancel(self._after_id)
            self._after_id = None

    def _play_next(self):
        if not self.playing or not self.frames or not self.winfo_exists():
            return
        self._show_frame(self.current_frame)
        duration = self.durations[self.current_frame] if self.current_frame < len(self.durations) else 100
        next_frame = (self.current_frame + 1) % len(self.frames)
        self.current_frame = next_frame
        try:
            if self.winfo_exists():
                self._after_id = self.after(duration, self._play_next)
        except Exception:
            pass
