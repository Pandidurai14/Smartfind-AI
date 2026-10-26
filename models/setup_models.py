import os
import urllib.request

base_dir = os.path.dirname(os.path.abspath(__file__))

# Folders path setup
folders = {
    "yolo": os.path.join(base_dir, "yolo"),
    "face": os.path.join(base_dir, "face"),
    "reid": os.path.join(base_dir, "reid")
}

# Auto-create sub-folders
for name, path in folders.items():
    os.makedirs(path, exist_ok=True)

# Download function
def download_model(url, save_path):
    if not os.path.exists(save_path):
        print(f"Downloading {save_path.split('/')[-1]}...")
        urllib.request.urlretrieve(url, save_path)
        print("Download Completed!")
    else:
        print(f"{save_path.split('/')[-1]} already exists.")

# Download YOLOv11 weights mattum
try:
    download_model(
        "https://github.com/ultralytics/assets/releases/download/v8.3.0/yolo11n.pt",
        os.path.join(folders["yolo"], "yolo11n.pt")
    )
except Exception as e:
    print(f"YOLO download error: {e}")

print("Setup Finished! OSNet and Face models will auto-download during AI runtime.")