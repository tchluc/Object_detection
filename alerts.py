"""
Module de gestion des alertes pour les zones surveillées.
Vérifie si les objets détectés entrent dans les zones d'alerte définies.
Supporte les zones rectangulaires et polygonales.
"""

import cv2
import numpy as np


def is_in_zone(box, zones):
    """
    Vérifie si le centre d'une boîte englobante est dans une des zones définies.
    Supporte les zones rectangulaires [x1, y1, x2, y2] et polygonales (liste de points).
    
    Args:
        box (tuple): (x, y, w, h) - coordonnées du centre et dimensions
        zones (list): Liste de zones rectangulaires [[x1, y1, x2, y2], ...] 
                      ou polygonales [[(x1,y1), (x2,y2), ...], ...]
    
    Returns:
        bool: True si l'objet est dans une zone, False sinon
    """
    x, y, w, h = box
    center_x, center_y = x, y  # x et y sont déjà les coordonnées du centre
    
    # Vérifier chaque zone
    for zone in zones:
        if len(zone) == 4 and not isinstance(zone[0], (list, tuple)):
            # Zone rectangulaire simple [x1, y1, x2, y2]
            x1, y1, x2, y2 = zone
            if x1 < center_x < x2 and y1 < center_y < y2:
                return True
        else:
            # Zone polygonale [(x1,y1), (x2,y2), ...]
            if is_point_in_polygon((center_x, center_y), zone):
                return True
    
    return False


def is_point_in_polygon(point, polygon):
    """
    Vérifie si un point est à l'intérieur d'un polygone (algorithme ray casting).
    
    Args:
        point (tuple): (x, y) coordonnées du point
        polygon (list): Liste de points [(x1,y1), (x2,y2), ...] définissant le polygone
    
    Returns:
        bool: True si le point est dans le polygone, False sinon
    """
    # Convertir en format numpy pour utiliser cv2.pointPolygonTest
    polygon_np = np.array(polygon, dtype=np.int32)
    result = cv2.pointPolygonTest(polygon_np, point, False)
    return result >= 0  # >= 0 signifie à l'intérieur ou sur le bord


def draw_zones(frame, zones, color=(0, 0, 255), thickness=2):
    """
    Dessine les zones d'alerte sur une frame.
    Supporte les rectangles et les polygones.
    
    Args:
        frame (np.array): Image sur laquelle dessiner
        zones (list): Liste de zones (rectangles ou polygones)
        color (tuple): Couleur BGR
        thickness (int): Épaisseur du trait
    
    Returns:
        np.array: Frame avec les zones dessinées
    """
    for zone in zones:
        if len(zone) == 4 and not isinstance(zone[0], (list, tuple)):
            # Rectangle [x1, y1, x2, y2]
            cv2.rectangle(frame, (zone[0], zone[1]), (zone[2], zone[3]), color, thickness)
        else:
            # Polygone [(x1,y1), (x2,y2), ...]
            pts = np.array(zone, dtype=np.int32)
            cv2.polylines(frame, [pts], isClosed=True, color=color, thickness=thickness)
    
    return frame
