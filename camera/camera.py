import cv2
from .camera_config import CameraConfig

class CameraStream:
    def __init__(self, source=None):
        self.source = source if source is not None else CameraConfig.DEFAULT_LIVE_SOURCE
        self.cap = cv2.VideoCapture(self.source)
        
        if isinstance(self.source, int):
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, CameraConfig.FRAME_WIDTH)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CameraConfig.FRAME_HEIGHT)
            self.cap.set(cv2.CAP_PROP_FPS, CameraConfig.TARGET_FPS)
            
        if not self.cap.isOpened():
            print(f"Warning: Failed to open source {self.source}")

    def get_frame(self):
        ret, frame = self.cap.read()
        if not ret:
            return False, None
        return True, frame

    def release(self):
        if self.cap and self.cap.isOpened():
            self.cap.release()