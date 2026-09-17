"""Windows notification-area integration."""

import os
import sys
import threading

from PIL import Image, ImageDraw
import pystray


class AnnotatorTrayMixin:
    def _start_tray(self):
        base_dir = getattr(sys, "_MEIPASS", os.path.dirname(__file__))
        png_path = os.path.join(base_dir, "ScreenDraw.png")
        if not os.path.exists(png_path):
            png_path = os.path.join(os.path.dirname(__file__), "ScreenDraw.png")

        if os.path.exists(png_path):
            image = Image.open(png_path).convert("RGBA")
        else:
            image = Image.new("RGBA", (64, 64), "#1e1e1e")
            draw = ImageDraw.Draw(image)
            draw.rectangle((14, 14, 50, 50), outline="#ff2d55", width=6)
            draw.line((22, 42, 42, 22), fill="#ffffff", width=4)

        menu = pystray.Menu(
            pystray.MenuItem("Show", lambda icon, item: self.root.after(0, self.show_app)),
            pystray.MenuItem("Exit", lambda icon, item: self.root.after(0, self.exit_app)),
        )
        self.tray_icon = pystray.Icon("ScreenAnnotator", image, "screen draw", menu)
        self.tray_thread = threading.Thread(target=self.tray_icon.run, daemon=True)
        self.tray_thread.start()

    def hide_app(self):
        # Reset click-through before hiding so the next Show starts interactive.
        self.set_tool("pointer")
        self._mouse_down = False
        self.overlay.withdraw()
        self.toolbar.withdraw()
        if getattr(self, "tray_icon", None) is None:
            self._start_tray()

    def show_app(self):
        def restore():
            self.overlay.deiconify()
            self.toolbar.deiconify()
            self.set_tool("pointer")
            self.overlay.lift()
            self.toolbar.lift()
            self.toolbar.focus_force()

        self.root.after_idle(restore)

    def _stop_tray(self):
        if getattr(self, "tray_icon", None) is not None:
            self.tray_icon.stop()
            self.tray_icon = None