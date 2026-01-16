# Projet de Détection et Suivi d'Objets avec Zones d'Alerte

Ce projet utilise l'intelligence artificielle (YOLO) pour détecter, classifier et suivre des objets dans des vidéos de surveillance. Il inclut une fonctionnalité permettant de définir des zones d'alerte et de signaler lorsqu'un objet pénètre dans ces zones.

## Fonctionnalités

*   **Détection et Classification** : Utilise YOLO (YOLOv11) pour identifier différents types d'objets.
*   **Suivi (Tracking)** : Utilise l'algorithme BotSort (configuré via `custom_tracker.yaml`) pour suivre les objets d'une image à l'autre.
*   **Ré-identification (ReID)** : Utilise un modèle de classification secondaire et la similarité cosinus pour conserver l'identité des objets même après une occlusion ou lors du passage d'une caméra à une autre (suivi global).
*   **Zones d'Alerte** : Permet de définir des zones rectangulaires spécifiques pour chaque vidéo. Si un objet entre dans cette zone, une alerte est générée.
*   **Export des Données** : Les trajectoires et les alertes sont sauvegardées dans des fichiers CSV.
*   **Résumé des Objets** : Génère automatiquement un fichier récapitulatif avec les classes d'objets et leur nombre d'apparitions.
*   **Visualisation** : Génère des vidéos annotées avec les boîtes englobantes, les identifiants et les indicateurs d'alerte.

## Structure du Projet

```
Object_detection/
├── main.py                     # Script principal (point d'entrée)
├── processor.py                # Module de traitement vidéo
├── tracking.py                 # Module de tracking global
├── alerts.py                   # Module de gestion des alertes (rectangles et polygones)
├── config.py                   # Configuration centrale
├── summary.py                  # Module de génération de résumés
├── select_zone.py              # Outil de sélection de zones rectangulaires
├── select_polygon_zone.py      # Outil de sélection de zones polygonales
├── custom_tracker.yaml         # Configuration du tracker BotSort
├── VIDEO_RESEAU_1/             # Dossier des vidéos d'entrée
├── RESULTATS_DRSI_11/          # Dossier des résultats
│   ├── donnees_*.csv           # Trajectoires par vidéo
│   ├── object_summary.csv      # Résumé des objets détectés
│   └── annotated_*.mp4         # Vidéos annotées
└── yolo*.pt                    # Modèles YOLO pré-entraînés
```

## Architecture

Le projet est organisé en modules clairs avec des responsabilités séparées :

*   **main.py** : Gestion du multiprocessing et coordination des traitements
*   **processor.py** : Traitement des frames, détection et visualisation
*   **tracking.py** : Logique de tracking global inter-vidéos
*   **alerts.py** : Vérification des zones d'alerte
*   **summary.py** : Génération de statistiques et résumés
*   **config.py** : Paramètres centralisés et configuration

## Prérequis

Assurez-vous d'avoir Python installé. Les bibliothèques suivantes sont nécessaires :

```bash
pip install ultralytics opencv-python numpy scikit-learn torch
```

Note : `torch` est généralement installé avec `ultralytics`, mais assurez-vous d'avoir la version compatible avec votre matériel (CUDA pour GPU NVIDIA est recommandé pour la vitesse).

## Installation

1.  Clonez ce dépôt ou copiez les fichiers dans un dossier local.
2.  Assurez-vous que vos vidéos à analyser sont dans le dossier `VIDEO_RESEAU_1`.
3.  Téléchargez ou assurez-vous que les modèles YOLO (`yolo11m.pt`, `yolo26n-cls.pt`) sont présents à la racine du projet (ils seront téléchargés automatiquement au premier lancement si manquants, connexion internet requise).

## Utilisation

### 1. Définir les Zones d'Alerte (Optionnel)

Si vous souhaitez surveiller des zones spécifiques, vous avez deux options :

#### Option A : Zones Rectangulaires (simples)

1.  Ouvrez `select_zone.py`.
2.  Modifiez la variable `video_name` si nécessaire.
3.  Exécutez le script :
    ```bash
    python select_zone.py
    ```
