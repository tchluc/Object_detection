"""
Module pour générer des résumés statistiques des objets détectés.
Ce module analyse les données CSV et crée des fichiers de synthèse.
"""

import os
import csv
from collections import defaultdict


def generate_object_summary(csv_folder, output_file="object_summary.csv"):
    """
    Génère un fichier CSV résumant les classes d'objets et leur nombre d'apparitions.
    
    Args:
        csv_folder (str): Dossier contenant les fichiers CSV de trajectoires
        output_file (str): Nom du fichier de sortie pour le résumé
    
    Returns:
        dict: Dictionnaire avec les statistiques par vidéo et globales
    """
    # Dictionnaires pour compter les objets
    global_class_counts = defaultdict(int)  # Compte global par classe
    video_class_counts = defaultdict(lambda: defaultdict(int))  # Compte par vidéo et classe
    unique_objects = defaultdict(set)  # IDs uniques par classe
    
    # Parcourir tous les fichiers CSV dans le dossier
    csv_files = [f for f in os.listdir(csv_folder) if f.endswith('.csv') and f.startswith('donnees_')]
    
    for csv_file in csv_files:
        csv_path = os.path.join(csv_folder, csv_file)
        video_name = csv_file.replace('donnees_', '').replace('.csv', '')
        
        with open(csv_path, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                class_name = row.get('class_name', 'unknown')
                obj_id = row.get('id', '0')
                
                # Compter les apparitions par classe
                global_class_counts[class_name] += 1
                video_class_counts[video_name][class_name] += 1
                
                # Suivre les IDs uniques par classe
                unique_objects[class_name].add(obj_id)
    
    # Générer le fichier de résumé
    summary_path = os.path.join(csv_folder, output_file)
    with open(summary_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Type', 'Classe', 'Nom_Video', 'Nombre_Apparitions', 'Objets_Uniques'])
        
        # Écrire les résumés globaux
        for class_name in sorted(global_class_counts.keys()):
            writer.writerow([
                'GLOBAL',
                class_name,
                'TOUTES_VIDEOS',
                global_class_counts[class_name],
                len(unique_objects[class_name])
            ])
        
        # Écrire les résumés par vidéo
        for video_name in sorted(video_class_counts.keys()):
            for class_name in sorted(video_class_counts[video_name].keys()):
                writer.writerow([
                    'PAR_VIDEO',
                    class_name,
                    video_name,
                    video_class_counts[video_name][class_name],
                    ''  # Les objets uniques sont comptés globalement
                ])
    
    print(f"Résumé généré: {summary_path}")
    return {
        'global': dict(global_class_counts),
        'by_video': dict(video_class_counts),
        'unique_ids': {k: len(v) for k, v in unique_objects.items()}
    }


def print_summary_stats(stats):
    """
    Affiche les statistiques de manière lisible dans la console.
    
    Args:
        stats (dict): Dictionnaire de statistiques retourné par generate_object_summary
    """
    print("\n" + "="*60)
    print("RÉSUMÉ DES OBJETS DÉTECTÉS")
    print("="*60)
    
    print("\n--- STATISTIQUES GLOBALES ---")
    for class_name, count in sorted(stats['global'].items()):
        unique_count = stats['unique_ids'].get(class_name, 0)
        print(f"  {class_name}: {count} apparitions, {unique_count} objets uniques")
    
    print("\n--- STATISTIQUES PAR VIDÉO ---")
    for video_name, classes in sorted(stats['by_video'].items()):
        print(f"\n  Vidéo: {video_name}")
        for class_name, count in sorted(classes.items()):
            print(f"    - {class_name}: {count} apparitions")
    
    print("\n" + "="*60 + "\n")
