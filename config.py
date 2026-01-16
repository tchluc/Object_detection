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
# Format: 'nom_video.mp4': [zone1, zone2, ...]
# 
# Types de zones supportés:
# 1. Rectangle: [x1, y1, x2, y2]
# 2. Polygone: [(x1, y1), (x2, y2), (x3, y3), ...]
#
# Exemples:
# - Rectangle simple: [[100, 100, 500, 500]]
# - Polygone: [[(100, 100), (500, 100), (500, 500), (100, 500)]]
# - Mixte: [[100, 100, 500, 500], [(600, 100), (800, 100), (800, 300)]]
#
# Utilisez select_zone.py pour les rectangles
# Utilisez select_polygon_zone.py pour les polygones (surfaces au sol)
#
ALERT_ZONES = {
    'CAMERA_HALL_PORTE_GAUCHE.mp4': [[99, 332, 252, 349]],
    # Exemple avec polygone (décommentez et ajustez):
    # 'autre_video.mp4': [[(100, 100), (500, 100), (400, 300), (200, 300)]],
}

# --- Paramètres d'Affichage ---
ZONE_COLOR = (0, 0, 255)           # Couleur des zones d'alerte (Rouge BGR)
ALERT_COLOR = (0, 0, 255)          # Couleur des alertes (Rouge BGR)
ZONE_THICKNESS = 2                 # Épaisseur du trait des zones
TEXT_COLOR_NORMAL = (0, 255, 0)    # Couleur du texte normal (Vert BGR)
TEXT_COLOR_TARGET = (0, 255, 255)  # Couleur pour l'objet ciblé (Jaune BGR)

# --- Paramètres de Tracking ---
SIMILARITY_THRESHOLD = 0.75         # Seuil de similarité pour la réidentification (0-1)
