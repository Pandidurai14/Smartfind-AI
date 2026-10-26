"""Capture actual Dashboard window pixels (brief visible flash, no camera)."""
import sys, time
sys.path.insert(0, ".")
from PIL import ImageGrab
from gui.main_window import MainWindow

app = MainWindow()
app.show_frame("DashboardPage")
app.deiconify()
app.attributes("-topmost", True)
app.focus_force()
app.update_idletasks()
app.update()
app.lift()
time.sleep(2.0)
app.update()
x, y = app.winfo_rootx(), app.winfo_rooty()
w, h = app.winfo_width(), app.winfo_height()
shot = ImageGrab.grab(bbox=(x, y, x + w, y + h))
shot.save("ui_preview/dashboard_actual.png")
print("saved ui_preview/dashboard_actual.png", shot.size)
app.destroy()
