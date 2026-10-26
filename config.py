import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Folder Paths
UPLOADS_DIR = os.path.join(BASE_DIR, "uploads")
RESULTS_DIR = os.path.join(BASE_DIR, "results")
REPORTS_DIR = os.path.join(BASE_DIR, "reports")
DB_DIR = os.path.join(BASE_DIR, "database")

# AI Thresholds
FACE_MATCH_THRESHOLD = 0.6
REID_MATCH_THRESHOLD = 0.7
BLUR_THRESHOLD = 100.0

# Auto-create necessary empty folders
for folder in [UPLOADS_DIR, RESULTS_DIR, REPORTS_DIR, DB_DIR]:
    os.makedirs(folder, exist_ok=True)