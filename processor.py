"""
Module de traitement vidéo pour la détection et le suivi d'objets.
Gère l'analyse frame par frame, le tracking local et global, les alertes et la visualisation.
"""

import os
import csv
import cv2
import numpy as np
import tkinter as tk
from tkinter import simpledialog
from ultralytics import YOLO
from ultralytics.trackers.bot_sort import ReID

import config
import alerts
import tracking

def process_video_task(video_name, shared_global_tracks, shared_target_id, global_id_counter, lock):
    """
    Fonction de processus indépendante pour gérer l'analyse vidéo complète.
    
    Args:
        video_name (str): Nom du fichier vidéo à traiter
        shared_global_tracks (dict): Dictionnaire partagé des tracks globaux
        shared_target_id (Value): ID de l'objet ciblé pour le suivi
        global_id_counter (Value): Compteur d'IDs globaux
        lock (Lock): Verrou pour l'accès concurrent aux données partagées
    """
    # Initialiser une instance Tk séparée pour ce processus (pour les dialogues)
    try:
        root = tk.Tk()
        root.withdraw()
    except:
        root = None

    print(f"[{video_name}] DÉMARRAGE...")
    
    # Initialiser les modèles locaux (un par processus)
    model = YOLO(config.YOLO_MODEL_PATH)
    reid = ReID(model=config.REID_MODEL_PATH)

    video_path = os.path.join(config.INPUT_FOLDER, video_name)
    csv_path = os.path.join(config.OUTPUT_FOLDER, f"donnees_{video_name}.csv")

    # Configuration de la vidéo
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    # Créer le fichier vidéo de sortie annoté
    out_video_path = os.path.join(config.OUTPUT_FOLDER, f"annotated_{video_name}")
    out = cv2.VideoWriter(out_video_path, cv2.VideoWriter_fourcc(*'mp4v'), fps, (width, height))

    # Récupérer les zones d'alerte pour cette vidéo
    current_zones = config.ALERT_ZONES.get(video_name, [])
    local_to_global = {}  # Mapping des IDs locaux vers IDs globaux

    # Créer une fenêtre d'affichage
    window_name = f"Video: {video_name}"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(window_name, 640, 480)

    # Lancer le tracking YOLO en streaming
    results = model.track(
        source=video_path,
        device=0,              # GPU si disponible (sinon utilise CPU)
        persist=True,          # Maintenir les tracks entre les frames
        stream=True,           # Mode streaming pour économiser la mémoire
        tracker=config.TRACKER_CONFIG,
        imgsz=1280,           # Taille d'image pour la détection
        half=True,            # Utiliser la précision FP16 (plus rapide)
        conf=0.5,             # Seuil de confiance minimum
        iou=0.5,              # Seuil IoU pour NMS
        vid_stride=1,         # Traiter chaque frame
        save=False            # Ne pas sauvegarder automatiquement
    )

    # Créer le fichier CSV pour sauvegarder les trajectoires
    with open(csv_path, mode='w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['camera', 'frame', 'id', 'class_name', 'x_center', 'y_center', 'alerte'])

        frame_idx = 0
        for r in results:
            ret, frame = cap.read()
            if not ret: break

            # Dessiner les zones d'alerte sur la frame
            for zone in current_zones:
                cv2.rectangle(frame, (zone[0], zone[1]), (zone[2], zone[3]), config.ZONE_COLOR, config.ZONE_THICKNESS)

            # Traiter les détections si des objets sont présents
            if r.boxes.id is not None:
                ids = r.boxes.id.int().cpu().tolist()
                boxes = r.boxes.xywh.cpu().numpy()
                clss = r.boxes.cls.int().cpu().tolist()

                # Convertir les boîtes au format xyxy pour ReID
                dets = np.array([[x - w/2, y - h/2, x + w/2, y + h/2] for x, y, w, h in boxes])
                # Extraire les embeddings pour la réidentification
                embeddings = reid(r.orig_img, dets) if len(dets) > 0 else []

                for i, (obj_id, box, cls_id) in enumerate(zip(ids, boxes, clss)):
                    name = model.names[cls_id]
                    x, y, w, h = box
                    x1, y1, x2, y2 = int(x - w/2), int(y - h/2), int(x + w/2), int(y + h/2)

                    # Vérifier que l'embedding existe
                    if i >= len(embeddings) or embeddings[i].size == 0:
                        continue
                    
                    embedding = embeddings[i]

                    # --- Matching Global ID avec les autres vidéos ---
                    with lock:
                        tracks_snapshot = shared_global_tracks.copy()
                    
                    # Trouver la meilleure correspondance avec les tracks existants
                    best_id, best_sim = tracking.find_best_match(embedding, tracks_snapshot)
                    
                    final_global_id = None
                    if best_id is not None and best_sim > config.SIMILARITY_THRESHOLD:
                        # Objet reconnu, utiliser l'ID existant
                        final_global_id = best_id
                        tracking.update_global_track(shared_global_tracks, final_global_id, embedding, (x, y), video_name, lock)
                    else:
                        # Nouvel objet, créer un nouvel ID global
                        final_global_id = tracking.create_new_track(shared_global_tracks, global_id_counter, embedding, (x, y), video_name, lock)
                    
                    local_to_global[obj_id] = final_global_id

                    # Vérification des alertes
                    is_alert = 1 if alerts.is_in_zone(box, current_zones) else 0
                    if is_alert:
                        # Marquer l'objet en alerte avec un cercle rouge
                        cv2.circle(frame, (int(x), int(y)), 10, config.ALERT_COLOR, -1)
                        print(f"[{video_name}] ALERTE Objet {final_global_id}", flush=True)

                    # Sauvegarder les données dans le CSV
                    writer.writerow([video_name, frame_idx, final_global_id, name, x, y, is_alert])

                    # Logique de visualisation
                    current_target = shared_target_id.value
                    color = config.TEXT_COLOR_NORMAL
                    thickness = 2
                    
                    # Mettre en surbrillance l'objet ciblé
                    if current_target != -1 and str(final_global_id) == str(current_target):
                        color = config.TEXT_COLOR_TARGET
                        thickness = 4
                        cv2.putText(frame, "CIBLE", (x1, y1 - 30), cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)
                        
                        try:
                            # Afficher un crop de l'objet ciblé dans une fenêtre séparée
                            crop_x1, crop_y1 = max(0, x1), max(0, y1)
                            crop_x2, crop_y2 = min(width, x2), min(height, y2)
                            if crop_x2 > crop_x1 and crop_y2 > crop_y1:
                                target_crop = frame[crop_y1:crop_y2, crop_x1:crop_x2]
                                cv2.imshow(f"Tracking ID {current_target}", target_crop)
                        except: pass
                    
                    # Dessiner la boîte englobante et l'ID
                    cv2.rectangle(frame, (x1, y1), (x2, y2), color, thickness)
                    cv2.putText(frame, f"ID:{final_global_id}", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

            # Affichage final
            annotated_frame = r.plot(img=frame)
            disp = cv2.resize(frame, (960, 540))
            cv2.imshow(window_name, disp)
            out.write(frame)

            # Gestion des entrées clavier
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('s'):
                # Touche 's' pour sélectionner un objet à suivre
                if root:
                    new_id = simpledialog.askstring(f"Select ID ({video_name})", "Entrer l'ID Global à suivre:", parent=root)
                    if new_id:
                        try:
                            shared_target_id.value = int(new_id)
                            print(f"Cible définie: {new_id}", flush=True)
                        except ValueError:
                            print("ID invalide")
                    else:
                        shared_target_id.value = -1
                        cv2.destroyAllWindows()
                        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)

            frame_idx += 1

    # Libérer les ressources
    cap.release()
    out.release()
    cv2.destroyWindow(window_name)
    if root: root.destroy()
    print(f"[{video_name}] TERMINÉ.")
