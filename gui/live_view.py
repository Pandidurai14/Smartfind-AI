import customtkinter as ctk
from PIL import Image
import cv2

class LiveViewFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        
        self.video_label = ctk.CTkLabel(self, text="")
        self.video_label.pack(pady=10, padx=10, fill="both", expand=True)
        
        self.stats_frame = ctk.CTkFrame(self, height=50)
        self.stats_frame.pack(fill="x", padx=10, pady=10)
        
        self.track_label = ctk.CTkLabel(self.stats_frame, text="Current ID: None", font=ctk.CTkFont(size=14))
        self.track_label.pack(side="left", padx=20, pady=10)
        
        self.match_label = ctk.CTkLabel(self.stats_frame, text="Match: 0%", font=ctk.CTkFont(size=14))
        self.match_label.pack(side="left", padx=20, pady=10)

    def update_frame(self, cv_image):
        cv_image = cv2.cvtColor(cv_image, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(cv_image)
        ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=(640, 480))
        self.video_label.configure(image=ctk_img)
        self.video_label.image = ctk_img

    def update_stats(self, track_id, match_score):
        self.track_label.configure(text=f"Current ID: {track_id}")
        self.match_label.configure(text=f"Match: {match_score}%")