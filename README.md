# Video to GIF Converter

A modern, beautiful desktop application for converting video clips to animated GIF files.

## Features

- **Drag & Drop**: Simply drag a video file onto the app or click to browse
- **Range Selection**: Select the exact portion of video to convert with an intuitive slider
- **Speed Control**: Retimer from 0.25x to 4.0x with quick presets
- **Compression Presets**: Best Quality, Balanced, Small Size, or Tiny
- **Smart Resizing**: Letterboxing/pillarboxing ensures your video is never stretched or distorted
- **Video & GIF Preview**: Preview frames before and after conversion
- **Dark Theme**: Sleek, modern dark UI built with CustomTkinter
- **Progress Tracking**: Real-time progress bar and status updates
- **Input Validation**: Helpful error messages for invalid inputs

## Standalone Build (AppImage)

Build a self-contained AppImage that runs on any x86_64 Linux system without requiring Python, pip, or ffmpeg:

```bash
chmod +x build.sh
./build.sh
```

This produces `VideoToGIF.AppImage` (~80-120MB). Copy it anywhere and run:

```bash
chmod +x VideoToGIF.AppImage
./VideoToGIF.AppImage
```

**Note:** Requires `libfuse2` on Ubuntu 22.04+: `sudo apt install libfuse2`

## From Source

### Requirements

- Python 3.8+
- ffmpeg (must be available in your system PATH)

### Installation

1. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Install ffmpeg:
   - **macOS**: `brew install ffmpeg`
   - **Ubuntu/Debian**: `sudo apt install ffmpeg`
   - **Windows**: Download from [ffmpeg.org](https://ffmpeg.org/download.html) and add to PATH
   - **Arch Linux**: `sudo pacman -S ffmpeg`

3. Run the application:
   ```bash
   python main.py
   ```

## Usage

1. **Select Video**: Drag & drop a video file or click the drop zone to browse
2. **Set Output**: Choose where to save the GIF file
3. **Configure Settings**:
   - Range: Drag the slider handles to select the clip portion
   - Frame Rate: 1-30 fps (default: 10)
   - Speed: 0.25x to 4.0x retimer
   - Size: Choose a preset or enter custom dimensions
   - Compression: Best Quality, Balanced, Small Size, or Tiny
4. **Preview**: Review video frames before converting
5. **Convert**: Click "Convert to GIF" and watch the progress

## Project Structure

```
oc_project8/
├── main.py              # Entry point
├── utils.py             # Resource path helpers for bundled mode
├── build.spec           # PyInstaller configuration
├── build.sh             # AppImage build script
├── ui/
│   ├── __init__.py
│   ├── app.py           # Main application window
│   ├── components.py    # Reusable UI components
│   ├── theme.py         # Theme colors and styles
│   └── preview.py       # Video and GIF preview widgets
├── converter/
│   ├── __init__.py
│   ├── video_to_gif.py  # Core conversion logic
│   └── validator.py     # Input validation
├── assets/
│   └── jr_gif.png       # Application icon
├── requirements.txt
└── README.md
```

## License

MIT
