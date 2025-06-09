import os
import logging
from PIL import Image, ImageDraw

logger = logging.getLogger(__name__)

AVATAR_DIR = os.path.join(os.path.dirname(__file__), '..', 'static')


def generate_triangle_avatar(name: str, size: int = 150, color: str = "blue") -> str:
    """Generate a simple triangular avatar image and return its file path."""
    os.makedirs(AVATAR_DIR, exist_ok=True)
    path = os.path.join(AVATAR_DIR, f"{name.lower()}.png")
    if os.path.exists(path):
        logger.debug("Avatar for %s already exists: %s", name, path)
        return path
    logger.info("Generating avatar for %s", name)
    img = Image.new("RGBA", (size, size), "white")
    draw = ImageDraw.Draw(img)
    draw.polygon([(size / 2, 10), (10, size - 10), (size - 10, size - 10)], fill=color)
    try:
        img.save(path)
    except Exception as exc:
        logger.error("Failed to save avatar %s: %s", name, exc)
        raise
    return path
