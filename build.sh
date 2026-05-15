#!/bin/bash
set -e

step() {
    echo ""
    echo "▶ $1"
}

done_msg() {
    echo "  ✓ $1"
}

# ── Step 1: FUSE check ──
step "Checking FUSE dependency"
if ! ldconfig -p | grep -q libfuse.so.2; then
    echo "  ⚠ libfuse2 not found. AppImage requires FUSE to run."
    echo "    Install with: sudo apt install libfuse2"
    read -p "  Continue anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi
done_msg "FUSE check passed"

# ── Step 2: Install dependencies ──
step "Installing build dependencies"
pip install pyinstaller --break-system-packages
done_msg "pyinstaller installed"

# ── Step 3: Download appimagetool ──
if ! command -v appimagetool &> /dev/null; then
    step "Downloading appimagetool"
    wget --progress=bar:force:noscroll \
        "https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage" \
        -O /tmp/appimagetool.AppImage
    chmod +x /tmp/appimagetool.AppImage
    sudo mv /tmp/appimagetool.AppImage /usr/local/bin/appimagetool
    done_msg "appimagetool installed"
else
    done_msg "appimagetool already installed ($(which appimagetool))"
fi

# ── Step 4: Download ffmpeg ──
step "Downloading static ffmpeg for Linux"
mkdir -p binaries
if [ ! -f "binaries/ffmpeg" ]; then
    curl --progress-bar \
        "https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz" \
        -o binaries/ffmpeg.tar.xz
    tar -xf binaries/ffmpeg.tar.xz -C binaries/ --strip-components=1
    find binaries/ -type f ! -name "ffmpeg" ! -name "ffprobe" -delete
    # Clean up empty directories left by tar extraction
    find binaries/ -type d ! -path "binaries" -exec rmdir {} + 2>/dev/null || true
    rm -f binaries/ffmpeg.tar.xz
    chmod +x binaries/ffmpeg binaries/ffprobe
    done_msg "ffmpeg downloaded ($(du -h binaries/ffmpeg | cut -f1))"
else
    done_msg "ffmpeg already present ($(du -h binaries/ffmpeg | cut -f1))"
fi

# ── Step 5: PyInstaller build ──
step "Building with PyInstaller"
rm -rf dist build
pyinstaller build.spec
if [ -d "dist/VideoToGIF" ]; then
    done_msg "PyInstaller build complete ($(du -sh dist/VideoToGIF | cut -f1))"
else
    echo "  ✗ PyInstaller build failed"
    exit 1
fi

# ── Step 6: Assemble AppDir ──
step "Assembling AppDir"
rm -rf AppDir
mkdir -p AppDir/usr/bin
cp -r dist/VideoToGIF/* AppDir/usr/bin/
ln -sf usr/bin/VideoToGIF.bin AppDir/AppRun

if [ -f "assets/jr_gif.png" ]; then
    python3 -c "
from PIL import Image
img = Image.open('assets/jr_gif.png')
img = img.resize((256, 256), Image.LANCZOS)
img.save('AppDir/VideoToGIF.png')
"
    ln -sf VideoToGIF.png AppDir/.DirIcon
    done_msg "Icon resized to 256x256"
else
    echo "  ⚠ No icon found at assets/jr_gif.png"
fi

cat > AppDir/VideoToGIF.desktop << 'EOF'
[Desktop Entry]
Name=Video to GIF Converter
Comment=Convert video clips to animated GIF files
Exec=VideoToGIF.bin
Icon=VideoToGIF
Terminal=false
Type=Application
Categories=Graphics;Video;
EOF
done_msg "AppDir assembled"

# ── Step 7: Build AppImage ──
step "Building AppImage"
appimagetool AppDir VideoToGIF.AppImage
done_msg "AppImage created"

# ── Done ──
echo ""
echo "═══════════════════════════════════════"
echo "  Build complete!"
echo "  Output: VideoToGIF.AppImage"
echo "  Size:   $(du -h VideoToGIF.AppImage | cut -f1)"
echo "═══════════════════════════════════════"
echo ""
echo "  Run: chmod +x VideoToGIF.AppImage && ./VideoToGIF.AppImage"
echo ""
