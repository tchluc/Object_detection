import os

# --- Folders ---
INPUT_FOLDER = "VIDEO_RESEAU_1"
OUTPUT_FOLDER = "RESULTATS_DRSI_11"
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# --- Models ---
YOLO_MODEL_PATH = 'yolo11m.pt'
REID_MODEL_PATH = 'yolo26n-cls.pt'
TRACKER_CONFIG = "custom_tracker.yaml"

# --- Alert Zones ---
# Format: 'video_filename': [[x1, y1, x2, y2]]
ALERT_ZONES = {
    'CAMERA_HALL_PORTE_GAUCHE.mp4': [[99, 332, 252, 349]],
}

# --- Display Parameters ---
ZONE_COLOR = (0, 0, 255)    # Red
ALERT_COLOR = (0, 0, 255)   # Red
ZONE_THICKNESS = 2
TEXT_COLOR_NORMAL = (0, 255, 0) # Green
TEXT_COLOR_TARGET = (0, 255, 255) # Yellow

# --- Tracking Parameters ---
SIMILARITY_THRESHOLD = 0.75
