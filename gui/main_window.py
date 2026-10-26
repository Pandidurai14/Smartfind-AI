import customtkinter as ctk
from tkinter import filedialog
import cv2
import numpy as np
import os
from datetime import datetime
from PIL import Image, ImageTk
from camera.camera import CameraStream
from ai_engine.detector import PersonDetector
from ai_engine.face_engine import FaceEngine


def load_app_logo(size=40):
    """assets/logo.png AV monogram crop -> PIL image (None if missing).

    Full logo = AV mark (top) + ALPHA VISION text (bottom). Icon box ku
    AV mark mattum crop pannrom.
    """
    try:
        base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        for name in ("logo.png", "logo.jpg", "logo.jpeg"):
            p = os.path.join(base, "assets", name)
            if os.path.isfile(p):
                img = Image.open(p).convert("RGB")
                w, h = img.size
                mono = img.crop((int(w * 0.13), int(h * 0.15), int(w * 0.90), int(h * 0.60)))
                mono.thumbnail((size, size), Image.LANCZOS)
                return mono
    except Exception as e:
        print(f"Logo load failed: {e}")
    return None

# --- SmartFind AI V5 theme: (light, dark) tuples so set_appearance_mode works ---
# Light mode = soft grey-blue (no over-bright pure white)
BG = ("#dde3ec", "#0a1428")
SIDEBAR = ("#e9edf4", "#0e1d38")
CARD = ("#f2f5f9", "#132442")
BORDER = ("#ccd5e2", "#1e3a5f")
TITLE_TXT = ("#1c2b45", "white")
MUTED_TXT = ("#5d6e88", "#8a9bb5")
ACCENT = "#2f80ed"
ACCENT_HOVER = "#1e6fd9"
GREEN = "#2ecc71"
ORANGE = "#f39c12"
RED = "#e74c3c"
CANVAS_BG = ("#d5dce8", "#0b1a33")
CAPTURE_BG = ("#c9d3e1", "#1a2f52")
SWITCH_ON = ("#2f80ed", "#2f80ed")

# Backward compat aliases
BG_DARK = BG
SIDEBAR_BG = SIDEBAR
CARD_BG = CARD
CARD_BORDER = BORDER
MUTED = MUTED_TXT


class MainWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("blue")
        self.title("SmartFind AI V5.0 - Find • Track • Secure")
        self.geometry("1380x820")
        self.configure(fg_color=BG)
        self.current_theme = "Dark"
        self.current_page = "DashboardPage"

        # --- Deep-learning backend: YOLOv11 + ArcFace (InsightFace) ---
        self.yolo_ok = False
        self.face_ok = False
        try:
            self.detector = PersonDetector()
            self.yolo_ok = True
        except Exception as e:
            print(f"YOLO load failed: {e}")
            self.detector = None
        try:
            self.face_engine = FaceEngine()
            self.face_ok = True
        except Exception as e:
            print(f"Face model load failed: {e}")
            self.face_engine = None
        self.target_embedding = None
        self.current_target_image = None
        self.current_target_original = None
        self.auto_pdf_enabled = False
        self.sound_enabled = True
        self._load_app_settings()
        self.cameras_connected = 0

        # ----- Top bar -----
        self.topbar = ctk.CTkFrame(self, fg_color=BG, height=62)
        self.topbar.pack(fill="x", padx=12, pady=(10, 4))
        self.topbar.pack_propagate(False)

        logo_box = ctk.CTkFrame(self.topbar, fg_color="white", width=44, height=44, corner_radius=10)
        logo_box.pack(side="left", padx=(4, 10), pady=8)
        logo_box.pack_propagate(False)
        logo_pil = load_app_logo(40)
        if logo_pil is not None:
            self._logo_ctk = ctk.CTkImage(light_image=logo_pil, dark_image=logo_pil, size=logo_pil.size)
            ctk.CTkLabel(logo_box, image=self._logo_ctk, text="", fg_color="white").pack(expand=True)
            try:
                self._logo_tk = ImageTk.PhotoImage(logo_pil.resize((32, 32), Image.LANCZOS))
                self.iconphoto(True, self._logo_tk)
            except Exception:
                pass
        else:
            ctk.CTkLabel(logo_box, text="A", font=ctk.CTkFont(size=22, weight="bold"), text_color="#0a1428").pack(expand=True)

        title_box = ctk.CTkFrame(self.topbar, fg_color="transparent")
        title_box.pack(side="left")
        ctk.CTkLabel(title_box, text="SmartFind AI", font=ctk.CTkFont(size=22, weight="bold"), text_color=TITLE_TXT).pack(anchor="w")
        ctk.CTkLabel(title_box, text="Find • Track • Secure", font=ctk.CTkFont(size=12), text_color=MUTED_TXT).pack(anchor="w")

        # right side
        admin_box = ctk.CTkFrame(self.topbar, fg_color="transparent")
        admin_box.pack(side="right", padx=6)
        ctk.CTkLabel(admin_box, text="A", font=ctk.CTkFont(size=14, weight="bold"), text_color="black",
                     fg_color="#b8b8f0", width=32, height=32, corner_radius=16).pack(side="left", padx=(0, 8))
        ctk.CTkLabel(admin_box, text="Admin  ▾", font=ctk.CTkFont(size=14), text_color=TITLE_TXT).pack(side="left", padx=(0, 12))
        ctk.CTkLabel(admin_box, text="🔔", font=ctk.CTkFont(size=18)).pack(side="left", padx=6)
        self.backend_label = ctk.CTkLabel(admin_box, text="● Loading models...",
                                          font=ctk.CTkFont(size=13), text_color="#f0a35e")
        self.backend_label.pack(side="left", padx=10)
        self.update_backend_status()

        sep = ctk.CTkFrame(self, fg_color=BORDER, height=1)
        sep.pack(fill="x", padx=24, pady=0)

        # ----- Body: sidebar + container -----
        self.body = ctk.CTkFrame(self, fg_color="transparent")
        self.body.pack(fill="both", expand=True, padx=12, pady=6)
        self.body.grid_columnconfigure(1, weight=1)
        self.body.grid_rowconfigure(0, weight=1)

        self.sidebar = ctk.CTkFrame(self.body, fg_color=SIDEBAR, width=220, corner_radius=14)
        self.sidebar.grid(row=0, column=0, sticky="nsw", padx=(0, 10))
        self.sidebar.grid_propagate(False)
        self.sidebar.configure(width=220)

        self.nav_buttons = {}
        ctk.CTkLabel(self.sidebar, text="MENU", font=ctk.CTkFont(size=11, weight="bold"),
                     text_color=MUTED_TXT).pack(anchor="w", padx=20, pady=(14, 2))
        nav_items = [
            ("DashboardPage", "⌂  Dashboard"),
            ("LiveCameraPage", "❖  Live Cameras"),
            ("VideoSearchPage", "○  Video Search"),
            ("MatchesPage", "✔  Matches"),
            ("ReportPage", "▤  Report"),
            ("SettingsPage", "⚙  Settings"),
        ]
        for i, (key, txt) in enumerate(nav_items):
            b = ctk.CTkButton(self.sidebar, text=txt, anchor="w", height=42,
                              font=ctk.CTkFont(size=14, weight="bold" if i == 0 else "normal"),
                              fg_color=ACCENT if i == 0 else "transparent",
                              hover_color="#1a2f52", text_color=TITLE_TXT,
                              command=lambda k=key: self.show_frame(k))
            b.pack(fill="x", padx=10, pady=4 if i > 0 else (2, 4))
            self.nav_buttons[key] = b

        # Authorized box
        auth = ctk.CTkFrame(self.sidebar, fg_color="transparent", border_width=1, border_color=CARD_BORDER, corner_radius=10)
        auth.pack(side="bottom", fill="x", padx=10, pady=(6, 6))
        ctk.CTkLabel(auth, text="🛡 Authorized Access Only", font=ctk.CTkFont(size=12, weight="bold"), text_color=TITLE_TXT,
                     wraplength=180, justify="left").pack(anchor="w", padx=10, pady=(10, 4))
        ctk.CTkLabel(auth, text="This system is for security and defence use. All data is handled with strict privacy and security protocols.",
                     font=ctk.CTkFont(size=11), text_color=MUTED, wraplength=180, justify="left").pack(anchor="w", padx=10, pady=(0, 10))
        ctk.CTkLabel(self.sidebar, text="SmartFind AI V5.0\nAI-Powered Multi-Camera Search & Tracking",
                     font=ctk.CTkFont(size=11), text_color=ACCENT, justify="left").pack(side="bottom", anchor="w", padx=12, pady=(0, 12))

        self.container = ctk.CTkFrame(self.body, fg_color="transparent")
        self.container.grid(row=0, column=1, sticky="nsew")
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for PageClass in (DashboardPage, LiveCameraPage, VideoSearchPage, MatchesPage, ReportPage, SettingsPage):
            page_name = PageClass.__name__
            frame = PageClass(parent=self.container, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("DashboardPage")

    def show_frame(self, page_name):
        self.current_page = page_name
        # highlight nav - active: blue bg + white text, inactive: transparent + theme text
        for k, btn in self.nav_buttons.items():
            if k == page_name:
                btn.configure(fg_color=ACCENT, text_color="white", font=ctk.CTkFont(size=14, weight="bold"))
            else:
                btn.configure(fg_color="transparent", text_color=TITLE_TXT, font=ctk.CTkFont(size=14))
        # stop streams when leaving
        if page_name != "LiveCameraPage" and "LiveCameraPage" in self.frames:
            try:
                self.frames["LiveCameraPage"].stop_camera()
            except Exception:
                pass
        if page_name != "VideoSearchPage" and "VideoSearchPage" in self.frames:
            try:
                self.frames["VideoSearchPage"].stop_video()
            except Exception:
                pass
        frame = self.frames[page_name]
        frame.tkraise()
        # Dashboard stats live update
        if page_name == "DashboardPage":
            try:
                frame.refresh_stats()
            except Exception:
                pass
        # Matches page open panna auto-refresh - pudhu match udane theriyum
        if page_name == "MatchesPage":
            try:
                frame.refresh()
            except Exception as e:
                print(f"Matches refresh error: {e}")
        if page_name == "ReportPage":
            try:
                frame.refresh()
            except Exception as e:
                print(f"Report refresh error: {e}")

    def update_backend_status(self):
        """Top-right real status: YOLO + Face loaded? Camera on?"""
        if self.yolo_ok and self.face_ok:
            txt = f"● Backend Online | YOLO ✓ Face ✓ | {self.cameras_connected} camera(s)"
            col = "#2ecc71"
        else:
            missing = []
            if not self.yolo_ok:
                missing.append("YOLO ✗")
            if not self.face_ok:
                missing.append("Face ✗")
            txt = f"● Backend Offline ({' '.join(missing)}) | {self.cameras_connected} camera(s)"
            col = "#f0a35e"
        try:
            self.backend_label.configure(text=txt, text_color=col)
        except Exception:
            pass

    def set_camera_count(self, n):
        self.cameras_connected = n
        self.update_backend_status()

    def _base_dir(self):
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    def _report_json_path(self):
        reports_dir = os.path.join(self._base_dir(), "reports")
        os.makedirs(reports_dir, exist_ok=True)
        return os.path.join(reports_dir, "match_reports.json")

    # ---------- Important badge (shared by Matches + Report) ----------
    def _important_json_path(self):
        reports_dir = os.path.join(self._base_dir(), "reports")
        os.makedirs(reports_dir, exist_ok=True)
        return os.path.join(reports_dir, "important.json")

    def _load_important(self):
        import json
        path = self._important_json_path()
        if os.path.isfile(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                if isinstance(data, list):
                    return set(str(x) for x in data)
            except Exception as e:
                print(f"Important JSON read failed: {e}")
        return set()

    def _save_important(self, items):
        import json
        try:
            with open(self._important_json_path(), "w", encoding="utf-8") as f:
                json.dump(sorted(items), f, indent=2)
        except Exception as e:
            print(f"Important JSON save failed: {e}")

    def is_important(self, key):
        """key = match image basename (Matches file == Report record match_image)."""
        if not key:
            return False
        return str(key) in self._load_important()

    def toggle_important(self, key):
        """Flip important flag; returns new state (True = important now)."""
        items = self._load_important()
        k = str(key)
        if k in items:
            items.discard(k)
            state = False
        else:
            items.add(k)
            state = True
        self._save_important(items)
        return state

    def set_important(self, key, state=True):
        """Force-set important flag (Live/Video search session toggle ku)."""
        items = self._load_important()
        k = str(key)
        if state:
            items.add(k)
        else:
            items.discard(k)
        self._save_important(items)
        return state

    def _settings_json_path(self):
        reports_dir = os.path.join(self._base_dir(), "reports")
        os.makedirs(reports_dir, exist_ok=True)
        return os.path.join(reports_dir, "app_settings.json")

    def _load_app_settings(self):
        import json
        try:
            path = self._settings_json_path()
            if os.path.isfile(path):
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self.auto_pdf_enabled = bool(data.get("auto_pdf_enabled", False))
                self.sound_enabled = bool(data.get("sound_enabled", True))
        except Exception as e:
            print(f"Settings load failed: {e}")

    def save_app_settings(self):
        import json
        try:
            with open(self._settings_json_path(), "w", encoding="utf-8") as f:
                json.dump({
                    "auto_pdf_enabled": self.auto_pdf_enabled,
                    "sound_enabled": self.sound_enabled,
                }, f, indent=2)
        except Exception as e:
            print(f"Settings save failed: {e}")

    def play_match_sound(self):
        if not self.sound_enabled:
            return
        try:
            import winsound
            winsound.Beep(1200, 180)
            winsound.Beep(1600, 180)
        except Exception:
            try:
                self.bell()
            except Exception:
                pass

    def _load_report_records(self):
        import json
        path = self._report_json_path()
        if not os.path.isfile(path):
            return []
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return data if isinstance(data, list) else []
        except Exception as e:
            print(f"Report JSON read failed: {e}")
            return []

    def _save_report_records(self, records):
        import json
        path = self._report_json_path()
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(records, f, indent=2)
        except Exception as e:
            print(f"Report JSON save failed: {e}")

    def set_target_image(self, file_path):
        """Copy selected target into reports/targets so report is stable."""
        import shutil
        try:
            targets_dir = os.path.join(self._base_dir(), "reports", "targets")
            os.makedirs(targets_dir, exist_ok=True)
            ext = os.path.splitext(file_path)[1] or ".jpg"
            out = os.path.join(targets_dir, f"target_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}{ext}")
            shutil.copy(file_path, out)
            self.current_target_image = out
            self.current_target_original = file_path
            return out
        except Exception as e:
            print(f"Target copy failed: {e}")
            self.current_target_image = file_path
            self.current_target_original = file_path
            return file_path

    def add_report_record(self, match_path, track_id, score, found_at, source_name):
        """Store every confirmed match with target image + found image + timing."""
        record = {
            "id": f"RPT-{datetime.now().strftime('%Y%m%d%H%M%S')}-{track_id}",
            "track_id": int(track_id),
            "score": round(float(score), 2),
            "found_at": found_at.strftime("%Y-%m-%d %H:%M:%S") if hasattr(found_at, "strftime") else str(found_at),
            "source": source_name,
            "target_image": self.current_target_image,
            "target_original": self.current_target_original,
            "match_image": match_path,
        }
        records = self._load_report_records()
        records.insert(0, record)
        self._save_report_records(records)
        self.play_match_sound()
        try:
            rp = self.frames.get("ReportPage")
            if rp is not None:
                rp.pending_refresh = True
                if self.auto_pdf_enabled:
                    rp.generate_auto_pdf(record)
        except Exception:
            pass
        return record

    def set_theme(self, mode):
        """Dark / Light switch - called from SettingsPage. CTk tuple colors auto-switch.

        Switch-a oru solid cover frame-la mask pannrom, so full window repaint
        time-la black flash theriyaadhu (user-ku smooth transition).
        """
        if mode not in ("Dark", "Light"):
            mode = "Dark"
        if mode == self.current_theme:
            return
        self.current_theme = mode

        # --- cover: target background color screen-la paint aagiya piragu mattum switch ---
        import tkinter as tk
        new_bg = "#0a1428" if mode == "Dark" else "#dde3ec"
        cover = tk.Frame(self, bg=new_bg)
        cover.place(x=0, y=0, relwidth=1, relheight=1)
        self.update_idletasks()  # cover paint aagattum

        try:
            ctk.set_appearance_mode(mode)
            # CTkCanvas does not auto-switch, update manually
            bg = "#0b1a33" if mode == "Dark" else "#d5dce8"
            for key in ("LiveCameraPage", "VideoSearchPage"):
                try:
                    page = self.frames.get(key)
                    if page and hasattr(page, "canvas"):
                        page.canvas.configure(bg=bg)
                except Exception:
                    pass
            try:
                dash = self.frames.get("DashboardPage")
                if dash is not None and hasattr(dash, "repaint_icons"):
                    dash.repaint_icons(mode)
            except Exception:
                pass
            # refresh nav highlight, stay on same page
            self.show_frame(getattr(self, "current_page", "DashboardPage"))
            self.update_idletasks()  # new theme full-a paint aagattum
        finally:
            cover.destroy()
            self.update_idletasks()


class DashboardPage(ctk.CTkFrame):
    # NOTE: outer must stay a plain CTkFrame - CTkScrollableFrame binds its
    # object to an INNER canvas frame, so tkraise() page-switching silently
    # fails on it. Scrolling is provided by inner self.scroll instead.
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.scroll = ctk.CTkScrollableFrame(self, fg_color="transparent", scrollbar_button_color=CARD_BORDER)
        self.scroll.grid(row=0, column=0, sticky="nsew")

        # ----- Welcome banner -----
        banner = ctk.CTkFrame(self.scroll, fg_color=CARD_BG, corner_radius=14, border_width=1, border_color=CARD_BORDER)
        banner.pack(fill="x", padx=4, pady=6)
        banner.grid_columnconfigure(1, weight=1)
        accent = ctk.CTkFrame(banner, fg_color=ACCENT, width=4, height=60, corner_radius=2)
        accent.grid(row=0, column=0, sticky="ns", padx=(14, 0), pady=10)
        accent.grid_propagate(False)
        left = ctk.CTkFrame(banner, fg_color="transparent")
        left.grid(row=0, column=1, sticky="w", padx=14, pady=8)
        row1 = ctk.CTkFrame(left, fg_color="transparent")
        row1.pack(anchor="w")
        ctk.CTkLabel(row1, text="Welcome to ", font=ctk.CTkFont(size=22, weight="bold"), text_color=TITLE_TXT).pack(side="left")
        ctk.CTkLabel(row1, text="SmartFind AI", font=ctk.CTkFont(size=22, weight="bold"), text_color=ACCENT).pack(side="left")
        sub1 = ctk.CTkFrame(left, fg_color="transparent")
        sub1.pack(anchor="w", pady=(4, 0))
        ctk.CTkLabel(sub1, text="Search across multiple ", font=ctk.CTkFont(size=12), text_color=MUTED).pack(side="left")
        ctk.CTkLabel(sub1, text="camera feeds", font=ctk.CTkFont(size=12, weight="bold"), text_color=ACCENT).pack(side="left")
        ctk.CTkLabel(sub1, text=". Track movements. Get results.", font=ctk.CTkFont(size=12), text_color=MUTED).pack(side="left")
        ctk.CTkLabel(left, text="Faster. Smarter. Safer.", font=ctk.CTkFont(size=12), text_color=MUTED).pack(anchor="w")
        # appearance mode (icon canvases use this - seamless card bg)
        try:
            mode = ctk.get_appearance_mode()
        except Exception:
            mode = "Dark"
        self._icon_bg = "#132442" if mode != "Light" else "#f2f5f9"
        self._icon_items = []

        # ----- Stats row (live numbers) -----
        stats = ctk.CTkFrame(self.scroll, fg_color="transparent")
        stats.pack(fill="x", padx=4, pady=6)
        self.stat_num_labels = []
        stat_keys = ["cams", "matches", "models"]
        for i, key in enumerate(stat_keys):
            card = ctk.CTkFrame(stats, fg_color=CARD_BG, corner_radius=12, border_width=1, border_color=CARD_BORDER)
            card.pack(side="left", fill="both", expand=True, padx=(0, 10) if i < 2 else (0, 0))
            strip = ctk.CTkFrame(card, fg_color=ACCENT, height=4, width=56, corner_radius=2)
            strip.pack(pady=(12, 0))
            strip.pack_propagate(False)
            num = ctk.CTkLabel(card, text="0", font=ctk.CTkFont(size=30, weight="bold"), text_color=ACCENT)
            num.pack(pady=(6, 2))
            self.stat_num_labels.append(num)
        # labels under numbers
        for i, label in enumerate(["Cameras connected", "Candidate matches", "AI models in pipeline"]):
            ctk.CTkLabel(stats.winfo_children()[i], text=label, font=ctk.CTkFont(size=12), text_color=MUTED).pack(pady=(0, 14))
        self.refresh_stats()

        # ----- Find / Track / Secure with drawn icons -----
        trio = ctk.CTkFrame(self.scroll, fg_color="transparent")
        trio.pack(fill="x", padx=4, pady=6)
        trio_info = [
            ("Find", "One photo → AI searches every authorized camera feed.", "Start Search →", "VideoSearchPage", self._draw_find),
            ("Track", "Candidates linked camera-to-camera on a live timeline.", "View Cameras →", "LiveCameraPage", self._draw_track),
            ("Secure", "Evidence snapshots + AI report for verified review.", "See Results →", "MatchesPage", self._draw_secure),
        ]
        for title, desc, btn_txt, target, draw_fn in trio_info:
            card = ctk.CTkFrame(trio, fg_color=CARD_BG, corner_radius=12, border_width=1, border_color=CARD_BORDER)
            card.pack(side="left", fill="both", expand=True, padx=(0, 10) if title != "Secure" else (0, 0))
            cv = ctk.CTkCanvas(card, width=220, height=110, highlightthickness=0, bg=self._icon_bg)
            cv.pack(pady=(14, 4), padx=10)
            try:
                draw_fn(cv)
                self._icon_items.append((cv, draw_fn))
            except Exception as e:
                print(f"icon draw {title}: {e}")
            ctk.CTkLabel(card, text=title, font=ctk.CTkFont(size=17, weight="bold"), text_color=TITLE_TXT).pack()
            ctk.CTkLabel(card, text=desc, font=ctk.CTkFont(size=11), text_color=MUTED, wraplength=260).pack(pady=6, padx=12)
            ctk.CTkButton(card, text=btn_txt, fg_color="#1a3355", hover_color="#24466f", text_color="#7fb3ff",
                          command=lambda t=target: controller.show_frame(t)).pack(fill="x", padx=12, pady=12)

        # ----- How it works -----
        how = ctk.CTkFrame(self.scroll, fg_color=CARD_BG, corner_radius=14, border_width=1, border_color=CARD_BORDER)
        how.pack(fill="x", padx=4, pady=8)
        ctk.CTkLabel(how, text="How it works", font=ctk.CTkFont(size=16, weight="bold"), text_color=TITLE_TXT).pack(anchor="w", padx=18, pady=(14, 2))
        ctk.CTkLabel(how, text="Detection → tracking → face + appearance match → report.",
                     font=ctk.CTkFont(size=12), text_color=MUTED).pack(anchor="w", padx=18, pady=(0, 10))
        steps_row = ctk.CTkFrame(how, fg_color="transparent")
        steps_row.pack(fill="x", padx=12, pady=(0, 14))
        steps = [("Target", "Reference photo", self._mini_target),
                 ("Detect", "YOLOv11", self._mini_detect),
                 ("Track", "ByteTrack", self._mini_track),
                 ("Match", "ArcFace + OSNet", self._mini_match),
                 ("Report", "GenAI summary", self._mini_report)]
        step_bg = self._icon_bg
        for idx, (t, s, painter) in enumerate(steps):
            sc = ctk.CTkFrame(steps_row, fg_color="transparent", border_width=1, border_color=CARD_BORDER, corner_radius=10)
            sc.pack(side="left", fill="both", expand=True, padx=4)
            icon_cv = ctk.CTkCanvas(sc, width=120, height=56, highlightthickness=0, bg=step_bg)
            icon_cv.pack(pady=(10, 2))
            try:
                painter(icon_cv)
                self._icon_items.append((icon_cv, painter))
            except Exception as e:
                print(f"mini icon {t}: {e}")
            ctk.CTkLabel(sc, text=t, font=ctk.CTkFont(size=13, weight="bold"), text_color=TITLE_TXT).pack()
            ctk.CTkLabel(sc, text=s, font=ctk.CTkFont(size=11), text_color=MUTED).pack(pady=(0, 10))
            if idx < len(steps) - 1:
                arrow = ctk.CTkLabel(steps_row, text="➔", font=ctk.CTkFont(size=18, weight="bold"), text_color="#4ade80")
                arrow.pack(side="left", padx=1)

    def repaint_icons(self, mode):
        """Theme switch la icon canvas bg sync (CTkCanvas auto-switch aagathu)."""
        bg = "#132442" if mode != "Light" else "#f2f5f9"
        self._icon_bg = bg
        for cv, painter in getattr(self, "_icon_items", []):
            try:
                cv.configure(bg=bg)
                painter(cv)
            except Exception:
                pass

    def refresh_stats(self):
        try:
            cams = getattr(self.controller, "cameras_connected", 0)
            base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            mdir = os.path.join(base, "saved_matches")
            n = len([f for f in os.listdir(mdir) if f.lower().endswith((".jpg", ".jpeg", ".png"))]) if os.path.isdir(mdir) else 0
            vals = [str(cams), str(n), "5"]
            for lbl, v in zip(self.stat_num_labels, vals):
                lbl.configure(text=v)
        except Exception:
            pass

    # --- icon painters (blue/green neon like screenshot) ---
    # How-it-works mini diagrams - full color
    def _mini_target(self, cv):
        cv.delete("all")
        cv.create_rectangle(35, 18, 85, 46, fill="#1d4ed8", outline="#38bdf8", width=2)   # camera body
        cv.create_rectangle(78, 12, 92, 20, fill="#38bdf8", outline="")                   # viewfinder
        cv.create_oval(50, 22, 72, 44, fill="#0b1a33", outline="#4ade80", width=2)        # lens
        cv.create_oval(57, 29, 65, 37, fill="#4ade80", outline="")                        # lens glint
        cv.create_rectangle(38, 12, 48, 18, fill="#fbbf24", outline="")                   # flash

    def _mini_detect(self, cv):
        cv.delete("all")
        cv.create_oval(38, 6, 82, 50, outline="#f87171", width=3)                          # outer ring
        cv.create_oval(48, 16, 72, 40, outline="#38bdf8", width=2)                         # inner ring
        cv.create_line(60, 2, 60, 12, fill="#fbbf24", width=2)
        cv.create_line(60, 44, 60, 54, fill="#fbbf24", width=2)
        cv.create_line(34, 28, 44, 28, fill="#fbbf24", width=2)
        cv.create_line(76, 28, 86, 28, fill="#fbbf24", width=2)
        cv.create_oval(56, 24, 64, 32, fill="#4ade80", outline="")                        # center dot

    def _mini_track(self, cv):
        cv.delete("all")
        cv.create_rectangle(30, 18, 72, 44, fill="#1d4ed8", outline="#38bdf8", width=2)   # cam body
        cv.create_polygon(72, 24, 92, 14, 92, 48, 72, 38, fill="#4ade80", outline="#4ade80")  # lens cone
        cv.create_oval(32, 12, 40, 20, fill="#f87171", outline="")                        # REC dot
        cv.create_text(52, 50, text="REC", fill="#f87171", font=("Arial", 7, "bold"))

    def _mini_match(self, cv):
        cv.delete("all")
        import math
        for x in range(35, 86):
            y1 = 28 + 14 * math.sin((x - 35) / 50 * 6.28)
            y2 = 28 - 14 * math.sin((x - 35) / 50 * 6.28)
            cv.create_oval(x, y1, x + 1, y1 + 1, fill="#38bdf8", outline="")
            cv.create_oval(x, y2, x + 1, y2 + 1, fill="#4ade80", outline="")
        for x in (42, 54, 66, 78):
            y1 = 28 + 14 * math.sin((x - 35) / 50 * 6.28)
            y2 = 28 - 14 * math.sin((x - 35) / 50 * 6.28)
            cv.create_line(x, y1, x, y2, fill="#fbbf24", width=2)

    def _mini_report(self, cv):
        cv.delete("all")
        cv.create_rectangle(44, 8, 76, 50, fill="white", outline="#38bdf8", width=2)      # paper
        cv.create_polygon(66, 8, 76, 18, 66, 18, fill="#38bdf8", outline="")              # folded corner
        for y in (26, 32, 38):
            cv.create_line(50, y, 70, y, fill="#64748b", width=2)
        cv.create_line(50, 44, 62, 44, fill="#4ade80", width=2)
        cv.create_oval(74, 36, 90, 52, fill="#4ade80", outline="")                        # seal
        cv.create_text(82, 44, text="✓", fill="white", font=("Arial", 9, "bold"))

    def _draw_find(self, cv):
        cv.delete("all")
        # rounded person-search badge: aligned box + centered person + lens
        cv.create_rectangle(40, 15, 140, 95, outline="#38bdf8", width=3)
        cv.create_rectangle(112, 24, 132, 32, fill="#4ade80", outline="")          # status tag
        cv.create_oval(80, 28, 100, 48, outline="#4ade80", width=3)                # head
        cv.create_line(90, 48, 90, 68, fill="#4ade80", width=3)                    # body
        cv.create_line(78, 56, 102, 56, fill="#4ade80", width=3)                   # arms
        cv.create_line(90, 68, 81, 84, fill="#4ade80", width=3)
        cv.create_line(90, 68, 99, 84, fill="#4ade80", width=3)
        cv.create_oval(132, 48, 174, 90, outline="#38bdf8", width=3)               # lens
        cv.create_line(167, 83, 188, 102, fill="#38bdf8", width=4)                 # handle

    def _draw_track(self, cv):
        cv.delete("all")
        # straight timeline, 3 evenly spaced camera nodes
        cv.create_line(20, 55, 200, 55, fill="#4ade80", width=2, dash=(5, 4))
        for x, tag, col in [(50, "C1", "#38bdf8"), (110, "C2", "#38bdf8"), (170, "C3", "#4ade80")]:
            cv.create_rectangle(x - 16, 41, x + 16, 59, outline=col, width=3)
            cv.create_oval(x - 4, 47, x + 4, 55, fill=col, outline="")
            cv.create_oval(x - 6, 64, x + 6, 74, fill=col, outline="")
            cv.create_text(x, 84, text=tag, fill="#8a9bb5", font=("Arial", 9))

    def _draw_secure(self, cv):
        cv.delete("all")
        # symmetric shield + tick, aligned document
        cv.create_line(45, 24, 70, 15, fill="#38bdf8", width=3)
        cv.create_line(70, 15, 95, 24, fill="#38bdf8", width=3)
        cv.create_line(95, 24, 95, 58, fill="#38bdf8", width=3)
        cv.create_line(95, 58, 70, 88, fill="#38bdf8", width=3)
        cv.create_line(70, 88, 45, 58, fill="#38bdf8", width=3)
        cv.create_line(45, 58, 45, 24, fill="#38bdf8", width=3)
        cv.create_line(57, 52, 67, 62, fill="#4ade80", width=3)
        cv.create_line(67, 62, 85, 40, fill="#4ade80", width=3)
        cv.create_rectangle(112, 22, 168, 88, outline="#4ade80", width=3)
        for y in (34, 45, 56):
            cv.create_line(121, y, 159, y, fill="#64748b", width=2)
        cv.create_line(121, 72, 149, 72, fill="#4ade80", width=3)


class _BaseSearchPage(ctk.CTkFrame):
    """Shared styled container + AI logic for Live / Video pages."""
    def __init__(self, parent, controller, title="Search"):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller
        self.source_name = title
        self.camera_stream = None
        self.is_running = False

        self.sim_history = [0] * 20
        self.track_scores = {}
        self.matched_ids = set()
        self.id_grace_timers = {}

        self.last_best_score = 0.0
        self.missing_frames = 0

        self.save_dir = "saved_matches"
        os.makedirs(self.save_dir, exist_ok=True)
        self.saved_ids = set()

        # Important session toggle - ON aana pudhu match ellam important-a save aagum
        self.mark_important = False
        self.imp_btn = None

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        top_frame = ctk.CTkFrame(self, fg_color=CARD_BG, corner_radius=12, border_width=1, border_color=CARD_BORDER)
        top_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=6, padx=4)

        self.back_btn = ctk.CTkButton(top_frame, text="← Dashboard", width=130, height=34, fg_color="#243a5e",
                                      hover_color="#2f4d7a", command=lambda: controller.show_frame("DashboardPage"))
        self.back_btn.pack(side="left", padx=10, pady=10)
        ctk.CTkLabel(top_frame, text=title, font=ctk.CTkFont(size=20, weight="bold"), text_color=TITLE_TXT).pack(side="left", padx=16)

        left_frame = ctk.CTkFrame(self, fg_color=CARD_BG, corner_radius=12, border_width=1, border_color=CARD_BORDER)
        left_frame.grid(row=1, column=0, sticky="nsew", padx=4, pady=4)

        self.controls_frame = ctk.CTkFrame(left_frame, fg_color="transparent")
        self.controls_frame.pack(pady=12)

        self.video_label = ctk.CTkLabel(left_frame, text="Upload Image to turn on camera...", fg_color="black",
                                        corner_radius=10)
        self.video_label.pack(fill="both", expand=True, padx=10, pady=10)

        right_frame = ctk.CTkFrame(self, fg_color=CARD_BG, corner_radius=12, width=300,
                                   border_width=1, border_color=CARD_BORDER)
        right_frame.grid(row=1, column=1, sticky="ns", padx=4, pady=4)
        right_frame.grid_propagate(False)

        ctk.CTkLabel(right_frame, text="Live Similarity", font=ctk.CTkFont(size=16), text_color=TITLE_TXT).pack(pady=(18, 4))
        self.sim_label = ctk.CTkLabel(right_frame, text="0.00%", width=200, font=ctk.CTkFont(size=42, weight="bold"), text_color=GREEN)
        self.sim_label.pack(pady=4)
        ctk.CTkLabel(right_frame, text="Match Graph", font=ctk.CTkFont(size=14), text_color=MUTED).pack(pady=(14, 4))

        self.canvas = ctk.CTkCanvas(right_frame, bg="#0b1a33", height=140, width=260, highlightthickness=0)
        self.canvas.pack(pady=4)
        # sync canvas with current theme at creation
        try:
            mode = ctk.get_appearance_mode()
            if mode == "Light":
                self.canvas.configure(bg="#d5dce8")
        except Exception:
            pass

        ctk.CTkLabel(right_frame, text="Enhanced Match Capture", font=ctk.CTkFont(size=14), text_color=TITLE_TXT).pack(pady=(22, 4))
        self.capture_label = ctk.CTkLabel(right_frame, text="👤", font=ctk.CTkFont(size=46), fg_color=CAPTURE_BG, width=140, height=140, corner_radius=10)
        self.capture_label.pack(pady=4)

        self.update_graph()

    # ---------- shared AI pipeline (preserved from V4) ----------
    def _process_and_display(self, frame):
        if self.controller.detector is None or self.controller.face_engine is None:
            self.video_label.configure(image="", text="⚠ AI models not loaded. Check terminal for YOLO/Face errors.")
            return
        detections = self.controller.detector.detect_and_track(frame)
        best_score = 0.0
        current_ids = [track_id for (*_, track_id, _) in detections]

        for tid in list(self.id_grace_timers.keys()):
            if tid not in current_ids:
                self.id_grace_timers[tid] -= 1
                if self.id_grace_timers[tid] <= 0:
                    del self.id_grace_timers[tid]
                    self.track_scores.pop(tid, None)
                    self.matched_ids.discard(tid)
            else:
                self.id_grace_timers[tid] = 30
        for tid in current_ids:
            if tid not in self.id_grace_timers:
                self.id_grace_timers[tid] = 30

        for (x1, y1, x2, y2, track_id, conf) in detections:
            box_color = (0, 0, 255)
            label = f"ID:{track_id} | Unknown"
            smooth_score = 0.0
            if self.controller.target_embedding is not None:
                h, w = frame.shape[:2]
                x1, y1 = max(0, x1), max(0, y1)
                x2, y2 = min(w, x2), min(h, y2)
                if x2 > x1 and y2 > y1:
                    crop = frame[y1:y2, x1:x2]
                    lab = cv2.cvtColor(crop, cv2.COLOR_BGR2LAB)
                    l, a, b = cv2.split(lab)
                    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
                    cl = clahe.apply(l)
                    limg = cv2.merge((cl, a, b))
                    light_corrected = cv2.cvtColor(limg, cv2.COLOR_LAB2BGR)
                    kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
                    enhanced_crop = cv2.filter2D(light_corrected, -1, kernel)
                    face_emb = self.controller.face_engine.get_embedding(enhanced_crop)
                    if face_emb is not None:
                        raw_score = self.controller.face_engine.compare_faces(self.controller.target_embedding, face_emb)
                        if track_id not in self.track_scores:
                            self.track_scores[track_id] = []
                        self.track_scores[track_id].append(raw_score)
                        if len(self.track_scores[track_id]) > 5:
                            self.track_scores[track_id].pop(0)
                        smooth_score = sum(self.track_scores[track_id]) / len(self.track_scores[track_id])
                        if smooth_score > best_score:
                            best_score = smooth_score
                        if smooth_score >= 15:
                            self.matched_ids.add(track_id)
                            crop_rgb = cv2.cvtColor(enhanced_crop, cv2.COLOR_BGR2RGB)
                            pil_crop = Image.fromarray(crop_rgb)
                            ctk_crop = ctk.CTkImage(light_image=pil_crop, dark_image=pil_crop, size=(140, 140))
                            self.capture_label.configure(image=ctk_crop, text="")
                            self.capture_label.image = ctk_crop
                            if track_id not in self.saved_ids:
                                found_at = datetime.now()
                                timestamp = found_at.strftime("%Y-%m-%d_%H-%M-%S")
                                filename = f"match_ID{track_id}_{smooth_score:.1f}pct_{timestamp}.jpg"
                                filepath = os.path.join(self.save_dir, filename)
                                cv2.imwrite(filepath, enhanced_crop)
                                self.saved_ids.add(track_id)
                                # session important ON aana match file-aiyum important mark
                                if self.mark_important:
                                    try:
                                        self.controller.set_important(filename, True)
                                        mp = self.controller.frames.get("MatchesPage")
                                        if mp is not None:
                                            mp.pending_refresh = True
                                    except Exception as e:
                                        print(f"Important mark failed: {e}")
                                try:
                                    self.controller.add_report_record(filepath, track_id, smooth_score, found_at, self.source_name)
                                except Exception as e:
                                    print(f"Report record save failed: {e}")
                                # Matches page auto-refresh ku flag
                                try:
                                    mp = self.controller.frames.get("MatchesPage")
                                    if mp is not None:
                                        mp.pending_refresh = True
                                except Exception:
                                    pass
            if track_id in self.matched_ids:
                if smooth_score >= 15:
                    box_color = (0, 255, 0)
                    label = f"ID:{track_id} | MATCH {smooth_score:.1f}%"
                else:
                    box_color = (0, 165, 255)
                    label = f"ID:{track_id} | TARGET (FACE HIDDEN)"
            cv2.rectangle(frame, (x1, y1), (x2, y2), box_color, 2)
            cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, box_color, 2)

        if best_score > 0:
            self.last_best_score = best_score
            self.missing_frames = 0
        else:
            self.missing_frames += 1
            if self.missing_frames < 15:
                best_score = self.last_best_score
            else:
                self.last_best_score = 0.0
                best_score = 0.0

        is_target_hidden = any(tid in self.matched_ids for tid in current_ids) and best_score < 15
        if best_score >= 15:
            ui_color = GREEN
        elif is_target_hidden:
            ui_color = ORANGE
        else:
            ui_color = RED
        self.sim_label.configure(text=f"{best_score:.2f}%", text_color=ui_color)
        self.sim_history.append(best_score)
        self.sim_history.pop(0)
        self.update_graph()

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(frame_rgb)
        ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=(640, 480))
        self.video_label.configure(image=ctk_img, text="")
        self.video_label.image = ctk_img

    def update_graph(self):
        try:
            self.canvas.delete("all")
            width, height = 260, 140
            for i in range(len(self.sim_history) - 1):
                x1 = int((i / 19) * width)
                y1 = int(height - (self.sim_history[i] / 100) * height)
                x2 = int(((i + 1) / 19) * width)
                y2 = int(height - (self.sim_history[i+1] / 100) * height)
                line_color = GREEN if self.sim_history[i+1] >= self.sim_history[i] else RED
                self.canvas.create_line(x1, y1, x2, y2, fill=line_color, width=2)
        except Exception:
            pass

    def _reset_state(self):
        self.sim_history = [0] * 20
        self.track_scores.clear()
        self.matched_ids.clear()
        self.id_grace_timers.clear()
        self.last_best_score = 0.0
        self.missing_frames = 0
        self.saved_ids.clear()
        self.update_graph()
        self.sim_label.configure(text="0.00%", text_color=GREEN)
        self.capture_label.configure(image="", text="👤")

    # ---- Important toggle (shared by Live Camera + Video Search) ----
    def _add_important_button(self, parent, padx=8):
        self.imp_btn = ctk.CTkButton(
            parent, text="☆ Important", height=38, width=140,
            fg_color="transparent", hover_color="#d68910",
            border_width=1, border_color=BORDER, text_color=TITLE_TXT,
            command=self._toggle_important_mode,
        )
        self.imp_btn.pack(side="left", padx=padx)
        return self.imp_btn

    def _toggle_important_mode(self):
        self.mark_important = not self.mark_important
        if self.mark_important:
            self.imp_btn.configure(text="⭐ Important ON", fg_color=ORANGE,
                                   hover_color="#d68910", border_width=0,
                                   text_color="#0a1428")
        else:
            self.imp_btn.configure(text="☆ Important", fg_color="transparent",
                                   hover_color="#d68910", border_width=1,
                                   border_color=BORDER, text_color=TITLE_TXT)


