import cv2
import os

# Configuration
input_folder = "VIDEO_RESEAU_1"  # Dossier contenant les vidéos
video_name = "CAMERA_HALL_PORTE_GAUCHE.mp4"  # Nom de la vidéo cible
video_path = os.path.join(input_folder, video_name)

# Vérifier si le fichier existe
if not os.path.exists(video_path):
    print(f"Erreur : La vidéo {video_path} n'existe pas.")
    # Essayer de trouver une vidéo dans le dossier pour aider
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
drawing = False
ix, iy = -1, -1
bbox = []

def draw_rectangle(event, x, y, flags, param):
    global ix, iy, drawing, bbox, img_copy

    if event == cv2.EVENT_LBUTTONDOWN:
        drawing = True
        ix, iy = x, y

    elif event == cv2.EVENT_MOUSEMOVE:
        if drawing:
            img_copy = img.copy()
            cv2.rectangle(img_copy, (ix, iy), (x, y), (0, 255, 0), 2)
            cv2.imshow('Select Alert Zone', img_copy)

    elif event == cv2.EVENT_LBUTTONUP:
        drawing = False
        cv2.rectangle(img_copy, (ix, iy), (x, y), (0, 255, 0), 2)
        cv2.imshow('Select Alert Zone', img_copy)
        # Normaliser les coordonnées (x1, y1, x2, y2) où x1<x2 et y1<y2
        x1, x2 = min(ix, x), max(ix, x)
        y1, y2 = min(iy, y), max(iy, y)
        bbox = [x1, y1, x2, y2]
        print(f"Zone sélectionnée : {bbox}")
        print(f"Copiez cette ligne dans detection_classification.py pour {os.path.basename(video_path)}")

# Lecture de la première frame
cap = cv2.VideoCapture(video_path)
ret, frame = cap.read()
cap.release()

if not ret:
    print("Erreur : Impossible de lire la vidéo.")
    exit()

# Redimensionner si l'image est trop grande pour l'écran (optionnel, mais pratique)
scale_percent = 100 # Pourcentage de la taille originale
width = int(frame.shape[1] * scale_percent / 100)
height = int(frame.shape[0] * scale_percent / 100)
dim = (width, height)
# Si besoin de resize, décommenter la ligne suivante et ajuster les coords en sortie
# frame = cv2.resize(frame, dim, interpolation = cv2.INTER_AREA)

img = frame.copy()
img_copy = img.copy()

cv2.namedWindow('Select Alert Zone')
cv2.setMouseCallback('Select Alert Zone', draw_rectangle)

print("Instructions :")
print("1. Dessinez un rectangle avec la souris pour définir la zone d'alerte.")
print("2. Appuyez sur 'c' pour effacer la sélection.")
print("3. Appuyez sur 'q' pour quitter.")

while True:
    cv2.imshow('Select Alert Zone', img_copy)
    k = cv2.waitKey(1) & 0xFF
    
    if k == ord('c'):
        img_copy = img.copy()
        bbox = []
        print("Sélection effacée.")
    elif k == ord('q'):
        break

cv2.destroyAllWindows()

if bbox:
    print("\n--- RÉSULTAT FINAL ---")
    print(f"Vidéo : {os.path.basename(video_path)}")
    print(f"Coordonnées : {bbox}")
    print("----------------------")
else:
    print("Aucune zone sélectionnée.")
