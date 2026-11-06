def read(image, at):
    h, w = image.shape[:2]
    return [{"x": 0, "y": 0, "px": [w // 2, h // 2], "note": f"size {w}x{h}"}]