4.  Une fenêtre s'ouvre. Dessinez un rectangle avec la souris autour de la zone à surveiller.
5.  Les coordonnées s'afficheront dans la console (ex: `[100, 100, 500, 500]`).

#### Option B : Zones Polygonales (surfaces au sol)

Pour des zones plus complexes (surfaces au sol, zones irrégulières) :

1.  Exécutez le script :
    ```bash
    python select_polygon_zone.py
    ```
2.  Cliquez pour placer chaque point du polygone
3.  Appuyez sur **ESPACE** pour fermer le polygone
4.  Vous pouvez créer plusieurs polygones
5.  Les coordonnées complètes s'afficheront dans la console

#### Configuration des Zones

Copiez les coordonnées obtenues et ouvrez `config.py` pour mettre à jour `ALERT_ZONES` :

```python
ALERT_ZONES = {
    # Zones rectangulaires
    'video1.mp4': [[100, 100, 500, 500]],
    
    # Zones polygonales (surfaces au sol)
    'video2.mp4': [[(150, 200), (450, 180), (500, 400), (100, 420)]],
    
    # Plusieurs zones mixtes
    'video3.mp4': [
        [50, 50, 200, 200],  # Rectangle
        [(300, 100), (500, 120), (480, 300), (320, 280)]  # Polygone
    ],
}
```

### 2. Lancer l'Analyse

Exécutez le script principal :

```bash
python main.py
```

Le script va :
*   Charger les vidéos depuis `VIDEO_RESEAU_1`.
*   Traiter chaque frame pour détecter et suivre les objets.
*   Vérifier la présence d'objets dans les zones d'alerte définies.
*   Afficher la progression dans la console.
*   Générer automatiquement un résumé des objets détectés.

### 3. Analyser les Résultats

Une fois l'analyse terminée, consultez le dossier `RESULTATS_DRSI_11` :

*   **Vidéos annotées** : `annotated_*.mp4` - Vous verrez les objets détectés avec leurs ID et une marque rouge s'ils sont en alerte.
*   **Trajectoires par vidéo** : `donnees_*.csv` - Fichiers contenant l'historique complet des détections pour chaque vidéo.
    *   Colonnes : `camera`, `frame`, `id`, `class_name`, `x_center`, `y_center`, `alerte`
*   **Résumé global** : `object_summary.csv` - Fichier récapitulatif avec :
    *   Statistiques globales (toutes vidéos confondues)
    *   Nombre d'apparitions par classe d'objet
    *   Nombre d'objets uniques par classe
    *   Statistiques détaillées par vidéo

## Personnalisation

*   **Modèles** : Vous pouvez changer les modèles utilisés dans `config.py` (variables `YOLO_MODEL_PATH` et `REID_MODEL_PATH`) pour utiliser d'autres versions de YOLO (ex: `yolov8n.pt` pour plus de rapidité, `yolo11x.pt` pour plus de précision).
*   **Paramètres de Tracking** : Modifiez `custom_tracker.yaml` pour ajuster la sensibilité du suivi. Augmentez `track_buffer` pour un suivi plus persistant.
*   **Seuil de Similarité** : Ajustez `SIMILARITY_THRESHOLD` dans `config.py` pour contrôler la sensibilité de la réidentification (0.0 à 1.0).

## Suivi d'Objets Amélioré

Le système utilise plusieurs techniques pour un tracking robuste :

1. **Tracking Local** : BotSort avec ReID pour suivre les objets frame par frame dans une vidéo
2. **Tracking Global** : Système de réidentification par similarité cosinus pour suivre les objets entre plusieurs vidéos
3. **Track Buffer Étendu** : Configuration optimisée pour maintenir les tracks même après occlusion temporaire
4. **Visualisation Interactive** : Appuyez sur 's' pendant la lecture pour cibler un objet spécifique et le suivre en temps réel

## Notes Techniques

*   Le traitement parallèle permet d'analyser plusieurs vidéos simultanément
*   Les IDs globaux sont partagés entre tous les processus pour un suivi cohérent
*   Les embeddings ReID permettent de réidentifier les objets même après perte temporaire
*   Le système génère automatiquement des statistiques détaillées à la fin du traitement
