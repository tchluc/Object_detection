# Projet de Détection et Suivi d'Objets avec Zones d'Alerte

Ce projet utilise l'intelligence artificielle (YOLO) pour détecter, classifier et suivre des objets dans des vidéos de surveillance. Il inclut une fonctionnalité permettant de définir des zones d'alerte et de signaler lorsqu'un objet pénètre dans ces zones.

## Fonctionnalités

*   **Détection et Classification** : Utilise YOLO (YOLOv11) pour identifier différents types d'objets.
*   **Suivi (Tracking)** : Utilise l'algorithme BotSort (configuré via `custom_tracker.yaml`) pour suivre les objets d'une image à l'autre.
*   **Ré-identification (ReID)** : Utilise un modèle de classification secondaire et la similarité cosinus pour conserver l'identité des objets même après une occlusion ou lors du passage d'une caméra à une autre (suivi global).
*   **Zones d'Alerte** : Permet de définir des zones rectangulaires spécifiques pour chaque vidéo. Si un objet entre dans cette zone, une alerte est générée.
*   **Export des Données** : Les trajectoires et les alertes sont sauvegardées dans un fichier CSV.
*   **Visualisation** : Génère des vidéos annotées avec les boîtes englobantes, les identifiants et les indicateurs d'alerte.

## Structure du Projet

*   `detection_classification.py` : Script principal qui effectue le traitement des vidéos.
*   `select_zone.py` : Outil utilitaire pour sélectionner visuellement les zones d'alerte sur une vidéo et récupérer les coordonnées.
*   `custom_tracker.yaml` : Fichier de configuration pour l'algorithme de suivi BotSort.
*   `VIDEO_RESEAU_1/` : Dossier contenant les vidéos d'entrée à analyser.
*   `RESULTATS_DRSI_11/` : Dossier de sortie contenant les résultats (vidéos annotées et fichier CSV).
*   `yolo11m.pt`, `yolo26n-cls.pt`, etc. : Modèles de poids YOLO pré-entraînés.

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

Si vous souhaitez surveiller des zones spécifiques :

1.  Ouvrez `select_zone.py`.
2.  Modifiez la variable `video_name` (ou assurez-vous que le script charge la bonne vidéo automatiquement).
3.  Exécutez le script :
    ```bash
    python select_zone.py
    ```
4.  Une fenêtre s'ouvre. Dessinez un rectangle avec la souris autour de la zone à surveiller.
5.  Les coordonnées s'afficheront dans la console (ex: `[100, 100, 500, 500]`).
6.  Copiez ces coordonnées.
7.  Ouvrez `detection_classification.py` et mettez à jour le dictionnaire `alert_zones` avec le nom de votre fichier vidéo et les coordonnées copiées.

### 2. Lancer l'Analyse

Exécutez le script principal :

```bash
python detection_classification.py
```

Le script va :
*   Charger les vidéos depuis `VIDEO_RESEAU_1`.
*   Traiter chaque frame pour détecter et suivre les objets.
*   Vérifier la présence d'objets dans les zones d'alerte définies.
*   Afficher la progression dans la console.

### 3. Analyser les Résultats

Une fois l'analyse terminée, consultez le dossier `RESULTATS_DRSI_11` :
*   **Vidéos annotées** : Vous verrez les objets détectés avec leurs ID et une marque rouge s'ils sont en alerte.
*   **`donnees_trajectoires.csv`** : Fichier contenant l'historique complet des détections. Colonnes :
    *   `camera` : Nom du fichier vidéo.
    *   `frame` : Numéro de la frame.
    *   `id` : Identifiant unique de l'objet (Global ID).
    *   `class_name` : Type d'objet (ex: person, car).
    *   `x_center`, `y_center` : Position de l'objet.
    *   `alerte` : `1` si l'objet est dans la zone d'alerte, `0` sinon.

## Personnalisation

*   **Modèles** : Vous pouvez changer les modèles utilisés dans `detection_classification.py` (variables `model` et `reid`) pour utiliser d'autres versions de YOLO (ex: `yolov8n.pt` pour plus de rapidité, `yolo11x.pt` pour plus de précision).
*   **Paramètres de Tracking** : Modifiez `custom_tracker.yaml` pour ajuster la sensibilité du suivi.