class LiveCameraPage(_BaseSearchPage):
    def __init__(self, parent, controller):
        super().__init__(parent, controller, title="Live Cameras")
        self.upload_btn = ctk.CTkButton(self.controls_frame, text="⬆ Upload Target Image", height=38, width=200,
                                        fg_color=ACCENT, hover_color=ACCENT_HOVER, command=self.upload_image)
        self.upload_btn.pack(side="left", padx=8)
        self.stop_btn = ctk.CTkButton(self.controls_frame, text="⏹ Stop Camera", height=38, width=150,
                                      command=self.stop_camera, state="disabled", fg_color=RED, hover_color="#c0392b")
        self.stop_btn.pack(side="left", padx=8)
        self._add_important_button(self.controls_frame)

    def upload_image(self):
        file_path = filedialog.askopenfilename(title="Select Target Image", filetypes=[("Image Files", "*.jpg *.jpeg *.png")])
        if file_path:
            target_img = cv2.imread(file_path)
            if target_img is not None:
                self.controller.target_embedding = self.controller.face_engine.get_embedding(target_img)
                if self.controller.target_embedding is not None:
                    self.controller.set_target_image(file_path)
                    self.upload_btn.configure(text="✅ Target Face Set", fg_color="#27ae60")
                    self.start_camera()
                else:
                    self.upload_btn.configure(text="❌ No Face Found!", fg_color="red")

    def start_camera(self):
        self.video_label.configure(image="", text="Starting Camera...")
        self._reset_state()
        self.upload_btn.configure(state="disabled")
        self.stop_btn.configure(state="normal")
        if self.camera_stream is None:
            self.camera_stream = CameraStream(0)
        self.is_running = True
        try:
            self.controller.set_camera_count(1)
        except Exception:
            pass
        self.update_frame()

    def update_frame(self):
        if not self.is_running:
            return
        try:
            ret, frame = self.camera_stream.get_frame()
            if not ret:
                self.after(30, self.update_frame)
                return
            self._process_and_display(frame)
        except Exception as e:
            print(f"Camera Error: {e}")
        self.after(30, self.update_frame)

    def stop_camera(self):
        self.is_running = False
        if self.camera_stream:
            try:
                self.camera_stream.release()
            except Exception:
                pass
            self.camera_stream = None
        try:
            self.controller.set_camera_count(0)
        except Exception:
            pass
        try:
            self.video_label.configure(image="", text="Camera Stopped. Please upload a Target to start again.")
            self.upload_btn.configure(text="⬆ Upload Target Image", fg_color=ACCENT, state="normal")
            self.stop_btn.configure(state="disabled")
            self._reset_state()
        except Exception:
            pass


