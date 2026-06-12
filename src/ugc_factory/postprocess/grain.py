"""Film grain + vignette overlay — kills the 'AI look'."""
import numpy as np
from PIL import Image

GRAIN_PRESETS = {
    "off":    0.0,
    "low":    8.0,
    "medium": 14.0,
    "high":   22.0,
}


def add_film_grain(image: Image.Image, intensity: str = "medium") -> Image.Image:
    """Apply photographic grain + subtle vignette."""
    amp = GRAIN_PRESETS.get(intensity, 0.0)
    if amp == 0.0:
        return image

    arr = np.array(image.convert("RGB"), dtype=np.float32)
    h, w, _ = arr.shape

    # Luminance grain (monochromatic, film-like)
    noise = np.random.normal(0, amp, (h, w)).astype(np.float32)
    arr += np.stack([noise, noise, noise], axis=-1)

    # Subtle color grain (10% amplitude)
    arr += np.random.normal(0, amp * 0.1, (h, w, 3)).astype(np.float32)

    arr = np.clip(arr, 0, 255).astype(np.uint8)
    return _vignette(Image.fromarray(arr), strength=0.15)


def _vignette(image: Image.Image, strength: float = 0.15) -> Image.Image:
    arr = np.array(image, dtype=np.float32)
    h, w, _ = arr.shape
    Y, X = np.ogrid[:h, :w]
    cx, cy = w / 2, h / 2
    dist = np.sqrt((X - cx) ** 2 + (Y - cy) ** 2)
    max_dist = np.sqrt(cx ** 2 + cy ** 2)
    mask = (1 - strength * (dist / max_dist) ** 2).astype(np.float32)[..., None]
    arr *= np.clip(mask, 0, 1)
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))
