"""Toggle Dark->Light and grab frames to find black-flash duration."""
import sys, time, statistics
sys.path.insert(0, ".")
from PIL import ImageGrab, ImageStat
from gui.main_window import MainWindow

app = MainWindow()
app.show_frame("SettingsPage")
app.deiconify()
app.attributes("-topmost", True)
app.focus_force()
app.update_idletasks()
app.update()
time.sleep(1.0)
app.update()

x, y = app.winfo_rootx(), app.winfo_rooty()
w, h = app.winfo_width(), app.winfo_height()

# baseline brightness
base = ImageGrab.grab(bbox=(x, y, x + w, y + h))
b0 = ImageStat.Stat(base.convert("L")).mean[0]
print(f"baseline mean brightness = {b0:.1f}")

# toggle in main thread, but grab very fast right after
t0 = time.time()
app.set_theme("Light")
t1 = time.time()
print(f"set_theme took {t1-t0:.3f}s")

samples = []
for i in range(40):
    shot = ImageGrab.grab(bbox=(x, y, x + w, y + h)).convert("L")
    m = ImageStat.Stat(shot).mean[0]
    dt = time.time() - t0
    samples.append((dt, m))
    app.update()
    time.sleep(0.05)

dark_frames = [(dt, m) for dt, m in samples if m < b0 * 0.45]
print("frames (time, mean):")
for dt, m in samples[:25]:
    flag = " <== BLACK" if m < b0 * 0.45 else ""
    print(f"  {dt:5.3f}s  {m:6.1f}{flag}")
if dark_frames:
    print(f"BLACK duration ~ {dark_frames[-1][0]-dark_frames[0][0]:.2f}s, count={len(dark_frames)}")
else:
    print("NO black frames detected")
app.destroy()