class VideoSearchPage(_BaseSearchPage):
    def __init__(self, parent, controller):
        super().__init__(parent, controller, title="Video Search")
        self.video_cap = None
        self.controls_frame.pack_forget()
        self.vid_controls_frame = ctk.CTkFrame(self.video_label.master, fg_color="transparent")
        self.vid_controls_frame.pack(pady=10, before=self.video_label)
        self.target_btn = ctk.CTkButton(self.vid_controls_frame, text="1. ⬆ Target Image", height=38, width=150,
                                        fg_color=ACCENT, hover_color=ACCENT_HOVER, command=self.upload_target)
        self.target_btn.pack(side="left", padx=5)
        self.video_btn = ctk.CTkButton(self.vid_controls_frame, text="2. 🎬 Select Video", height=38, width=150,
                                       command=self.upload_video, state="disabled")
        self.video_btn.pack(side="left", padx=5)
        self.stop_video_btn = ctk.CTkButton(self.vid_controls_frame, text="⏹ Stop Video", height=38, width=130,
                                            command=self.stop_video, state="disabled", fg_color=RED, hover_color="#c0392b")
        self.stop_video_btn.pack(side="left", padx=5)
        self._add_important_button(self.vid_controls_frame, padx=5)
        self.video_label.configure(text="Upload Target and Video to begin search...")

    def upload_target(self):
        file_path = filedialog.askopenfilename(title="Select Target Image", filetypes=[("Image Files", "*.jpg *.jpeg *.png")])
        if file_path:
            target_img = cv2.imread(file_path)
            if target_img is not None:
                self.controller.target_embedding = self.controller.face_engine.get_embedding(target_img)
                if self.controller.target_embedding is not None:
                    self.controller.set_target_image(file_path)
                    self.target_btn.configure(text="✅ Target Set", fg_color="#27ae60")
                    self.video_btn.configure(state="normal", fg_color=ACCENT)
                else:
                    self.target_btn.configure(text="❌ No Face Found!", fg_color="red")

    def upload_video(self):
        file_path = filedialog.askopenfilename(title="Select Video File", filetypes=[("Video Files", "*.mp4 *.avi *.mkv")])
        if file_path:
            self.video_btn.configure(text="✅ Video Loaded", fg_color="#27ae60")
            self.start_video(file_path)

    def start_video(self, path):
        self.stop_video()
        self._reset_state()
        self.target_btn.configure(state="disabled")
        self.video_btn.configure(state="disabled")
        self.stop_video_btn.configure(state="normal")
        self.video_cap = cv2.VideoCapture(path)
        self.is_running = True
        self.update_video_frame()

    def update_video_frame(self):
        if not self.is_running or not self.video_cap:
            return
        ret, frame = self.video_cap.read()
        if ret:
            self._process_and_display(frame)
            self.after(30, self.update_video_frame)
        else:
            self.is_running = False
            if self.video_cap:
                self.video_cap.release()
                self.video_cap = None
            self.video_label.configure(image="", text="🎬 Video Processing Completed!")
            self.target_btn.configure(text="1. ⬆ Target Image", fg_color=ACCENT, state="normal")
            self.video_btn.configure(text="2. 🎬 Select Video", fg_color=ACCENT, state="disabled")
            self.stop_video_btn.configure(state="disabled")

    def stop_video(self):
        self.is_running = False
        if getattr(self, "video_cap", None):
            try:
                self.video_cap.release()
            except Exception:
                pass
            self.video_cap = None
        try:
            self.video_label.configure(image="", text="Upload Target and Video to begin search...")
            self.target_btn.configure(text="1. ⬆ Target Image", fg_color=ACCENT, state="normal")
            self.video_btn.configure(text="2. 🎬 Select Video", fg_color=ACCENT, state="disabled")
            self.stop_video_btn.configure(state="disabled")
            self._reset_state()
        except Exception:
            pass

    def stop_camera(self):
        pass


