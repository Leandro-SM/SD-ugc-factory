"""Face detection (OpenCV Haar) — lightweight, no extra downloads."""
import cv2
import numpy as np
from PIL import Image


def detect_face_box(image: Image.Image) -> tuple[int, int, int, int] | None:
    """Return (x, y, w, h) of largest face, or None."""
    arr = np.array(image.convert("RGB"))
    gray = cv2.cvtColor(arr, cv2.COLOR_RGB2GRAY)
    cascade = cv2.CascadeClassifier(
        cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    )
    faces = cascade.detectMultiScale(
        gray, scaleFactor=1.1, minNeighbors=5, minSize=(60, 60)
    )
    if len(faces) == 0:
        return None
    faces = sorted(faces, key=lambda f: f[2] * f[3], reverse=True)
    x, y, w, h = faces[0]
    return int(x), int(y), int(w), int(h)
