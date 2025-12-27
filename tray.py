import threading
import pystray
from PIL import Image

class TrayIcon:
    def __init__(self, on_exit):
        self.on_exit = on_exit
        self.icon = pystray.Icon("OSC2Yukari", Image.new("RGB", (16, 16), "blue"))
        self.icon.menu = pystray.Menu(
            pystray.MenuItem("Exit", self.exit)
        )

    def start(self):
        threading.Thread(target=self.icon.run, daemon=True).start()

    def exit(self):
        self.icon.stop()
        self.on_exit()
