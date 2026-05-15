"""Reusable UI components for the Video to GIF Converter."""

import os
from tkinter import filedialog
import customtkinter as ctk

from ui.theme import THEME, PRESET_SIZES


class DropZone(ctk.CTkFrame):
    def __init__(self, master, on_file_selected=None, **kwargs):
        colors = THEME["colors"]
        sizes = THEME["sizes"]
        super().__init__(
            master,
            fg_color=colors["dropzone_bg"],
            corner_radius=sizes["border_radius"],
            border_width=2,
            border_color=colors["dropzone_border"],
            height=sizes["dropzone_height"],
            **kwargs,
        )

        self.on_file_selected = on_file_selected
        self.selected_file = None
        self._drag_active = False

        self.label_icon = ctk.CTkLabel(
            self,
            text="",
            font=(THEME["fonts"]["title"][0], 32),
            text_color=colors["text_muted"],
        )
        self.label_icon.place(relx=0.5, rely=0.25, anchor="center")

        self.label_main = ctk.CTkLabel(
            self,
            text="Drag & drop video here",
            font=(THEME["fonts"]["subtitle"][0], 14, "bold"),
            text_color=colors["text_secondary"],
        )
        self.label_main.place(relx=0.5, rely=0.5, anchor="center")

        self.label_sub = ctk.CTkLabel(
            self,
            text="or click to browse",
            font=(THEME["fonts"]["label"][0], 12),
            text_color=colors["text_muted"],
        )
        self.label_sub.place(relx=0.5, rely=0.72, anchor="center")

        self.file_label = ctk.CTkLabel(
            self,
            text="",
            font=(THEME["fonts"]["value"][0], 11),
            text_color=colors["success"],
        )

        self.bind_events()

    def bind_events(self):
        for widget in [self, self.label_icon, self.label_main, self.label_sub, self.file_label]:
            widget.bind("<Enter>", self._on_enter)
            widget.bind("<Leave>", self._on_leave)
            widget.bind("<Button-1>", self._on_click)
            widget.bind("<ButtonRelease-1>", self._on_click)

    def handle_drop(self, event=None):
        if event is None:
            return
        data = getattr(event, "data", "")
        if not data:
            return
        files = self.tk.splitlist(data)
        if files:
            self._set_file(files[0])

    def _on_enter(self, event=None):
        colors = THEME["colors"]
        self.configure(border_color=colors["accent"])

    def _on_leave(self, event=None):
        colors = THEME["colors"]
        if not self._drag_active:
            self.configure(border_color=colors["dropzone_border"])

    def _on_click(self, event=None):
        self._browse_file()

    def _browse_file(self):
        filetypes = [
            ("Video files", "*.mp4 *.mov *.avi *.mkv *.webm *.flv *.wmv *.m4v *.mpeg *.mpg"),
            ("All files", "*.*"),
        ]
        path = filedialog.askopenfilename(filetypes=filetypes)
        if path:
            self._set_file(path)

    def _set_file(self, path):
        self.selected_file = path
        filename = os.path.basename(path)
        try:
            self.label_main.configure(text=filename)
            self.label_sub.configure(text=os.path.dirname(path))
            self.label_icon.configure(text="")
            self.file_label.configure(text=f"Selected: {filename}")
            self.file_label.place(relx=0.5, rely=0.92, anchor="center")
        except Exception:
            pass
        if self.on_file_selected:
            try:
                self.on_file_selected(path)
            except Exception:
                pass

    def clear(self):
        self.selected_file = None
        colors = THEME["colors"]
        self.configure(border_color=colors["dropzone_border"])
        self.label_main.configure(text="Drag & drop video here")
        self.label_sub.configure(text="or click to browse")
        self.label_icon.configure(text="")
        self.file_label.place_forget()


