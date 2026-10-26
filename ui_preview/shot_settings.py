"""Capture Settings page in Dark + Light (brief visible flash, no camera)."""
import sys, time
sys.path.insert(0, ".")
from PIL import ImageGrab
from gui.main_window import MainWindow

app = MainWindow()
app.show_frame("SettingsPage")
app.deiconify()
app.attributes("-topmost", True)
app.focus_force()
app.update_idletasks()
app.update()
app.lift()
time.sleep(1.5)
app.update()

def grab(name):
    x, y = app.winfo_rootx(), app.winfo_rooty()
    w, h = app.winfo_width(), app.winfo_height()
    shot = ImageGrab.grab(bbox=(x, y, x + w, y + h))
    shot.save(f"ui_preview/{name}")
    print("saved", name, shot.size)

grab("settings_dark.png")
app.set_theme("Light")
app.show_frame("SettingsPage")
app.update()
time.sleep(1.0)
app.update()
grab("settings_light.png")
app.destroy()
