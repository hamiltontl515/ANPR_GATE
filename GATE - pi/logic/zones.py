def get_zone(bbox, frame_shape):
    """
    Simple zone split:
    left side = ENTRY
    right side = EXIT
    """

    x1, y1, x2, y2 = bbox
    frame_w = frame_shape[1]

    center_x = (x1 + x2) // 2

    if center_x < frame_w // 2:
        return "ENTRY"
    else:
        return "EXIT"