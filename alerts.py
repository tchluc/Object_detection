def is_in_zone(box, zones):
    """
    Checks if the center of a bounding box is within any of the defined zones.
    
    Args:
        box (tuple): (x, y, w, h) - center coordinates and dimensions.
        zones (list): List of [x1, y1, x2, y2] zones.
    
    Returns:
        bool: True if inside a zone, False otherwise.
    """
    x, y, w, h = box
    center_x, center_y = x, y 
    for zone in zones:
        x1, y1, x2, y2 = zone
        if x1 < center_x < x2 and y1 < center_y < y2:
            return True
    return False
