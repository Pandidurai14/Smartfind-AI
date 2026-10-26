from ultralytics import YOLO

class ByteTrackerEngine:
    def __init__(self, model_path="models/yolo11n.pt"):
        # YOLO's built-in ByteTrack use பண்ணலாம்
        self.model = YOLO(model_path)
        
    def track(self, frame):
        # tracker="bytetrack.yaml" மூலம் ID assign ஆகும்
        results = self.model.track(frame, classes=[0], persist=True, tracker="bytetrack.yaml", verbose=False)
        tracks = []
        
        for r in results:
            if r.boxes.id is not None:
                for box, track_id in zip(r.boxes, r.boxes.id):
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    tracks.append({
                        "track_id": int(track_id),
                        "box": (x1, y1, x2, y2)
                    })
        return tracks