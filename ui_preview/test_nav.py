"""Nav-highlight + theme verification (no camera started)."""
import sys
sys.path.insert(0, ".")
from gui.main_window import MainWindow, ACCENT

app = MainWindow()
app.withdraw()
app.update_idletasks()

pages = ["DashboardPage", "LiveCameraPage", "VideoSearchPage", "MatchesPage", "ReportPage", "SettingsPage"]
for page in pages:
    app.show_frame(page)
    app.update_idletasks()
    assert app.current_page == page, page
    for k, btn in app.nav_buttons.items():
        fg = str(btn.cget("fg_color"))
        if k == page:
            assert fg.lower() == ACCENT.lower(), f"{page}: active btn {k} fg={fg}"
        else:
            assert fg.lower() == "transparent", f"{page}: inactive btn {k} fg={fg}"
    print(f"OK {page}: highlight + raise correct")

# theme toggle
for mode, expect_bg in [("Light", "#d5dce8"), ("Dark", "#0b1a33")]:
    app.set_theme(mode)
    app.update_idletasks()
    assert app.current_theme == mode, mode
    for key in ("LiveCameraPage", "VideoSearchPage"):
        bg = str(app.frames[key].canvas.cget("bg"))
        assert bg.lower() == expect_bg.lower(), (mode, key, bg)
    print(f"OK theme {mode}: canvas bg={expect_bg}, stayed on {app.current_page}")

print("ALL NAV + THEME TESTS PASSED")
app.destroy()
