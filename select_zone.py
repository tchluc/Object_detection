"""
Outil interactif pour sélectionner des zones d'alerte dans les vidéos.
Permet de dessiner des rectangles sur la première frame d'une vidéo
pour définir les zones à surveiller.
"""

import cv2
import os

# Configuration
input_folder = "VIDEO_RESEAU_1"
video_name = "CAMERA_HALL_PORTE_GAUCHE.mp4"
video_path = os.path.join(input_folder, video_name)

# Vérifier que la vidéo existe
if not os.path.exists(video_path):
    print(f"Erreur : La vidéo {video_path} n'existe pas.")

    if os.path.exists(input_folder):
        files = [f for f in os.listdir(input_folder) if f.endswith(('.mp4', '.MP4', '.avi'))]
        if files:
            print(f"Vidéos trouvées dans {input_folder}: {files}")
            video_path = os.path.join(input_folder, files[0])
            print(f"Utilisation de {files[0]} par défaut.")
        else:
            print(f"Aucune vidéo trouvée dans {input_folder}.")
            exit()
    else:
        print(f"Le dossier {input_folder} n'existe pas.")
        exit()

# Variables globales pour le dessin
drawing = False  # True si on est en train de dessiner
ix, iy = -1, -1  # Coordonnées initiales
bbox = []        # Boîte englobante finale

def draw_rectangle(event, x, y, flags, param):
    """
    Callback pour gérer les événements de la souris.
    Permet de dessiner un rectangle en cliquant et glissant.
    
    Args:
        event: Type d'événement de la souris
        x, y: Coordonnées de la souris
        flags: Drapeaux supplémentaires
        param: Paramètres supplémentaires
    """
    global ix, iy, drawing, bbox, img_copy

    if event == cv2.EVENT_LBUTTONDOWN:
        # Début du dessin
        drawing = True
        ix, iy = x, y

    elif event == cv2.EVENT_MOUSEMOVE:
        # Mise à jour du rectangle pendant le déplacement
        if drawing:
            img_copy = img.copy()
            cv2.rectangle(img_copy, (ix, iy), (x, y), (0, 255, 0), 2)
            cv2.imshow('Select Alert Zone', img_copy)

    elif event == cv2.EVENT_LBUTTONUP:
        # Fin du dessin
        drawing = False
        cv2.rectangle(img_copy, (ix, iy), (x, y), (0, 255, 0), 2)
        cv2.imshow('Select Alert Zone', img_copy)

        # Normaliser les coordonnées (min/max)
        x1, x2 = min(ix, x), max(ix, x)
        y1, y2 = min(iy, y), max(iy, y)
        bbox = [x1, y1, x2, y2]
        print(f"Zone sélectionnée : {bbox}")
        print(f"Copiez cette ligne dans config.py pour {os.path.basename(video_path)}")


# Charger la première frame de la vidéo
cap = cv2.VideoCapture(video_path)
ret, frame = cap.read()
cap.release()

if not ret:
    print("Erreur : Impossible de lire la vidéo.")
    exit()

# Redimensionner si nécessaire (ici pas de redimensionnement)
scale_percent = 100
width = int(frame.shape[1] * scale_percent / 100)
height = int(frame.shape[0] * scale_percent / 100)
dim = (width, height)

# Préparer les images
img = frame.copy()
img_copy = img.copy()

# Créer la fenêtre et lier le callback de la souris
cv2.namedWindow('Select Alert Zone')
cv2.setMouseCallback('Select Alert Zone', draw_rectangle)

print("Instructions :")
print("1. Dessinez un rectangle avec la souris pour définir la zone d'alerte.")
print("2. Appuyez sur 'c' pour effacer la sélection.")
print("3. Appuyez sur 'q' pour quitter.")

# Boucle principale
while True:
    cv2.imshow('Select Alert Zone', img_copy)
    k = cv2.waitKey(1) & 0xFF
    
    if k == ord('c'):
        # Effacer la sélection
        img_copy = img.copy()
        bbox = []
        print("Sélection effacée.")
    elif k == ord('q'):
        # Quitter
        break

cv2.destroyAllWindows()

# Afficher le résultat final
if bbox:
    print("\n--- RÉSULTAT FINAL ---")
    print(f"Vidéo : {os.path.basename(video_path)}")
    print(f"Coordonnées : {bbox}")
    print("----------------------")
else:
    print("Aucune zone sélectionnée.")
