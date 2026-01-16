import os
import csv
import torch
import numpy as np
from ultralytics import YOLO
from ultralytics.trackers.bot_sort import ReID
from sklearn.metrics.pairwise import cosine_similarity
import cv2  # Pour dessiner zones et checker intersections

# 1. Configuration des dossiers
input_folder = "VIDEO_RESEAU_1"
output_folder = "RESULTATS_DRSI_11"
os.makedirs(output_folder, exist_ok=True)

# 2. Chargement des modèles
model = YOLO('yolo11m.pt')
reid = ReID(model='yolo26n-cls.pt')  # Ou 'yolov8n-cls.pt' si besoin

# 3. Définition des zones d'alertes
# UTILISEZ select_zone.py pour obtenir les coordonnées [x1, y1, x2, y2] pour vos vidéos
# Configurez les zones ici :
alert_zones = {
    'CAMERA_HALL_PORTE_GAUCHE.mp4': [[100, 100, 500, 500]], 
    # 'votre_video.mp4': [[x1, y1, x2, y2]],
}
zone_color = (0, 0, 255)  # Rouge pour dessin des zones
alert_color = (0, 0, 255) # Couleur de l'alerte
zone_thickness = 2

# Fonction pour checker si un objet est dans une zone (rectangle simple ; pour polygone, utilise cv2.pointPolygonTest)
def is_in_zone(box, zones):
    x, y, w, h = box
    center_x, center_y = x, y  # Centre de la bbox
    for zone in zones:
        x1, y1, x2, y2 = zone
        if x1 < center_x < x2 and y1 < center_y < y2:
            return True
    return False

csv_path = os.path.join(output_folder, "donnees_trajectoires.csv")

global_tracks = {}  # {global_id: {'embedding': np.array, 'last_pos': (x,y), 'last_video': str}}
global_id_counter = 1

with open(csv_path, mode='w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['camera', 'frame', 'id', 'class_name', 'x_center', 'y_center', 'alerte'])  # Ajout colonne 'alerte'

    video_files = [f for f in os.listdir(input_folder) if f.endswith(('.mp4', '.MP4'))]

    for video_name in video_files:
        video_path = os.path.join(input_folder, video_name)
        print(f"Traitement : {video_name}")

        # Récup zones pour cette vidéo (défaut : aucune)
        current_zones = alert_zones.get(video_name, [])

        results = model.track(
            source=video_path,
            device=0,
            persist=True,
            stream=True,
            tracker="custom_tracker.yaml",
            imgsz=1280,
            half=True,
            conf=0.5,
            iou=0.5,
            vid_stride=1,
            save=True  # Sauvegarde vidéo annotée
        )

        local_to_global = {}

        # Ouvrir la vidéo pour dessin (optionnel : pour ajouter zones sur la sortie sauvegardée)
        cap = cv2.VideoCapture(video_path)
        fps = cap.get(cv2.CAP_PROP_FPS)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        out_video_path = os.path.join(output_folder, f"annotated_{video_name}")
        out = cv2.VideoWriter(out_video_path, cv2.VideoWriter_fourcc(*'mp4v'), fps, (width, height))

        frame_idx = 0
        for r in results:
            # Lire frame originale pour dessin
            ret, frame = cap.read()
            if not ret:
                break

            # Dessiner zones d'alertes sur le frame
            for zone in current_zones:
                cv2.rectangle(frame, (zone[0], zone[1]), (zone[2], zone[3]), zone_color, zone_thickness)

            if r.boxes.id is not None:
                ids = r.boxes.id.int().cpu().tolist()
                boxes = r.boxes.xywh.cpu().numpy()
                clss = r.boxes.cls.int().cpu().tolist()

                dets = np.array([[x - w/2, y - h/2, x + w/2, y + h/2] for x, y, w, h in boxes])

                if len(dets) > 0:
                    embeddings = reid(r.orig_img, dets)
                else:
                    embeddings = []

                for i, (obj_id, box, cls_id) in enumerate(zip(ids, boxes, clss)):
                    name = model.names[cls_id]
                    x, y, w, h = box

                    if i >= len(embeddings) or embeddings[i].size == 0:
                        continue

                    embedding = embeddings[i]

                    # Matching global (comme avant)
                    matched = False
                    for g_id, data in global_tracks.items():
                        sim = cosine_similarity(embedding.reshape(1, -1), data['embedding'].reshape(1, -1))[0][0]
                        if sim > 0.7:
                            local_to_global[obj_id] = g_id
                            global_tracks[g_id]['embedding'] = embedding
                            global_tracks[g_id]['last_pos'] = (x, y)
                            global_tracks[g_id]['last_video'] = video_name
                            matched = True
                            break

                    if not matched:
                        local_to_global[obj_id] = global_id_counter
                        global_tracks[global_id_counter] = {'embedding': embedding, 'last_pos': (x, y), 'last_video': video_name}
                        global_id_counter += 1

                    # Checker alerte
                    alerte = 1 if is_in_zone(box, current_zones) else 0
                    if alerte:
                        print(f"Alerte ! Objet {local_to_global[obj_id]} ({name}) dans zone sur {video_name} frame {frame_idx}")

                    # Écrire dans CSV avec alerte
                    writer.writerow([video_name, frame_idx, local_to_global[obj_id], name, x, y, alerte])

                    # Optionnel : Dessiner alerte sur frame (ex. : cercle rouge sur objet en alerte)
                    # Optionnel : Dessiner alerte sur frame (ex. : cercle rouge sur objet en alerte)
                    if alerte:
                        # Cercle sur l'objet
                        cv2.circle(frame, (int(x), int(y)), 10, alert_color, -1)
                        # Texte ALERTE en haut de l'écran
                        cv2.putText(frame, "ALERTE INTRUSION!", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 3, alert_color, 5)
                        # Texte sur l'objet
                        cv2.putText(frame, "ALERTE", (int(x), int(y)-20), cv2.FONT_HERSHEY_SIMPLEX, 1, alert_color, 2)

            # Ajouter annotations YOLO sur le frame (si besoin ; sinon, utilise r.plot())
            annotated_frame = r.plot(img=frame)  # Superpose annotations YOLO sur notre frame modifié

            # Écrire frame annoté dans vidéo sortie
            out.write(annotated_frame)

            frame_idx += 1

        # Nettoyage
        cap.release()
        out.release()
        del results
        torch.cuda.empty_cache()

print(f"Analyse terminée. Résultats dans {csv_path} et vidéos annotées dans {output_folder}")