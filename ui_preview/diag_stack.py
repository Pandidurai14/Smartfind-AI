"""Diagnose which frame is actually on top (stacking order)."""
import sys
sys.path.insert(0, ".")
from gui.main_window import MainWindow

app = MainWindow()
app.withdraw()
app.update_idletasks()

for page in ["DashboardPage", "SettingsPage", "MatchesPage", "DashboardPage"]:
    app.show_frame(page)
    app.update_idletasks()
    order = [str(w).split(".")[-1] for w in app.container.winfo_children()]
    top = order[-1]
    print(f"show {page}: current_page={app.current_page} topmost={top} full_order={order}")

app.destroy()