class TimeEntry(ctk.CTkFrame):
    def __init__(self, master, label_text="Time", default="00:00:00", **kwargs):
        colors = THEME["colors"]
        spacing = THEME["spacing"]
        sizes = THEME["sizes"]
        super().__init__(master, fg_color="transparent", **kwargs)

        self.label = ctk.CTkLabel(
            self,
            text=label_text,
            font=(THEME["fonts"]["label_bold"][0], THEME["fonts"]["label_bold"][1], "bold"),
            text_color=colors["text_primary"],
            anchor="w",
        )
        self.label.pack(side="left", padx=(0, spacing["gap_sm"]))

        self.entry = ctk.CTkEntry(
            self,
            width=100,
            height=sizes["input_height"],
            font=(THEME["fonts"]["value"][0], THEME["fonts"]["value"][1]),
            fg_color=colors["bg_input"],
            border_color=colors["border"],
            corner_radius=6,
            text_color=colors["text_primary"],
        )
        self.entry.insert(0, default)
        self.entry.pack(side="left")

    def get(self):
        return self.entry.get()

    def set(self, value):
        self.entry.delete(0, "end")
        self.entry.insert(0, value)


class DurationEntry(ctk.CTkFrame):
    def __init__(self, master, default="5", **kwargs):
        colors = THEME["colors"]
        sizes = THEME["sizes"]
        spacing = THEME["spacing"]
        super().__init__(master, fg_color="transparent", **kwargs)

        self.label = ctk.CTkLabel(
            self,
            text="Duration (sec)",
            font=(THEME["fonts"]["label_bold"][0], THEME["fonts"]["label_bold"][1], "bold"),
            text_color=colors["text_primary"],
            anchor="w",
        )
        self.label.pack(side="left", padx=(0, spacing["gap_sm"]))

        self.entry = ctk.CTkEntry(
            self,
            width=80,
            height=sizes["input_height"],
            font=(THEME["fonts"]["value"][0], THEME["fonts"]["value"][1]),
            fg_color=colors["bg_input"],
            border_color=colors["border"],
            corner_radius=6,
            text_color=colors["text_primary"],
        )
        self.entry.insert(0, default)
        self.entry.pack(side="left")

        self.unit = ctk.CTkLabel(
            self,
            text="seconds",
            font=(THEME["fonts"]["label"][0], THEME["fonts"]["label"][1]),
            text_color=colors["text_muted"],
        )
        self.unit.pack(side="left", padx=(spacing["gap_sm"], 0))

    def get(self):
        return self.entry.get()

    def set(self, value):
        self.entry.delete(0, "end")
        self.entry.insert(0, str(value))


class FPSSlider(ctk.CTkFrame):
    def __init__(self, master, default=10, **kwargs):
        colors = THEME["colors"]
        sizes = THEME["sizes"]
        spacing = THEME["spacing"]
        super().__init__(master, fg_color="transparent", **kwargs)

        self.label = ctk.CTkLabel(
            self,
            text="Frame Rate",
            font=(THEME["fonts"]["label_bold"][0], THEME["fonts"]["label_bold"][1], "bold"),
            text_color=colors["text_primary"],
            anchor="w",
        )
        self.label.pack(side="left", padx=(0, spacing["gap_md"]))

        self.slider = ctk.CTkSlider(
            self,
            from_=1,
            to=30,
            number_of_steps=29,
            width=200,
            height=16,
            fg_color=colors["progress_bg"],
            progress_color=colors["accent"],
            button_color=colors["accent"],
            button_hover_color=colors["accent_hover"],
        )
        self.slider.set(default)
        self.slider.pack(side="left", fill="x", expand=True, padx=(0, spacing["gap_sm"]))

        self.value_label = ctk.CTkLabel(
            self,
            text=f"{default} fps",
            font=(THEME["fonts"]["value"][0], THEME["fonts"]["value"][1], "bold"),
            text_color=colors["accent"],
            width=50,
        )
        self.value_label.pack(side="left")

        self.slider.configure(command=self._on_change)

    def _on_change(self, value):
        self.value_label.configure(text=f"{int(value)} fps")

    def get(self):
        return int(self.slider.get())


