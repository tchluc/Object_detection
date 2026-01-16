"""
Script principal pour la détection et le suivi d'objets multi-vidéos.
Utilise le multiprocessing pour traiter plusieurs vidéos en parallèle.
"""

import os
import multiprocessing
import config
from processor import process_video_task
from summary import generate_object_summary, print_summary_stats

def main():
    """
    Point d'entrée principal du programme.
    Lance le traitement parallèle des vidéos et génère un résumé final.
    """
    # Nécessaire pour le multiprocessing sous Windows
    multiprocessing.freeze_support()

    # Gestionnaire de mémoire partagée pour la communication entre processus
    manager = multiprocessing.Manager()
    
    # Structures de données partagées entre tous les processus
    shared_global_tracks = manager.dict()      # Tracks globaux pour le suivi inter-vidéo
    global_id_counter = manager.Value('i', 1)  # Compteur d'ID globaux
    shared_target_id = manager.Value('i', -1)  # ID de l'objet ciblé (-1 = aucun)
    lock = manager.Lock()                       # Verrou pour accès concurrent sécurisé

    # Vérifier l'existence du dossier d'entrée
    if not os.path.exists(config.INPUT_FOLDER):
        print(f"Erreur: Le dossier '{config.INPUT_FOLDER}' n'existe pas.")
        return

    # Récupérer toutes les vidéos à traiter
    video_files = [f for f in os.listdir(config.INPUT_FOLDER) if f.endswith(('.mp4', '.MP4'))]
    print(f"Vidéos trouvées: {video_files}")

    # Créer et démarrer un processus par vidéo
    processes = []
    for video_name in video_files:
        p = multiprocessing.Process(
            target=process_video_task,
            args=(video_name, shared_global_tracks, shared_target_id, global_id_counter, lock)
        )
        processes.append(p)
        p.start()

    # Attendre que tous les processus se terminent
    for p in processes:
        p.join()

    print("Traitement global terminé.")
    
    # Générer le résumé des objets détectés
    print("\nGénération du résumé des objets...")
    stats = generate_object_summary(config.OUTPUT_FOLDER)
    print_summary_stats(stats)

if __name__ == "__main__":
    main()