class MatchesPage(ctk.CTkFrame):
    """Sidebar 'Matches' - match aana pictures time-oda gallery."""
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller
        base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.save_dir = os.path.join(base, "saved_matches")
        os.makedirs(self.save_dir, exist_ok=True)
        self.pending_refresh = False
        self._imgs = []

        header = ctk.CTkFrame(self, fg_color=CARD, corner_radius=12, border_width=1, border_color=BORDER)
        header.pack(fill="x", padx=4, pady=6)
        ctk.CTkLabel(header, text="✔ Matches", font=ctk.CTkFont(size=20, weight="bold"), text_color=TITLE_TXT).pack(side="left", padx=16, pady=12)
        self.count_label = ctk.CTkLabel(header, text="0 photos", font=ctk.CTkFont(size=13), text_color=MUTED_TXT)
        self.count_label.pack(side="left", padx=8)
        ctk.CTkButton(header, text="⟳ Refresh", width=110, height=32, fg_color=ACCENT, hover_color=ACCENT_HOVER,
                      command=self.refresh).pack(side="right", padx=(6, 6), pady=10)
        ctk.CTkButton(header, text="📁 Open Folder", width=120, height=32, fg_color="#243a5e", hover_color="#2f4d7a",
                      command=self.open_folder).pack(side="right", padx=6, pady=10)

        ctk.CTkLabel(self, text="Match aana photo + time inga auto-save aagum. Live / Video search la match vantha udane inga varum.",
                     font=ctk.CTkFont(size=12), text_color=MUTED_TXT).pack(anchor="w", padx=10, pady=(0, 4))

        self.scroll = ctk.CTkScrollableFrame(self, fg_color=CARD, corner_radius=12, border_width=1, border_color=BORDER)
        self.scroll.pack(fill="both", expand=True, padx=4, pady=4)
        self.refresh()

    def _parse(self, fname):
        # new: match_ID2_87.5pct_2026-09-22_15-57-01.jpg | old: match_ID2_2026-09-22_15-57-01.jpg
        import re
        m = re.match(r"match_ID(\d+)_(?:([\d.]+)pct_)?(\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2})", fname)
        if not m:
            return None
        tid, score, ts = m.groups()
        pretty = ts.replace("_", " ").replace("-", ":", 2) if False else ts  # keep raw below
        # 2026-09-22_15-57-01 -> 2026-09-22 15:57:01
        try:
            d_part, t_part = ts.split("_")
            pretty = f"{d_part} {t_part.replace('-', ':')}"
        except Exception:
            pretty = ts
        return {"id": tid, "score": score, "time": pretty, "raw_ts": ts}

    def refresh(self):
        for w in self.scroll.winfo_children():
            w.destroy()
        self._imgs = []
        try:
            files = [f for f in os.listdir(self.save_dir) if f.lower().endswith((".jpg", ".jpeg", ".png"))]
        except Exception:
            files = []
        # latest first - filename timestamp sort
        files.sort(reverse=True)
        self.count_label.configure(text=f"{len(files)} photos")
        self.pending_refresh = False
        if not files:
            ctk.CTkLabel(self.scroll, text="Innum match illa. Live Camera / Video Search run pannunga.",
                         font=ctk.CTkFont(size=13), text_color=MUTED_TXT).pack(pady=30)
            return
        for fname in files:
            info = self._parse(fname)
            fpath = os.path.join(self.save_dir, fname)
            row = ctk.CTkFrame(self.scroll, fg_color="transparent", border_width=1, border_color=BORDER, corner_radius=10)
            row.pack(fill="x", padx=8, pady=6)
            try:
                pil = Image.open(fpath)
                pil.thumbnail((140, 140))
                cimg = ctk.CTkImage(light_image=pil, dark_image=pil, size=pil.size)
                il = ctk.CTkLabel(row, image=cimg, text="")
                il.image = cimg
                self._imgs.append(cimg)
                il.pack(side="left", padx=10, pady=10)
            except Exception:
                ctk.CTkLabel(row, text="🖼", font=ctk.CTkFont(size=40)).pack(side="left", padx=10, pady=10)
            txt = fname
            if info:
                score_txt = f"{float(info['score']):.1f}% match" if info["score"] else "match"
                txt = f"Track ID: {info['id']}\n{score_txt}\n🕒 {info['time']}\n{fname}"
            else:
                try:
                    mt = datetime.fromtimestamp(os.path.getmtime(fpath)).strftime("%Y-%m-%d %H:%M:%S")
                    txt = f"🕒 {mt}\n{fname}"
                except Exception:
                    pass
            ctk.CTkLabel(row, text=txt, font=ctk.CTkFont(size=12), text_color=TITLE_TXT, justify="left").pack(side="left", padx=10, pady=10)
            # ---- Important toggle (single indicator: button mattum) ----
            imp_key = fname
            imp = self.controller.is_important(imp_key)
            if imp:
                row.configure(border_width=2, border_color=ORANGE)
            star_txt = "⭐ Important" if imp else "☆ Important"
            star_btn = ctk.CTkButton(
                row, text=star_txt, width=110, height=30,
                fg_color=(ORANGE if imp else "transparent"),
                hover_color="#d68910",
                border_width=(0 if imp else 1),
                border_color=BORDER,
                text_color=("#0a1428" if imp else TITLE_TXT),
                command=lambda p=imp_key: self.toggle_important(p),
            )
            star_btn.pack(side="right", padx=6)
            ctk.CTkButton(row, text="🗑", width=44, fg_color="transparent", hover_color="#5a1f1f", text_color="#e74c3c",
                          command=lambda p=fpath: self.delete_one(p)).pack(side="right", padx=10)

    def toggle_important(self, key):
        self.controller.toggle_important(key)
        self.refresh()

    def delete_one(self, path):
        try:
            os.remove(path)
        except Exception as e:
            print(f"Delete failed: {e}")
        self.refresh()

    def open_folder(self):
        import subprocess, sys
        try:
            if sys.platform.startswith("win"):
                os.startfile(self.save_dir)
            elif sys.platform == "darwin":
                subprocess.Popen(["open", self.save_dir])
            else:
                subprocess.Popen(["xdg-open", self.save_dir])
        except Exception as e:
            print(f"Open folder failed: {e}")


