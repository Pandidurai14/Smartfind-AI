import customtkinter as ctk
from gui.main_window import MainWindow
import config  # இது run ஆகும்போது config.py-ல் உள்ள empty folders உருவாகிவிடும்

def main():
    ctk.set_appearance_mode("Dark")
    ctk.set_default_color_theme("blue")
    
    app = MainWindow()
    app.mainloop()

if __name__ == "__main__":
    main()