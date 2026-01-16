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
    Independent process function to handle video analysis, tracking, and visualization.
    """
    # Initialize separate Tk instance for this process (fragile but functional for simple dialogs)
    try:
        root = tk.Tk()
        root.withdraw()
    except:
        root = None

    print(f"[{video_name}] STARTING...")
    
    # Initialize Local Models
    model = YOLO(config.YOLO_MODEL_PATH)
    reid = ReID(model=config.REID_MODEL_PATH)

    video_path = os.path.join(config.INPUT_FOLDER, video_name)
    csv_path = os.path.join(config.OUTPUT_FOLDER, f"donnees_{video_name}.csv")

    # Video Setup
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    out_video_path = os.path.join(config.OUTPUT_FOLDER, f"annotated_{video_name}")
    out = cv2.VideoWriter(out_video_path, cv2.VideoWriter_fourcc(*'mp4v'), fps, (width, height))

    current_zones = config.ALERT_ZONES.get(video_name, [])
    local_to_global = {} 

    window_name = f"Video: {video_name}"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(window_name, 640, 480)

    # YOLO Tracking
    results = model.track(
        source=video_path,
        device=0, 
        persist=True,
        stream=True,
        tracker=config.TRACKER_CONFIG,
        imgsz=1280,
        half=True,
        conf=0.5,
        iou=0.5,
        vid_stride=1,
        save=False
    )

    with open(csv_path, mode='w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['camera', 'frame', 'id', 'class_name', 'x_center', 'y_center', 'alerte'])

        frame_idx = 0
        for r in results:
            ret, frame = cap.read()
            if not ret: break

            # Draw Zones
            for zone in current_zones:
                cv2.rectangle(frame, (zone[0], zone[1]), (zone[2], zone[3]), config.ZONE_COLOR, config.ZONE_THICKNESS)

            if r.boxes.id is not None:
                ids = r.boxes.id.int().cpu().tolist()
                boxes = r.boxes.xywh.cpu().numpy()
                clss = r.boxes.cls.int().cpu().tolist()

                dets = np.array([[x - w/2, y - h/2, x + w/2, y + h/2] for x, y, w, h in boxes])
                embeddings = reid(r.orig_img, dets) if len(dets) > 0 else []

                for i, (obj_id, box, cls_id) in enumerate(zip(ids, boxes, clss)):
                    name = model.names[cls_id]
                    x, y, w, h = box
                    x1, y1, x2, y2 = int(x - w/2), int(y - h/2), int(x + w/2), int(y + h/2)

                    if i >= len(embeddings) or embeddings[i].size == 0:
                        continue
                    
                    embedding = embeddings[i]

                    # --- Global ID Matching ---
                    with lock:
                        tracks_snapshot = shared_global_tracks.copy()
                    
                    best_id, best_sim = tracking.find_best_match(embedding, tracks_snapshot)
                    
                    final_global_id = None
                    if best_id is not None and best_sim > config.SIMILARITY_THRESHOLD:
                        final_global_id = best_id
                        tracking.update_global_track(shared_global_tracks, final_global_id, embedding, (x, y), video_name, lock)
                    else:
                        final_global_id = tracking.create_new_track(shared_global_tracks, global_id_counter, embedding, (x, y), video_name, lock)
                    
                    local_to_global[obj_id] = final_global_id

                    # Alert Check
                    is_alert = 1 if alerts.is_in_zone(box, current_zones) else 0
                    if is_alert:
                        cv2.circle(frame, (int(x), int(y)), 10, config.ALERT_COLOR, -1)
                        print(f"[{video_name}] ALERT Object {final_global_id}", flush=True)

                    writer.writerow([video_name, frame_idx, final_global_id, name, x, y, is_alert])

                    # Visualization logic
                    current_target = shared_target_id.value
                    color = config.TEXT_COLOR_NORMAL
                    thickness = 2
                    
                    if current_target != -1 and str(final_global_id) == str(current_target):
                        color = config.TEXT_COLOR_TARGET
                        thickness = 4
                        cv2.putText(frame, "CIBLE", (x1, y1 - 30), cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)
                        
                        try:
                            # Show crop in separate window
                            crop_x1, crop_y1 = max(0, x1), max(0, y1)
                            crop_x2, crop_y2 = min(width, x2), min(height, y2)
                            if crop_x2 > crop_x1 and crop_y2 > crop_y1:
                                target_crop = frame[crop_y1:crop_y2, crop_x1:crop_x2]
                                cv2.imshow(f"Tracking ID {current_target}", target_crop)
                        except: pass
                    
                    cv2.rectangle(frame, (x1, y1), (x2, y2), color, thickness)
                    cv2.putText(frame, f"ID:{final_global_id}", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

            # Final Display
            annotated_frame = r.plot(img=frame)
            disp = cv2.resize(frame, (960, 540))
            cv2.imshow(window_name, disp)
            out.write(frame)

            # Input Handling
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('s'):
                if root:
                    new_id = simpledialog.askstring(f"Select ID ({video_name})", "Enter Global ID to track:", parent=root)
                    if new_id:
                        try:
                            shared_target_id.value = int(new_id)
                            print(f"Target set to: {new_id}", flush=True)
                        except ValueError:
                            print("Invalid ID")
                    else:
                        shared_target_id.value = -1
                        cv2.destroyAllWindows()
                        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)

            frame_idx += 1

    cap.release()
    out.release()
    cv2.destroyWindow(window_name)
    if root: root.destroy()
    print(f"[{video_name}] FINISHED.")
