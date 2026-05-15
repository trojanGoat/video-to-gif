"""Main application window for the Video to GIF Converter."""

import os
from tkinter import filedialog, messagebox
import customtkinter as ctk
from tkinterdnd2 import TkinterDnD, DND_FILES

from ui.theme import THEME
from ui.components import DropZone, FPSSlider, SizeSelector, RangeSlider, SpeedSlider, CompressionSelector
from ui.preview import VideoPreview, GifPreview
from converter import validator
from converter.video_to_gif import get_video_duration, convert_async


class App(TkinterDnD.Tk):
    def __init__(self):
        super().__init__()

        colors = THEME["colors"]
        sizes = THEME["sizes"]
        spacing = THEME["spacing"]

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")

        self.title("Video to GIF Converter")
        self.geometry(f"{sizes['window_width']}x{sizes['window_height']}")
        self.minsize(sizes["window_min_width"], sizes["window_min_height"])

        self.configure(background=colors["bg_primary"])

        self.drop_target_register(DND_FILES)
        self.dnd_bind("<<Drop>>", self._on_window_drop)

        self.video_path = None
        self.video_duration = 0
        self.converting = False
        self.worker_thread = None

        self._build_ui()

        if not validator.check_ffmpeg():
            messagebox.showerror(
                "ffmpeg not found",
                "ffmpeg is required but was not found in your PATH.\n\n"
                "Install it and try again:\n"
                "  macOS: brew install ffmpeg\n"
                "  Ubuntu: sudo apt install ffmpeg\n"
                "  Windows: https://ffmpeg.org/download.html",
            )

    def _build_ui(self):
        spacing = THEME["spacing"]
        colors = THEME["colors"]
        sizes = THEME["sizes"]

        main_frame = ctk.CTkScrollableFrame(
            self,
            fg_color=colors["bg_primary"],
            scrollbar_fg_color=colors["bg_primary"],
            scrollbar_button_color=colors["bg_tertiary"],
            scrollbar_button_hover_color=colors["accent"],
        )
        main_frame.pack(fill="both", expand=True, padx=spacing["pad_x"], pady=spacing["pad_y"])

        title = ctk.CTkLabel(
            main_frame,
            text="Video to GIF",
            font=(THEME["fonts"]["title"][0], THEME["fonts"]["title"][1], "bold"),
            text_color=colors["text_primary"],
        )
        title.pack(pady=(0, spacing["gap_lg"]))

        self.dropzone = DropZone(main_frame, on_file_selected=self._on_video_selected)
        self.dropzone.pack(fill="x", pady=(0, spacing["gap_lg"]))

        self.video_preview = VideoPreview(main_frame)
        self.video_preview.pack(fill="both", expand=True, pady=(0, spacing["gap_lg"]))

        output_frame = ctk.CTkFrame(
            main_frame,
            fg_color=colors["bg_card"],
            corner_radius=sizes["border_radius"],
        )
        output_frame.pack(fill="x", pady=(0, spacing["gap_lg"]))
        output_frame_inner = ctk.CTkFrame(output_frame, fg_color="transparent")
        output_frame_inner.pack(fill="x", padx=spacing["inner_pad_x"], pady=spacing["inner_pad_y"])

        output_label = ctk.CTkLabel(
            output_frame_inner,
            text="Output",
            font=(THEME["fonts"]["label_bold"][0], THEME["fonts"]["label_bold"][1], "bold"),
            text_color=colors["text_primary"],
            anchor="w",
        )
        output_label.pack(side="left", padx=(0, spacing["gap_sm"]))

        self.output_var = ctk.StringVar()
        self.output_entry = ctk.CTkEntry(
            output_frame_inner,
            textvariable=self.output_var,
            height=sizes["input_height"],
            font=(THEME["fonts"]["value"][0], THEME["fonts"]["value"][1]),
            fg_color=colors["bg_input"],
            border_color=colors["border"],
            corner_radius=6,
            text_color=colors["text_primary"],
            placeholder_text="output.gif",
        )
        self.output_entry.pack(side="left", fill="x", expand=True, padx=(0, spacing["gap_sm"]))

        self.output_browse_btn = ctk.CTkButton(
            output_frame_inner,
            text="Browse",
            command=self._browse_output,
            height=sizes["input_height"],
            width=70,
            font=(THEME["fonts"]["button"][0], THEME["fonts"]["button"][1] - 1),
            fg_color=colors["bg_tertiary"],
            hover_color=colors["bg_hover"],
            text_color=colors["text_primary"],
            corner_radius=6,
        )
        self.output_browse_btn.pack(side="left")

        settings_frame = ctk.CTkFrame(
            main_frame,
            fg_color=colors["bg_card"],
            corner_radius=sizes["border_radius"],
        )
        settings_frame.pack(fill="x", pady=(0, spacing["gap_lg"]))
        settings_inner = ctk.CTkFrame(settings_frame, fg_color="transparent")
        settings_inner.pack(fill="x", padx=spacing["inner_pad_x"], pady=spacing["inner_pad_y"])

        settings_title = ctk.CTkLabel(
            settings_inner,
            text="Settings",
            font=(THEME["fonts"]["label_bold"][0], THEME["fonts"]["label_bold"][1], "bold"),
            text_color=colors["text_primary"],
            anchor="w",
        )
        settings_title.pack(fill="x", pady=(0, spacing["gap_md"]))

        self.range_slider = RangeSlider(settings_inner)
        self.range_slider.pack(fill="x", pady=(0, spacing["gap_md"]))

        self.fps_slider = FPSSlider(settings_inner)
        self.fps_slider.pack(fill="x", pady=(0, spacing["gap_md"]))

        self.speed_slider = SpeedSlider(settings_inner)
        self.speed_slider.pack(fill="x", pady=(0, spacing["gap_md"]))

        self.size_selector = SizeSelector(settings_inner)
        self.size_selector.pack(fill="x", pady=(0, spacing["gap_md"]))

        self.compression_selector = CompressionSelector(settings_inner)
        self.compression_selector.pack(fill="x", pady=(0, spacing["gap_sm"]))

        self.size_selector.bind("<<ComboboxSelected>>", lambda e: self._update_preview())

        progress_frame = ctk.CTkFrame(
            main_frame,
            fg_color=colors["bg_card"],
            corner_radius=sizes["border_radius"],
        )
        progress_frame.pack(fill="x", pady=(0, spacing["gap_lg"]))
        progress_inner = ctk.CTkFrame(progress_frame, fg_color="transparent")
        progress_inner.pack(fill="x", padx=spacing["inner_pad_x"], pady=spacing["inner_pad_y"])

        self.progress_bar = ctk.CTkProgressBar(
            progress_inner,
            width=480,
            height=14,
            fg_color=colors["progress_bg"],
            progress_color=colors["progress_fill"],
            corner_radius=6,
        )
        self.progress_bar.set(0)
        self.progress_bar.pack(fill="x", pady=(0, spacing["gap_sm"]))

        self.status_label = ctk.CTkLabel(
            progress_inner,
            text="Ready",
            font=(THEME["fonts"]["status"][0], THEME["fonts"]["status"][1]),
            text_color=colors["text_muted"],
            anchor="w",
        )
        self.status_label.pack(fill="x")

        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.pack(fill="x", pady=(0, spacing["gap_lg"]))

        self.convert_btn = ctk.CTkButton(
            button_frame,
            text="Convert to GIF",
            command=self._start_conversion,
            height=sizes["button_height"],
            font=(THEME["fonts"]["button"][0], THEME["fonts"]["button"][1]),
            fg_color=colors["accent"],
            hover_color=colors["accent_hover"],
            text_color="#ffffff",
            corner_radius=8,
        )
        self.convert_btn.pack(fill="x")

        self.gif_preview = GifPreview(main_frame)
        self.gif_preview.pack(fill="both", expand=True, pady=(0, spacing["gap_lg"]))

    def _on_video_selected(self, path):
        self.video_path = path
        def _load():
            try:
                if not self.winfo_exists():
                    return
                self.video_duration = get_video_duration(path)
                self.range_slider.set_duration(self.video_duration)
                self.video_preview.load_video(path, self.video_duration)
                self._update_preview()
                self._set_status(f"Video loaded: {self.video_duration:.1f}s", THEME["colors"]["success"])
            except Exception as e:
                if self.winfo_exists():
                    self._set_status(f"Error reading video: {e}", THEME["colors"]["error"])
        self.after(0, _load)

    def _on_window_drop(self, event):
        self.dropzone.handle_drop(event)

    def _browse_output(self):
        initial_dir = os.path.dirname(self.video_path) if self.video_path else os.path.expanduser("~")
        path = filedialog.asksaveasfilename(
            initialdir=initial_dir,
            defaultextension=".gif",
            filetypes=[("GIF files", "*.gif"), ("All files", "*.*")],
        )
        if path:
            self.output_var.set(path)

    def _update_preview(self):
        if not self.video_path:
            return

        filename = os.path.basename(self.video_path)
        w, h = self.size_selector.get_size()
        if w is None:
            w, h = 640, 480

        fps = self.fps_slider.get()
        start, end = self.range_slider.get_range()
        speed = self.speed_slider.get_speed()
        duration = end - start
        max_colors, dither, quality = self.compression_selector.get_settings()

        info = (
            f"Input: {filename}\n"
            f"Duration: {self.video_duration:.1f}s\n"
            f"Output: {w}x{h} @ {fps} fps\n"
            f"Range: {start:.1f}s - {end:.1f}s ({duration:.1f}s)  Speed: {speed}x\n"
            f"Compression: {max_colors} colors, {dither} dither ({quality})"
        )
        self.video_preview._set_status(info)

    def _set_status(self, message, color=None):
        if color is None:
            color = THEME["colors"]["text_muted"]
        self.status_label.configure(text=message, text_color=color)

    def _start_conversion(self):
        if self.converting:
            self._cancel_conversion()
            return

        errors = self._validate()
        if errors:
            messagebox.showerror("Validation Error", "\n".join(errors))
            return

        self.converting = True
        self.convert_btn.configure(
            text="Cancel",
            fg_color=THEME["colors"]["error"],
            hover_color=THEME["colors"]["accent_hover"],
        )
        self.progress_bar.set(0)
        self._set_status("Starting conversion...", THEME["colors"]["warning"])

        output = self.output_var.get().strip() or "output.gif"
        if not output.endswith(".gif"):
            output += ".gif"

        start, end = self.range_slider.get_range()
        start_sec = start
        dur_val = end - start
        fps_valid, fps_val = validator.validate_fps(self.fps_slider.get())
        w, h = self.size_selector.get_size()
        speed = self.speed_slider.get_speed()
        max_colors, dither, _ = self.compression_selector.get_settings()

        self.worker_thread = convert_async(
            input_path=self.video_path,
            output_path=output,
            start_time=start_sec,
            duration=dur_val,
            fps=fps_val,
            width=w,
            height=h,
            progress_callback=self._on_progress,
            done_callback=self._on_done,
            speed=speed,
            max_colors=max_colors,
            dither=dither,
        )

    def _cancel_conversion(self):
        self.converting = False
        self.convert_btn.configure(
            text="Convert to GIF",
            fg_color=THEME["colors"]["accent"],
            hover_color=THEME["colors"]["accent_hover"],
        )
        self._set_status("Cancelled", THEME["colors"]["error"])

    def _on_progress(self, value):
        self.after(0, lambda: self.progress_bar.set(value / 100))
        self.after(0, lambda: self._set_status(f"Converting... {value:.0f}%", THEME["colors"]["warning"]))

    def _on_done(self, success, message):
        def _update():
            self.converting = False
            self.convert_btn.configure(
                text="Convert to GIF",
                fg_color=THEME["colors"]["accent"],
                hover_color=THEME["colors"]["accent_hover"],
            )
            if success:
                self.progress_bar.set(1.0)
                self._set_status(message, THEME["colors"]["success"])
                output = self.output_var.get().strip() or "output.gif"
                if not output.endswith(".gif"):
                    output += ".gif"
                if os.path.exists(output):
                    self.gif_preview.load_gif(output)
            else:
                self._set_status(f"Error: {message}", THEME["colors"]["error"])
        self.after(0, _update)

    def _validate(self):
        errors = []

        if not self.video_path:
            errors.append("No video file selected")
        else:
            ok, msg = validator.validate_video_file(self.video_path)
            if not ok:
                errors.append(msg)

        output = self.output_var.get().strip()
        ok, msg = validator.validate_output_path(output)
        if not ok:
            errors.append(msg)

        ok, msg = validator.validate_fps(self.fps_slider.get())
        if not ok:
            errors.append(f"FPS: {msg}")

        w, h = self.size_selector.get_size()
        if w is None or h is None:
            errors.append("Invalid custom size")

        if not errors and self.video_duration > 0:
            start, end = self.range_slider.get_range()
            dur_val = end - start
            ok, msg = validator.validate_start_vs_duration(start, dur_val, self.video_duration)
            if not ok:
                errors.append(msg)

        return errors