class SizeSelector(ctk.CTkFrame):
    def __init__(self, master, default_preset=0, **kwargs):
        colors = THEME["colors"]
        sizes = THEME["sizes"]
        spacing = THEME["spacing"]
        super().__init__(master, fg_color="transparent", **kwargs)

        self.label = ctk.CTkLabel(
            self,
            text="Output Size",
            font=(THEME["fonts"]["label_bold"][0], THEME["fonts"]["label_bold"][1], "bold"),
            text_color=colors["text_primary"],
            anchor="w",
        )
        self.label.pack(side="left", padx=(0, spacing["gap_md"]))

        preset_labels = [s[0] for s in PRESET_SIZES]
        self.preset_var = ctk.StringVar(value=preset_labels[default_preset])
        self.preset_dropdown = ctk.CTkOptionMenu(
            self,
            variable=self.preset_var,
            values=preset_labels,
            width=120,
            height=sizes["input_height"],
            font=(THEME["fonts"]["value"][0], THEME["fonts"]["value"][1]),
            fg_color=colors["bg_input"],
            button_color=colors["bg_tertiary"],
            button_hover_color=colors["bg_hover"],
            dropdown_fg_color=colors["bg_input"],
            dropdown_hover_color=colors["bg_hover"],
            text_color=colors["text_primary"],
            dropdown_text_color=colors["text_primary"],
            corner_radius=6,
            command=self._on_preset_change,
        )
        self.preset_dropdown.pack(side="left", padx=(0, spacing["gap_md"]))

        self.custom_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.custom_frame.pack(side="left")

        self.width_entry = ctk.CTkEntry(
            self.custom_frame,
            width=60,
            height=sizes["input_height"],
            font=(THEME["fonts"]["value"][0], THEME["fonts"]["value"][1]),
            fg_color=colors["bg_input"],
            border_color=colors["border"],
            corner_radius=6,
            text_color=colors["text_primary"],
            placeholder_text="W",
        )
        self.width_entry.pack(side="left", padx=(0, 4))

        self.x_label = ctk.CTkLabel(
            self.custom_frame,
            text="x",
            font=(THEME["fonts"]["value"][0], THEME["fonts"]["value"][1]),
            text_color=colors["text_muted"],
        )
        self.x_label.pack(side="left", padx=(0, 4))

        self.height_entry = ctk.CTkEntry(
            self.custom_frame,
            width=60,
            height=sizes["input_height"],
            font=(THEME["fonts"]["value"][0], THEME["fonts"]["value"][1]),
            fg_color=colors["bg_input"],
            border_color=colors["border"],
            corner_radius=6,
            text_color=colors["text_primary"],
            placeholder_text="H",
        )
        self.height_entry.pack(side="left")

        self.custom_mode = ctk.BooleanVar(value=False)
        self.custom_toggle = ctk.CTkCheckBox(
            self,
            text="Custom",
            variable=self.custom_mode,
            command=self._toggle_custom,
            font=(THEME["fonts"]["label"][0], THEME["fonts"]["label"][1]),
            text_color=colors["text_secondary"],
            fg_color=colors["accent"],
            hover_color=colors["accent_hover"],
            checkbox_height=16,
            checkbox_width=16,
        )
        self.custom_toggle.pack(side="left", padx=(spacing["gap_md"], 0))

        self._toggle_custom()

    def _on_preset_change(self, value):
        pass

    def _toggle_custom(self):
        if self.custom_mode.get():
            self.preset_dropdown.configure(state="disabled")
            self.width_entry.configure(state="normal")
            self.height_entry.configure(state="normal")
        else:
            self.preset_dropdown.configure(state="normal")
            self.width_entry.configure(state="disabled")
            self.height_entry.configure(state="disabled")

    def get_size(self):
        if self.custom_mode.get():
            w_str = self.width_entry.get().strip()
            h_str = self.height_entry.get().strip()
            if w_str and h_str:
                try:
                    return int(w_str), int(h_str)
                except ValueError:
                    return None, None
            return None, None
        preset_label = self.preset_var.get()
        for label, w, h in PRESET_SIZES:
            if label == preset_label:
                return w, h
        return 640, 480


