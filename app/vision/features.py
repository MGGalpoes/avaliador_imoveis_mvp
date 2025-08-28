from typing import List, Optional
from PIL import Image, ImageStat
import numpy as np
import os

def _brightness(img: Image.Image) -> float:
    # converte para L (grayscale) e calcula média normalizada
    gray = img.convert('L')
    stat = ImageStat.Stat(gray)
    return stat.mean[0] / 255.0

def _sharpness(img: Image.Image) -> float:
    # aproximar nitidez pela variância do gradiente (Sobel-like)
    gray = np.asarray(img.convert('L'), dtype=np.float32) / 255.0
    # kernels simples
    kx = np.array([[1, 0, -1],
                   [2, 0, -2],
                   [1, 0, -1]], dtype=np.float32)
    ky = np.array([[1, 2, 1],
                   [0, 0, 0],
                   [-1, -2, -1]], dtype=np.float32)
    gx = _convolve2d(gray, kx)
    gy = _convolve2d(gray, ky)
    mag = np.sqrt(gx*gx + gy*gy)
    return float(np.clip(np.var(mag) * 4.0, 0.0, 1.0))  # normalização simples

def _convolve2d(img: np.ndarray, kernel: np.ndarray) -> np.ndarray:
    kh, kw = kernel.shape
    pad_h, pad_w = kh//2, kw//2
    padded = np.pad(img, ((pad_h, pad_h), (pad_w, pad_w)), mode='edge')
    out = np.zeros_like(img)
    for i in range(img.shape[0]):
        for j in range(img.shape[1]):
            region = padded[i:i+kh, j:j+kw]
            out[i, j] = np.sum(region * kernel)
    return out

def photo_quality_score(path: str) -> Optional[float]:
    try:
        with Image.open(path) as im:
            im = im.copy().resize((512, 512))
        b = _brightness(im)
        s = _sharpness(im)
        # Combinação simples: peso maior para nitidez
        score = 0.35 * b + 0.65 * s
        return float(np.clip(score, 0.0, 1.0))
    except Exception:
        return None

def photos_score(paths: List[str]) -> float:
    scores = []
    for p in paths:
        if p and os.path.exists(p):
            sc = photo_quality_score(p)
            if sc is not None:
                scores.append(sc)
    if not scores:
        return 0.5  # neutro
    return float(np.clip(sum(scores) / len(scores), 0.0, 1.0))
