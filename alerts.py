"""
Module de gestion des alertes pour les zones surveillées.
Vérifie si les objets détectés entrent dans les zones d'alerte définies.
"""

def is_in_zone(box, zones):
    """
    Vérifie si le centre d'une boîte englobante est dans une des zones définies.
    
    Args:
        box (tuple): (x, y, w, h) - coordonnées du centre et dimensions
        zones (list): Liste de zones [[x1, y1, x2, y2], ...]
    
    Returns:
        bool: True si l'objet est dans une zone, False sinon
    """
    x, y, w, h = box
    center_x, center_y = x, y  # x et y sont déjà les coordonnées du centre
    
    # Vérifier chaque zone
    for zone in zones:
        x1, y1, x2, y2 = zone
        if x1 < center_x < x2 and y1 < center_y < y2:
            return True
    return False
