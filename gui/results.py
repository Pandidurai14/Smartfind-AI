import customtkinter as ctk
from PIL import Image

class ResultsFrame(ctk.CTkScrollableFrame):
    def __init__(self, master):
        super().__init__(master)
        
        self.title_label = ctk.CTkLabel(self, text="Match Results", font=ctk.CTkFont(size=20, weight="bold"))
        self.title_label.pack(pady=20)
        
        self.results_container = ctk.CTkFrame(self)
        self.results_container.pack(fill="both", expand=True, padx=10, pady=10)

    def add_result(self, image_path, track_id, score, status):
        result_box = ctk.CTkFrame(self.results_container)
        result_box.pack(fill="x", pady=5, padx=5)
        
        img = Image.open(image_path)
        ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=(100, 100))
        
        img_label = ctk.CTkLabel(result_box, image=ctk_img, text="")
        img_label.image = ctk_img
        img_label.pack(side="left", padx=10, pady=10)
        
        info_label = ctk.CTkLabel(result_box, text=f"Track ID: {track_id}\nScore: {score}%\nStatus: {status}", justify="left")
        info_label.pack(side="left", padx=20, pady=10)