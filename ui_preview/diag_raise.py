"""Pinpoint why DashboardPage.tkraise() is a no-op."""
import sys
sys.path.insert(0, ".")
from gui.main_window import MainWindow

app = MainWindow()
app.withdraw()
app.update_idletasks()

dash = app.frames["DashboardPage"]
print("type:", type(dash).__name__, type(dash).__mro__[1].__name__)
print("dash pathname:", dash._w)
print("dash master:", dash.master._w if hasattr(dash.master, "_w") else dash.master)
print("container pathname:", app.container._w)
print("same parent:", str(dash.master._w) == str(app.container._w) if hasattr(dash.master, "_w") else "n/a")
print("dash winfo parent:", dash.winfo_parent())
print("container children:", [c.winfo_name() for c in app.container.winfo_children()])

# try lift explicitly
dash.lift()
app.update_idletasks()
order = [c.winfo_name() for c in app.container.winfo_children()]
print("after lift, topmost:", order[-1])

# try tk call raise
app.container.tk.call("raise", dash._w)
app.update_idletasks()
order = [c.winfo_name() for c in app.container.winfo_children()]
print("after tcl raise, topmost:", order[-1])
app.destroy()
