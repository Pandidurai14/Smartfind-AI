import os
from ultralytics import YOLO

class PersonDetector:
    def __init__(self):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        model_path = os.path.join(base_dir, "models", "yolo", "yolo11n.pt")
        print("Loading YOLOv11 Model with Tracker...")
        self.model = YOLO(model_path)
        
    def detect_and_track(self, frame):
        # persist=True என்பது ID-களை மறக்காமல் ட்ராக் செய்ய உதவும்
        try:
            results = self.model.track(frame, persist=True, classes=[0], verbose=False)
        except Exception as e:
            print(f"YOLO track error: {e}")
            return []

        detections = []
        if not results or results[0].boxes is None or len(results[0].boxes) == 0:
            return detections
        boxes = results[0].boxes.xyxy.cpu().numpy()
        # tracker ID miss aanaalum box-a drop panna koodathu - temp ID 0
        try:
            track_ids = results[0].boxes.id.int().cpu().tolist() if results[0].boxes.id is not None else [0] * len(boxes)
        except Exception:
            track_ids = list(range(len(boxes)))
        try:
            confs = results[0].boxes.conf.cpu().tolist()
        except Exception:
            confs = [0.9] * len(boxes)

        for box, track_id, conf in zip(boxes, track_ids, confs):
            x1, y1, x2, y2 = map(int, box)
            if conf > 0.4:  # dark room ku 0.5 -> 0.4 relax
                detections.append((x1, y1, x2, y2, int(track_id), float(conf)))

        return detections