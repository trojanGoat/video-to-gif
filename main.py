"""Entry point for the Video to GIF Converter."""

import sys
import os

if getattr(sys, "frozen", False):
    sys.path.insert(0, os.path.dirname(sys.executable))

from ui.app import App


def main():
    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()
