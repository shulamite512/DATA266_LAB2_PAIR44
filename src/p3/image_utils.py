import os

import numpy as np
from PIL import Image, ImageOps, UnidentifiedImageError


def load_and_validate(path, min_side=64, blank_std=4.0):
    """Return (PIL image or None, problem string). Never raises."""
    if not path:
        return None, "no image provided"
    if not os.path.exists(path):
        return None, f"file not found: {os.path.basename(path)}"
    if os.path.getsize(path) == 0:
        return None, "the file is empty (0 bytes)"
    try:
        img = Image.open(path)
        img.load()
        img = ImageOps.exif_transpose(img).convert("RGB")
    except (UnidentifiedImageError, OSError, ValueError, SyntaxError) as e:
        return None, f"the file is not a readable image ({type(e).__name__})"
    if min(img.size) < min_side:
        return None, f"the image is too small ({img.size[0]}x{img.size[1]}); please upload at least {min_side}px"
    arr = np.asarray(img.convert("L"), dtype=np.float32)
    if arr.std() < blank_std:
        return None, "the image is blank or almost uniform, so there is nothing to describe or edit"
    return img, ""


def to_512(img):
    return ImageOps.fit(img, (512, 512), Image.BICUBIC)