import os
from fpdf import FPDF

class ReportPage(ctk.CTkFrame):
    """Report page: target image + found image + found timing + PDF export."""
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller
        self.pending_refresh = False
        self._imgs = []
        self._selected = set()

        header = ctk.CTkFrame(self, fg_color=CARD_BG, corner_radius=14, border_width=1, border_color=CARD_BORDER)
        header.pack(fill="x", padx=4, pady=6)
        ctk.CTkLabel(header, text="Report", font=ctk.CTkFont(size=22, weight="bold"), text_color=TITLE_TXT).pack(side="left", padx=16, pady=12)
        self.count_label = ctk.CTkLabel(header, text="0 records", font=ctk.CTkFont(size=13), text_color=MUTED_TXT)
        self.count_label.pack(side="left", padx=10)
        ctk.CTkButton(header, text="🗑 Delete Selected", width=140, fg_color="#e74c3c", hover_color="#c0392b",
                      command=self.delete_selected).pack(side="right", padx=8, pady=10)
        ctk.CTkButton(header, text="📄 Generate PDF", fg_color=ACCENT, hover_color=ACCENT_HOVER,
                      command=self.generate_report).pack(side="right", padx=6, pady=10)
        ctk.CTkButton(header, text="⟳ Refresh", fg_color="#243a5e", hover_color="#2f4d7a",
                      command=self.refresh).pack(side="right", padx=6, pady=10)

        # Select All row
        select_row = ctk.CTkFrame(self, fg_color="transparent")
        select_row.pack(fill="x", padx=10, pady=(0, 4))
        self._select_all_var = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(select_row, text="Select All", variable=self._select_all_var,
                        command=self.toggle_select_all).pack(side="left")
        self._selected_label = ctk.CTkLabel(select_row, text="0 selected", font=ctk.CTkFont(size=12), text_color=MUTED_TXT)
        self._selected_label.pack(side="left", padx=10)

        ctk.CTkLabel(self, text="Live Camera / Video Search la target find aana udane: target image, found image, timing inga varum.",
                     font=ctk.CTkFont(size=12), text_color=MUTED_TXT).pack(anchor="w", padx=10, pady=(0, 4))

        self.scroll = ctk.CTkScrollableFrame(self, fg_color=CARD_BG, corner_radius=14, border_width=1, border_color=CARD_BORDER)
        self.scroll.pack(fill="both", expand=True, padx=4, pady=4)
        self.refresh()

    def _records(self):
        return self.controller._load_report_records()

    def refresh(self):
        for w in self.scroll.winfo_children():
            w.destroy()
        self._imgs = []
        records = self._records()
        self.count_label.configure(text=f"{len(records)} records")
        self.pending_refresh = False
        if not records:
            ctk.CTkLabel(self.scroll, text="Innum report data illa. Live Camera / Video Search la target find pannunga.",
                         text_color=MUTED_TXT, font=ctk.CTkFont(size=13)).pack(pady=35)
            return
        for rec in records:
            row = ctk.CTkFrame(self.scroll, fg_color="transparent", border_width=1,
                               border_color=BORDER, corner_radius=12)
            row.pack(fill="x", padx=10, pady=8)

            # Checkbox for selection
            key = self._key(rec)
            var = ctk.BooleanVar(value=key in self._selected)
            cb = ctk.CTkCheckBox(row, text="", variable=var, width=30,
                                 command=lambda k=key, v=var: self._toggle_select(k, v))
            cb.pack(side="left", padx=(10, 0), pady=12)

            self._image_box(row, rec.get("target_image"), "Target Person")
            self._image_box(row, rec.get("match_image"), "Found Picture")

            score = rec.get("score", 0)
            info = (
                f"Track ID: {rec.get('track_id', '-') }\n"
                f"Match: {score}%\n"
                f"Found Time: {rec.get('found_at', '-') }\n"
                f"Source: {rec.get('source', '-') }"
            )
            ctk.CTkLabel(row, text=info, font=ctk.CTkFont(size=13), text_color=TITLE_TXT,
                         justify="left").pack(side="left", padx=16, pady=12, fill="x", expand=True)

            ctk.CTkButton(row, text="PDF", width=70, fg_color=ACCENT, hover_color=ACCENT_HOVER,
                          command=lambda r=rec: self.generate_report([r])).pack(side="right", padx=10)

    def _key(self, rec):
        """Shared important key with Matches page = match image basename."""
        mi = rec.get("match_image")
        return os.path.basename(mi) if mi else rec.get("id", "")

    def _toggle_select(self, key, var):
        if var.get():
            self._selected.add(key)
        else:
            self._selected.discard(key)
        self._selected_label.configure(text=f"{len(self._selected)} selected")

    def toggle_select_all(self):
        select_all = self._select_all_var.get()
        self._selected.clear()
        if select_all:
            for rec in self._records():
                self._selected.add(self._key(rec))
        self._selected_label.configure(text=f"{len(self._selected)} selected")
        self.refresh()

    def delete_selected(self):
        if not self._selected:
            return
        import tkinter.messagebox as mb
        if not mb.askyesno("Delete", f"Delete {len(self._selected)} selected records?"):
            return
        records = self._records()
        remaining = [r for r in records if self._key(r) not in self._selected]
        self.controller._save_report_records(remaining)
        self._selected.clear()
        self._select_all_var.set(False)
        self.refresh()

    def _image_box(self, parent, path, title):
        box = ctk.CTkFrame(parent, fg_color="transparent")
        box.pack(side="left", padx=10, pady=10)
        ctk.CTkLabel(box, text=title, font=ctk.CTkFont(size=11, weight="bold"), text_color=MUTED_TXT).pack()
        try:
            if path and os.path.isfile(path):
                img = Image.open(path).convert("RGB")
                img.thumbnail((120, 120), Image.LANCZOS)
                cimg = ctk.CTkImage(light_image=img, dark_image=img, size=img.size)
                self._imgs.append(cimg)
                ctk.CTkLabel(box, image=cimg, text="", fg_color=CANVAS_BG, width=128, height=128, corner_radius=10).pack(pady=4)
                return
        except Exception as e:
            print(f"Report image load failed: {e}")
        ctk.CTkLabel(box, text="No Image", fg_color=CANVAS_BG, text_color=MUTED_TXT,
                     width=128, height=128, corner_radius=10).pack(pady=4)

    def generate_report(self, records=None):
        """Create PDF using Pillow only: centered logo + target/found images + timing."""
        from tkinter import filedialog, messagebox
        from PIL import ImageDraw, ImageFont, ImageOps

        records = records or self._records()
        if not records:
            messagebox.showwarning("No Report Data", "Report generate panna match data illa.")
            return
        out = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF Files", "*.pdf")],
            initialfile=f"SmartFind_AI_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        )
        if not out:
            return

        pages = []
        for rec in records:
            pages.append(self._make_pdf_page(rec))
        try:
            pages[0].save(out, "PDF", save_all=True, append_images=pages[1:], resolution=100.0)
            messagebox.showinfo("Report Generated", f"PDF report generated successfully!\n{out}")
        except Exception as e:
            messagebox.showerror("PDF Error", f"PDF generate failed:\n{e}")

    def generate_auto_pdf(self, record):
        """Automatically save a one-match PDF without asking location."""
        try:
            out_dir = os.path.join(self.controller._base_dir(), "reports", "auto_pdfs")
            os.makedirs(out_dir, exist_ok=True)
            safe_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            track_id = record.get("track_id", "unknown")
            out = os.path.join(out_dir, f"match_report_ID{track_id}_{safe_time}.pdf")
            page = self._make_pdf_page(record)
            page.save(out, "PDF", resolution=100.0)
            print(f"Auto PDF saved: {out}")
            return out
        except Exception as e:
            print(f"Auto PDF save failed: {e}")
            return None

    def _make_pdf_page(self, rec):
        from PIL import ImageDraw, ImageFont, ImageOps
        W, H = 1240, 1754  # A4-ish at 150 dpi
        page = Image.new("RGB", (W, H), "white")
        draw = ImageDraw.Draw(page)
        try:
            title_font = ImageFont.truetype("arialbd.ttf", 42)
            h_font = ImageFont.truetype("arialbd.ttf", 28)
            body_font = ImageFont.truetype("arial.ttf", 24)
            small_font = ImageFont.truetype("arial.ttf", 20)
        except Exception:
            title_font = h_font = body_font = small_font = ImageFont.load_default()

        # Center logo
        logo_path = os.path.join(self.controller._base_dir(), "assets", "logo.png")
        if os.path.isfile(logo_path):
            logo = Image.open(logo_path).convert("RGB")
            logo = ImageOps.contain(logo, (260, 180))
            page.paste(logo, ((W - logo.width) // 2, 55))

        draw.text((W // 2, 260), "SmartFind AI - Match Report", fill=(10, 20, 40), font=title_font, anchor="mm")
        draw.line((90, 310, W - 90, 310), fill=(47, 128, 237), width=4)

        # Important = corner-la chinna star mattum (big stamp illa)
        if self.controller.is_important(self._key(rec)):
            import math
            cx, cy, R, r = W - 78, 78, 26, 11
            pts = []
            for i in range(10):
                ang = -math.pi / 2 + i * math.pi / 5
                rad = R if i % 2 == 0 else r
                pts.append((cx + rad * math.cos(ang), cy + rad * math.sin(ang)))
            draw.polygon(pts, fill=(243, 156, 18), outline=(217, 136, 12))

        draw.text((110, 360), f"Report ID: {rec.get('id', '-')}", fill=(20, 30, 50), font=body_font)
        draw.text((110, 400), f"Found Time: {rec.get('found_at', '-')}", fill=(20, 30, 50), font=body_font)
        draw.text((110, 440), f"Source: {rec.get('source', '-')}", fill=(20, 30, 50), font=body_font)
        draw.text((110, 480), f"Track ID: {rec.get('track_id', '-')}    Match: {rec.get('score', '-')}%", fill=(20, 30, 50), font=body_font)

        # Image cards
        self._draw_pdf_image_card(page, draw, rec.get("target_image"), 110, 580, "Target Person Image", h_font, small_font)
        self._draw_pdf_image_card(page, draw, rec.get("match_image"), 650, 580, "Found Picture", h_font, small_font)

        draw.line((90, H - 130, W - 90, H - 130), fill=(220, 226, 235), width=2)
        draw.text((W // 2, H - 85), "Generated by SmartFind AI • Find • Track • Secure", fill=(90, 100, 120), font=small_font, anchor="mm")
        draw.text((W // 2, H - 55), datetime.now().strftime("Generated: %Y-%m-%d %H:%M:%S"), fill=(90, 100, 120), font=small_font, anchor="mm")
        return page

    def _draw_pdf_image_card(self, page, draw, path, x, y, title, title_font, small_font):
        from PIL import ImageOps
        draw.rounded_rectangle((x, y, x + 480, y + 600), radius=24, outline=(210, 222, 235), width=3, fill=(247, 250, 252))
        draw.text((x + 240, y + 40), title, fill=(15, 32, 60), font=title_font, anchor="mm")
        if path and os.path.isfile(path):
            try:
                img = Image.open(path).convert("RGB")
                img = ImageOps.contain(img, (400, 420))
                page.paste(img, (x + 40 + (400 - img.width) // 2, y + 90 + (420 - img.height) // 2))
                draw.text((x + 240, y + 545), os.path.basename(path), fill=(90, 100, 120), font=small_font, anchor="mm")
                return
            except Exception as e:
                print(f"PDF image failed: {e}")
        draw.text((x + 240, y + 300), "No Image", fill=(120, 130, 145), font=title_font, anchor="mm")


class SettingsPage(ctk.CTkFrame):
    """Professional settings: section cards + system status + appearance + alerts."""
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller
        self._imgs = []

        outer = ctk.CTkScrollableFrame(self, fg_color="transparent")
        outer.pack(fill="both", expand=True, padx=4, pady=6)

        # ---- Header ----
        head = ctk.CTkFrame(outer, fg_color=CARD, corner_radius=14, border_width=1, border_color=BORDER)
        head.pack(fill="x", pady=(0, 10))
        ctk.CTkLabel(head, text="⚙  Settings", font=ctk.CTkFont(size=24, weight="bold"),
                     text_color=TITLE_TXT).pack(anchor="w", padx=22, pady=(18, 2))
        ctk.CTkLabel(head, text="SmartFind AI V5.0 — Appearance, alerts aur system status manage pannunga.",
                     font=ctk.CTkFont(size=13), text_color=MUTED_TXT).pack(anchor="w", padx=22, pady=(0, 18))

        # ---- Section: Appearance ----
        sec1 = self._section(outer, "🎨  Appearance", "Dark / Light mode — full UI color maarum")
        self.theme_switch = ctk.CTkSegmentedButton(sec1, values=["Dark", "Light"],
                                                   command=self.on_theme_change,
                                                   selected_color=ACCENT,
                                                   selected_hover_color=ACCENT_HOVER,
                                                   unselected_color=CARD,
                                                   unselected_hover_color=BORDER,
                                                   text_color=TITLE_TXT,
                                                   font=ctk.CTkFont(size=14, weight="bold"),
                                                   width=260, height=34)
        try:
            self.theme_switch.set(controller.current_theme)
        except Exception:
            self.theme_switch.set("Dark")
        self.theme_switch.pack(anchor="w", padx=22, pady=(0, 6))
        cur = controller.current_theme
        self.status_label = ctk.CTkLabel(sec1,
                                         text=f"Current: {cur} mode",
                                         font=ctk.CTkFont(size=12), text_color=MUTED_TXT)
        self.status_label.pack(anchor="w", padx=22, pady=(0, 16))

        # ---- Section: Alerts & Reports ----
        sec2 = self._section(outer, "🔔  Alerts & Reports", "Target found aana udane enna nadakum nu settings")

        self.auto_pdf_switch = self._switch_row(
            sec2,
            "Automatically PDF download",
            "Match found aana odane PDF auto-a reports/auto_pdfs/ la save aagum",
            controller.auto_pdf_enabled,
            self.on_auto_pdf_toggle,
        )
        self._divider(sec2)

        self.sound_switch = self._switch_row(
            sec2,
            "Sound alert on match",
            "Target found aana podhu beep sound varum",
            controller.sound_enabled,
            self.on_sound_toggle,
        )
        sec2.pack_configure(pady=(0, 10))

        # ---- Section: System Status ----
        sec3 = self._section(outer, "🖥  System Status", "AI backend + threshold info")
        grid = ctk.CTkFrame(sec3, fg_color="transparent")
        grid.pack(fill="x", padx=18, pady=(0, 8))
        grid.grid_columnconfigure((0, 1, 2), weight=1)
        self._stat_card(grid, 0, "YOLOv11", "Person Detect + Track", controller.yolo_ok)
        self._stat_card(grid, 1, "ArcFace", "Face Embedding 512-d", controller.face_ok)
        self._stat_card(grid, 2, "Cameras", f"{controller.cameras_connected} connected", controller.cameras_connected > 0)

        ctk.CTkLabel(sec3,
                     text="Thresholds (config.py):  FACE 0.6  |  ReID 0.7  |  Blur 100.0  |  Match score ≥ 15%",
                     font=ctk.CTkFont(size=12), text_color=MUTED_TXT).pack(anchor="w", padx=22, pady=(2, 16))

    # ---------- helpers ----------
    def _section(self, parent, title, subtitle):
        box = ctk.CTkFrame(parent, fg_color=CARD, corner_radius=14, border_width=1, border_color=BORDER)
        box.pack(fill="x", pady=(0, 10))
        ctk.CTkLabel(box, text=title, font=ctk.CTkFont(size=16, weight="bold"),
                     text_color=TITLE_TXT).pack(anchor="w", padx=22, pady=(16, 0))
        ctk.CTkLabel(box, text=subtitle, font=ctk.CTkFont(size=12),
                     text_color=MUTED_TXT).pack(anchor="w", padx=22, pady=(2, 10))
        return box

    def _divider(self, parent):
        ctk.CTkFrame(parent, fg_color=BORDER, height=1).pack(fill="x", padx=22, pady=4)

    def _switch_row(self, parent, title, desc, enabled, command):
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", padx=18, pady=8)
        txt = ctk.CTkFrame(row, fg_color="transparent")
        txt.pack(side="left", fill="x", expand=True)
        ctk.CTkLabel(txt, text=title, font=ctk.CTkFont(size=14, weight="bold"),
                     text_color=TITLE_TXT).pack(anchor="w")
        ctk.CTkLabel(txt, text=desc, font=ctk.CTkFont(size=11),
                     text_color=MUTED_TXT).pack(anchor="w")
        sw = ctk.CTkSwitch(row, text="", command=command,
                           progress_color=ACCENT, button_color="white",
                           width=44)
        sw.pack(side="right", padx=6)
        if enabled:
            sw.select()
        return sw

    def _stat_card(self, parent, col, title, desc, ok):
        card = ctk.CTkFrame(parent, fg_color=BG, corner_radius=10, border_width=1, border_color=BORDER)
        card.grid(row=0, column=col, sticky="ew", padx=4, pady=4)
        top = ctk.CTkFrame(card, fg_color="transparent")
        top.pack(fill="x", padx=12, pady=(10, 0))
        ctk.CTkLabel(top, text=title, font=ctk.CTkFont(size=14, weight="bold"),
                     text_color=TITLE_TXT).pack(side="left")
        dot = "🟢" if ok else "🔴"
        ctk.CTkLabel(top, text=dot, font=ctk.CTkFont(size=13)).pack(side="right")
        ctk.CTkLabel(card, text=desc, font=ctk.CTkFont(size=11),
                     text_color=MUTED_TXT).pack(anchor="w", padx=12, pady=(2, 10))

    def on_theme_change(self, mode):
        self.controller.set_theme(mode)
        if mode == "Light":
            self.status_label.configure(text="Current: Light mode — soft grey-blue (no over-bright)")
        else:
            self.status_label.configure(text="Current: Dark mode")

    def on_auto_pdf_toggle(self):
        self.controller.auto_pdf_enabled = bool(self.auto_pdf_switch.get())
        self.controller.save_app_settings()

    def on_sound_toggle(self):
        self.controller.sound_enabled = bool(self.sound_switch.get())
        self.controller.save_app_settings()
        if self.controller.sound_enabled:
            self.controller.play_match_sound()


# Backward compat: old HomeDashboard name
HomeDashboard = DashboardPage
