import os
import multiprocessing
import config
from processor import process_video_task

def main():
    # Necessary for Windows multiprocessing
    multiprocessing.freeze_support()

    # Shared Memory Manager
    manager = multiprocessing.Manager()
    
    # Shared Data Structures
    shared_global_tracks = manager.dict()
    global_id_counter = manager.Value('i', 1)
    shared_target_id = manager.Value('i', -1)
    lock = manager.Lock()

    # Get Video Files
    if not os.path.exists(config.INPUT_FOLDER):
        print(f"Error: Input folder '{config.INPUT_FOLDER}' not found.")
        return

    video_files = [f for f in os.listdir(config.INPUT_FOLDER) if f.endswith(('.mp4', '.MP4'))]
    print(f"Found videos: {video_files}")

    # Start Processes
    processes = []
    for video_name in video_files:
        p = multiprocessing.Process(
            target=process_video_task,
            args=(video_name, shared_global_tracks, shared_target_id, global_id_counter, lock)
        )
        processes.append(p)
        p.start()

    # Wait for completion
    for p in processes:
        p.join()

    print("Global processing complete.")

if __name__ == "__main__":
    main()
