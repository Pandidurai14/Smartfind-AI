import customtkinter as ctk
from tkinter import filedialog
from PIL import Image

class UploadFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        
        self.target_image_path = None
        self.input_source = ctk.IntVar(value=0)
        
        self.title_label = ctk.CTkLabel(self, text="Target Person Setup", font=ctk.CTkFont(size=20, weight="bold"))
        self.title_label.pack(pady=20)
        
        self.upload_btn = ctk.CTkButton(self, text="Select Target Image", command=self.select_image)
        self.upload_btn.pack(pady=10)
        
        self.image_label = ctk.CTkLabel(self, text="No Image Selected")
        self.image_label.pack(pady=10)
        
        self.source_label = ctk.CTkLabel(self, text="Select Input Source:", font=ctk.CTkFont(size=16))
        self.source_label.pack(pady=20)
        
        self.radio_live = ctk.CTkRadioButton(self, text="Live Camera", variable=self.input_source, value=0)
        self.radio_live.pack(pady=5)
        
        self.radio_video = ctk.CTkRadioButton(self, text="Upload Video", variable=self.input_source, value=1)
        self.radio_video.pack(pady=5)
        
        self.start_btn = ctk.CTkButton(self, text="START SEARCH", fg_color="green", font=ctk.CTkFont(weight="bold"))
        self.start_btn.pack(pady=30)

    def select_image(self):
        path = filedialog.askopenfilename(filetypes=[("Images", "*.jpg *.png *.jpeg")])
        if path:
            self.target_image_path = path
            self.image_label.configure(text=f"Selected: {path.split('/')[-1]}")