class RangeSlider(ctk.CTkFrame):
    def __init__(self, master, duration=10, **kwargs):
        colors = THEME["colors"]
        sizes = THEME["sizes"]
        spacing = THEME["spacing"]
        super().__init__(master, fg_color="transparent", **kwargs)

        self.duration = duration
        self.start_time = 0
        self.end_time = min(5, duration)

        self.label = ctk.CTkLabel(
            self,
            text="Clip Range",
            font=(THEME["fonts"]["label_bold"][0], THEME["fonts"]["label_bold"][1], "bold"),
            text_color=colors["text_primary"],
            anchor="w",
        )
        self.label.pack(fill="x", pady=(0, spacing["gap_sm"]))

        self.time_labels = ctk.CTkFrame(self, fg_color="transparent")
        self.time_labels.pack(fill="x", pady=(0, spacing["gap_sm"]))

        self.start_label = ctk.CTkLabel(
            self.time_labels,
            text="00:00.0",
            font=(THEME["fonts"]["value"][0], THEME["fonts"]["value"][1]),
            text_color=colors["accent"],
            anchor="w",
        )
        self.start_label.pack(side="left")

        self.end_label = ctk.CTkLabel(
            self.time_labels,
            text="00:05.0",
            font=(THEME["fonts"]["value"][0], THEME["fonts"]["value"][1]),
            text_color=colors["accent"],
            anchor="e",
        )
        self.end_label.pack(side="right")

        self.canvas = ctk.CTkCanvas(
            self,
            height=32,
            bg=colors["bg_input"],
            highlightthickness=0,
            borderwidth=0,
        )
        self.canvas.pack(fill="x", pady=(0, spacing["gap_sm"]))

        self.track_height = 8
        self.handle_radius = 10
        self.padding = self.handle_radius

        self.dragging = None

        self.canvas.bind("<Button-1>", self._on_click)
        self.canvas.bind("<B1-Motion>", self._on_drag)
        self.canvas.bind("<Configure>", self._on_resize)

        self._render_slider()

    def set_duration(self, duration):
        self.duration = duration
        self.start_time = 0
        self.end_time = min(5, duration)
        self._update_labels()
        self._render_slider()

    def get_range(self):
        return self.start_time, self.end_time

    def _on_resize(self, event):
        self._render_slider()

    def _get_handle_x(self, time_val):
        width = self.canvas.winfo_width() - 2 * self.padding
        return self.padding + (time_val / self.duration) * width if self.duration > 0 else self.padding

    def _get_time_from_x(self, x):
        width = self.canvas.winfo_width() - 2 * self.padding
        ratio = max(0, min(1, (x - self.padding) / width))
        return ratio * self.duration

    def _on_click(self, event):
        start_x = self._get_handle_x(self.start_time)
        end_x = self._get_handle_x(self.end_time)

        if abs(event.x - start_x) < self.handle_radius + 4:
            self.dragging = "start"
        elif abs(event.x - end_x) < self.handle_radius + 4:
            self.dragging = "end"
        elif event.x < start_x:
            self.dragging = "start"
            self.start_time = max(0, min(self.end_time - 0.1, self._get_time_from_x(event.x)))
            self._update_labels()
            self._render_slider()
        elif event.x > end_x:
            self.dragging = "end"
            self.end_time = max(self.start_time + 0.1, min(self.duration, self._get_time_from_x(event.x)))
            self._update_labels()
            self._render_slider()
        else:
            mid = (self.start_time + self.end_time) / 2
            offset = self._get_time_from_x(event.x) - mid
            range_size = self.end_time - self.start_time
            new_start = max(0, min(self.duration - range_size, self.start_time + offset))
            self.start_time = new_start
            self.end_time = new_start + range_size
            self.dragging = "both"
            self._update_labels()
            self._render_slider()

    def _on_drag(self, event):
        if self.dragging is None:
            return
        time_val = self._get_time_from_x(event.x)
        range_size = self.end_time - self.start_time

        if self.dragging == "start":
            self.start_time = max(0, min(self.end_time - 0.1, time_val))
        elif self.dragging == "end":
            self.end_time = max(self.start_time + 0.1, min(self.duration, time_val))
        elif self.dragging == "both":
            new_start = max(0, min(self.duration - range_size, time_val - range_size / 2))
            self.start_time = new_start
            self.end_time = new_start + range_size

        self._update_labels()
        self._render_slider()

    def _update_labels(self):
        self.start_label.configure(text=self._format_time(self.start_time))
        self.end_label.configure(text=self._format_time(self.end_time))

    def _format_time(self, seconds):
        mins = int(seconds // 60)
        secs = seconds % 60
        return f"{mins:02d}:{secs:04.1f}"

    def _render_slider(self):
        self.canvas.delete("all")
        colors = THEME["colors"]
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        if width < 20 or height < 10:
            return

        track_y = height // 2
        track_left = self.padding
        track_right = width - self.padding

        self.canvas.create_rectangle(
            track_left, track_y - self.track_height // 2,
            track_right, track_y + self.track_height // 2,
            fill=colors["bg_tertiary"], outline="",
        )

        start_x = self._get_handle_x(self.start_time)
        end_x = self._get_handle_x(self.end_time)

        self.canvas.create_rectangle(
            start_x, track_y - self.track_height // 2,
            end_x, track_y + self.track_height // 2,
            fill=colors["accent"], outline="",
        )

        for x, fill_color in [(start_x, "#ffffff"), (end_x, "#ffffff")]:
            self.canvas.create_oval(
                x - self.handle_radius, track_y - self.handle_radius,
                x + self.handle_radius, track_y + self.handle_radius,
                fill=fill_color, outline=colors["accent"], width=2,
            )


COMPRESSION_PRESETS = [
    ("Best Quality", 256, "bayer", "high"),
    ("Balanced", 128, "bayer", "medium"),
    ("Small Size", 64, "floyd_steinberg", "low"),
    ("Tiny", 32, "sierra2", "lowest"),
]


class CompressionSelector(ctk.CTkFrame):
    def __init__(self, master, default=1, **kwargs):
        colors = THEME["colors"]
        sizes = THEME["sizes"]
        spacing = THEME["spacing"]
        super().__init__(master, fg_color="transparent", **kwargs)

        self.label = ctk.CTkLabel(
            self,
            text="Compression",
            font=(THEME["fonts"]["label_bold"][0], THEME["fonts"]["label_bold"][1], "bold"),
            text_color=colors["text_primary"],
            anchor="w",
        )
        self.label.pack(side="left", padx=(0, spacing["gap_md"]))

        preset_labels = [p[0] for p in COMPRESSION_PRESETS]
        self.var = ctk.StringVar(value=preset_labels[default])
        self.dropdown = ctk.CTkOptionMenu(
            self,
            variable=self.var,
            values=preset_labels,
            width=130,
            height=sizes["input_height"],
            font=(THEME["fonts"]["value"][0], THEME["fonts"]["value"][1]),
            fg_color=colors["bg_input"],
            button_color=colors["bg_tertiary"],
            button_hover_color=colors["bg_hover"],
            dropdown_fg_color=colors["bg_input"],
            dropdown_hover_color=colors["bg_hover"],
            text_color=colors["text_primary"],
            dropdown_text_color=colors["text_primary"],
            corner_radius=6,
        )
        self.dropdown.pack(side="left")

    def get_settings(self):
        preset_label = self.var.get()
        for label, colors_count, dither, quality in COMPRESSION_PRESETS:
            if label == preset_label:
                return colors_count, dither, quality
        return 128, "bayer", "medium"


class SpeedSlider(ctk.CTkFrame):
    def __init__(self, master, default=1.0, **kwargs):
        colors = THEME["colors"]
        sizes = THEME["sizes"]
        spacing = THEME["spacing"]
        super().__init__(master, fg_color="transparent", **kwargs)

        self.label = ctk.CTkLabel(
            self,
            text="Speed",
            font=(THEME["fonts"]["label_bold"][0], THEME["fonts"]["label_bold"][1], "bold"),
            text_color=colors["text_primary"],
            anchor="w",
        )
        self.label.pack(side="left", padx=(0, spacing["gap_md"]))

        self.slow_btn = ctk.CTkButton(
            self,
            text="0.5x",
            width=45,
            height=sizes["input_height"] - 8,
            font=(THEME["fonts"]["value"][0], 11),
            fg_color=colors["bg_input"],
            hover_color=colors["bg_hover"],
            text_color=colors["text_secondary"],
            corner_radius=6,
            command=lambda: self.set_speed(0.5),
        )
        self.slow_btn.pack(side="left", padx=(0, 4))

        self.normal_btn = ctk.CTkButton(
            self,
            text="1x",
            width=45,
            height=sizes["input_height"] - 8,
            font=(THEME["fonts"]["value"][0], 11),
            fg_color=colors["bg_input"],
            hover_color=colors["bg_hover"],
            text_color=colors["text_secondary"],
            corner_radius=6,
            command=lambda: self.set_speed(1.0),
        )
        self.normal_btn.pack(side="left", padx=(0, 4))

        self.fast_btn = ctk.CTkButton(
            self,
            text="2x",
            width=45,
            height=sizes["input_height"] - 8,
            font=(THEME["fonts"]["value"][0], 11),
            fg_color=colors["bg_input"],
            hover_color=colors["bg_hover"],
            text_color=colors["text_secondary"],
            corner_radius=6,
            command=lambda: self.set_speed(2.0),
        )
        self.fast_btn.pack(side="left", padx=(0, 4))

        self.fast2_btn = ctk.CTkButton(
            self,
            text="3x",
            width=45,
            height=sizes["input_height"] - 8,
            font=(THEME["fonts"]["value"][0], 11),
            fg_color=colors["bg_input"],
            hover_color=colors["bg_hover"],
            text_color=colors["text_secondary"],
            corner_radius=6,
            command=lambda: self.set_speed(3.0),
        )
        self.fast2_btn.pack(side="left", padx=(0, spacing["gap_sm"]))

        self.slider = ctk.CTkSlider(
            self,
            from_=0.25,
            to=4.0,
            number_of_steps=15,
            width=120,
            height=16,
            fg_color=colors["progress_bg"],
            progress_color=colors["accent"],
            button_color=colors["accent"],
            button_hover_color=colors["accent_hover"],
        )
        self.slider.set(default)
        self.slider.pack(side="left", fill="x", expand=True, padx=(0, spacing["gap_sm"]))

        self.value_label = ctk.CTkLabel(
            self,
            text=f"{default}x",
            font=(THEME["fonts"]["value"][0], THEME["fonts"]["value"][1], "bold"),
            text_color=colors["accent"],
            width=40,
        )
        self.value_label.pack(side="left")

        self.slider.configure(command=self._on_change)
        self._update_buttons(default)

    def _on_change(self, value):
        self.value_label.configure(text=f"{value:.2f}x".rstrip("0").rstrip("."))
        self._update_buttons(value)

    def _update_buttons(self, value):
        active_color = THEME["colors"]["accent"]
        inactive_color = THEME["colors"]["bg_input"]
        self.slow_btn.configure(fg_color=active_color if abs(value - 0.5) < 0.01 else inactive_color)
        self.normal_btn.configure(fg_color=active_color if abs(value - 1.0) < 0.01 else inactive_color)
        self.fast_btn.configure(fg_color=active_color if abs(value - 2.0) < 0.01 else inactive_color)
        self.fast2_btn.configure(fg_color=active_color if abs(value - 3.0) < 0.01 else inactive_color)

    def set_speed(self, speed):
        self.slider.set(speed)
        self.value_label.configure(text=f"{speed}x")
        self._update_buttons(speed)

    def get_speed(self):
        return round(self.slider.get(), 2)
