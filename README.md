# Video to GIF Converter

A modern, beautiful desktop application for converting video clips to animated GIF files.

## Features

- **Drag & Drop**: Simply drag a video file onto the app or click to browse
- **Range Selection**: Select the exact portion of video to convert with an intuitive slider
- **Speed Control**: Retimer from 0.25x to 4.0x with quick presets
- **Compression Presets**: Best Quality, Balanced, Small Size, or Tiny
- **Smart Resizing**: Video fills the entire frame — landscape videos fit width, portrait videos fit height, with excess cropped
- **Video & GIF Preview**: Preview frames before and after conversion
- **Dark Theme**: Sleek, modern dark UI built with CustomTkinter
- **Progress Tracking**: Real-time progress bar and status updates
- **Input Validation**: Helpful error messages for invalid inputs

## Building the AppImage

Build a self-contained AppImage that runs on any x86_64 Linux system without requiring Python, pip, or ffmpeg.

### Prerequisites

- Ubuntu 22.04+ (or compatible Debian-based distro)
- Python 3.8+ with pip
- `libfuse2` (required to run AppImage): `sudo apt install libfuse2`

### Build Steps

```bash
# 1. Install Python dependencies
pip install -r requirements.txt --break-system-packages

# 2. Run the build script
chmod +x build.sh
./build.sh
```

The build script will:
1. Check for `libfuse2` and prompt if missing
2. Install PyInstaller
3. Download `appimagetool` (if not already installed)
4. Download static ffmpeg/ffprobe binaries for Linux
5. Build the PyInstaller one-dir bundle
6. Assemble the AppImage directory structure
7. Produce `VideoToGIF.AppImage` (~80-120MB)

### Running the AppImage

```bash
chmod +x VideoToGIF.AppImage
./VideoToGIF.AppImage
```

Or double-click from your file manager.

### What Gets Bundled

- Python runtime
- CustomTkinter + tkinterdnd2 (drag-and-drop support)
- Pillow (image processing)
- ffmpeg + ffprobe (static binaries)
- All application source code

## Running From Source

### Requirements

- Python 3.8+
- ffmpeg (must be available in your system PATH)

### Setup

```bash
# 1. Install Python dependencies
pip install -r requirements.txt

# 2. Install ffmpeg
#    Ubuntu/Debian: sudo apt install ffmpeg
#    macOS:         brew install ffmpeg
#    Arch Linux:    sudo pacman -S ffmpeg
#    Windows:       Download from ffmpeg.org and add to PATH

# 3. Run the application
python main.py
```

## Usage

1. **Select Video**: Drag & drop a video file or click the drop zone to browse
2. **Set Output**: Choose where to save the GIF file
3. **Configure Settings**:
   - **Range**: Drag the slider handles to select the clip portion
   - **Frame Rate**: 1-30 fps (default: 10)
   - **Speed**: 0.25x to 4.0x retimer with quick presets (0.5x, 1x, 2x, 3x)
   - **Size**: Choose a preset or enter custom WxH dimensions
   - **Compression**: Best Quality, Balanced, Small Size, or Tiny
4. **Preview**: Review video frames before converting
5. **Convert**: Click "Convert to GIF" and watch the progress

## Project Structure

```
oc_project8/
├── main.py              # Entry point
├── utils.py             # Resource path helpers for bundled mode
├── build.spec           # PyInstaller configuration
├── build.sh             # AppImage build script
├── requirements.txt     # Python dependencies
├── README.md            # This file
├── ui/
│   ├── __init__.py
│   ├── app.py           # Main application window
│   ├── components.py    # Reusable UI components (DropZone, Sliders, Selectors)
│   ├── theme.py         # Theme colors, fonts, sizes, presets
│   └── preview.py       # Video and GIF preview widgets
├── converter/
│   ├── __init__.py
│   ├── video_to_gif.py  # Core conversion logic (ffmpeg wrapper)
│   └── validator.py     # Input validation utilities
└── assets/
    └── jr_gif.png       # Application icon (2048x2048)
```

## Build Output (Excluded from Git)

```
oc_project8/
├── binaries/            # Downloaded ffmpeg/ffprobe static binaries
├── build/               # PyInstaller temporary files
├── dist/                # PyInstaller one-dir output
├── AppDir/              # AppImage directory structure (temporary)
└── VideoToGIF.AppImage  # Final distributable AppImage
```

## Supported Video Formats

MP4, MOV, AVI, MKV, WebM, FLV, WMV, M4V, MPEG, MPG

## Known Issues

- **FUSE on Ubuntu 22.04+**: AppImage requires `libfuse2`. Install with `sudo apt install libfuse2`
- **Architecture**: AppImage builds are x86_64 only. ARM builds require building on ARM hardware
- **glibc compatibility**: AppImage works on systems with glibc >= the build machine's version

## License

MIT
