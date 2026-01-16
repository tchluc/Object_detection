"""
Outil interactif pour sélectionner des zones d'alerte polygonales dans les vidéos.
Permet de dessiner des polygones libres sur la première frame d'une vidéo
pour définir des surfaces au sol à surveiller.
"""

import cv2
import numpy as np
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
points = []  # Points du polygone en cours
polygons = []  # Liste de tous les polygones terminés
current_polygon = []  # Polygone en cours de création


def draw_polygon(event, x, y, flags, param):
    """
    Callback pour gérer les événements de la souris.
    Permet de dessiner un polygone en cliquant pour chaque point.
    
    Args:
        event: Type d'événement de la souris
        x, y: Coordonnées de la souris
        flags: Drapeaux supplémentaires
        param: Paramètres supplémentaires
    """
    global points, img_copy, current_polygon

    if event == cv2.EVENT_LBUTTONDOWN:
        # Ajouter un point au polygone
        points.append((x, y))
        img_copy = img.copy()
        
        # Dessiner tous les polygones terminés
        for poly in polygons:
            pts = np.array(poly, dtype=np.int32)
            cv2.polylines(img_copy, [pts], isClosed=True, color=(0, 255, 0), thickness=2)
            cv2.fillPoly(img_copy, [pts], color=(0, 255, 0, 50))
        
        # Dessiner le polygone en cours
        if len(points) > 1:
            pts = np.array(points, dtype=np.int32)
            cv2.polylines(img_copy, [pts], isClosed=False, color=(255, 0, 0), thickness=2)
        
        # Marquer chaque point
        for pt in points:
            cv2.circle(img_copy, pt, 5, (0, 0, 255), -1)
        
        cv2.imshow('Select Polygon Zone', img_copy)
        print(f"Point ajouté: {(x, y)}")

    elif event == cv2.EVENT_MOUSEMOVE:
        # Afficher une ligne temporaire vers la souris
        if len(points) > 0:
            temp_img = img_copy.copy()
            cv2.line(temp_img, points[-1], (x, y), (128, 128, 128), 1)
            cv2.imshow('Select Polygon Zone', temp_img)


# Charger la première frame de la vidéo
cap = cv2.VideoCapture(video_path)
ret, frame = cap.read()
cap.release()

if not ret:
    print("Erreur : Impossible de lire la vidéo.")
    exit()

# Préparer les images
img = frame.copy()
img_copy = img.copy()

# Créer la fenêtre et lier le callback de la souris
cv2.namedWindow('Select Polygon Zone')
cv2.setMouseCallback('Select Polygon Zone', draw_polygon)

print("\n" + "="*60)
print("INSTRUCTIONS - Sélection de Zone Polygonale")
print("="*60)
print("1. Cliquez pour ajouter des points au polygone")
print("2. Appuyez sur 'ESPACE' pour fermer le polygone actuel")
print("3. Appuyez sur 'c' pour effacer le polygone en cours")
print("4. Appuyez sur 'r' pour effacer tous les polygones")
print("5. Appuyez sur 'q' pour quitter")
print("="*60 + "\n")

# Boucle principale
while True:
    cv2.imshow('Select Polygon Zone', img_copy)
    k = cv2.waitKey(1) & 0xFF
    
    if k == ord(' '):
        # Espace : Fermer le polygone actuel
        if len(points) >= 3:
            polygons.append(points.copy())
            print(f"Polygone terminé avec {len(points)} points")
            print(f"Coordonnées : {points}")
            points = []
            
            # Redessiner tout
            img_copy = img.copy()
            for poly in polygons:
                pts = np.array(poly, dtype=np.int32)
                cv2.polylines(img_copy, [pts], isClosed=True, color=(0, 255, 0), thickness=2)
                cv2.fillPoly(img_copy, [pts], color=(0, 255, 0, 50))
        else:
            print("Il faut au moins 3 points pour créer un polygone")
    
    elif k == ord('c'):
        # Effacer le polygone en cours
        points = []
        img_copy = img.copy()
        for poly in polygons:
            pts = np.array(poly, dtype=np.int32)
            cv2.polylines(img_copy, [pts], isClosed=True, color=(0, 255, 0), thickness=2)
        print("Polygone en cours effacé")
    
    elif k == ord('r'):
        # Réinitialiser tout
        points = []
        polygons = []
        img_copy = img.copy()
        print("Tous les polygones effacés")
    
    elif k == ord('q'):
        # Quitter
        break

cv2.destroyAllWindows()

# Afficher le résultat final
if polygons:
    print("\n" + "="*60)
    print("RÉSULTAT FINAL - Zones Polygonales")
    print("="*60)
    print(f"Vidéo : {os.path.basename(video_path)}")
    print(f"Nombre de polygones : {len(polygons)}")
    print("\nÀ copier dans config.py (ALERT_ZONES) :")
    print(f"'{os.path.basename(video_path)}': [")
    for i, poly in enumerate(polygons):
        print(f"    {poly},  # Polygone {i+1}")
    print("],")
    print("="*60 + "\n")
elif points and len(points) >= 3:
    print("\nAttention : Vous avez des points non fermés. Appuyez sur ESPACE pour les valider.")
else:
    print("\nAucune zone sélectionnée.")
