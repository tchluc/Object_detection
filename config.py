"""
Fichier de configuration central pour le système de détection d'objets.
Contient tous les paramètres configurables du projet.
"""

import os

# --- Dossiers ---
INPUT_FOLDER = "VIDEO_RESEAU_1"         # Dossier contenant les vidéos d'entrée
OUTPUT_FOLDER = "RESULTATS_DRSI_11"     # Dossier pour les résultats (vidéos, CSV)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# --- Modèles ---
YOLO_MODEL_PATH = 'yolo11m.pt'          # Modèle YOLO pour la détection d'objets
REID_MODEL_PATH = 'yolo26n-cls.pt'      # Modèle pour la réidentification (ReID)
TRACKER_CONFIG = "custom_tracker.yaml"   # Configuration du tracker BotSort

# --- Zones d'Alerte ---
# Format: 'nom_video.mp4': [[x1, y1, x2, y2], [x1, y1, x2, y2], ...]
# Plusieurs zones peuvent être définies par vidéo
ALERT_ZONES = {
    'CAMERA_HALL_PORTE_GAUCHE.mp4': [[99, 332, 252, 349]],
}

# --- Paramètres d'Affichage ---
ZONE_COLOR = (0, 0, 255)           # Couleur des zones d'alerte (Rouge BGR)
ALERT_COLOR = (0, 0, 255)          # Couleur des alertes (Rouge BGR)
ZONE_THICKNESS = 2                 # Épaisseur du trait des zones
TEXT_COLOR_NORMAL = (0, 255, 0)    # Couleur du texte normal (Vert BGR)
TEXT_COLOR_TARGET = (0, 255, 255)  # Couleur pour l'objet ciblé (Jaune BGR)

# --- Paramètres de Tracking ---
SIMILARITY_THRESHOLD = 0.75         # Seuil de similarité pour la réidentification (0-1)
