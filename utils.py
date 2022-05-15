from random import choice
from pathlib import Path

from PIL import Image, ImageColor

Image.MAX_IMAGE_PIXELS = None

COLOR_MAP = list(ImageColor.colormap.keys())
IMAGE_FOLDER_NAME = "images"


def prepare_folder() -> None:
    """
    Function that creates image folder or remove all images from it
    :return: None
    """
    path = Path(IMAGE_FOLDER_NAME)
    if not path.exists():
        path.mkdir()
    elif files_path := path.glob("*"):
        for file_path in files_path:
            file_path.unlink()


def draw_image(folder: Path, color: str) -> None:
    """
    Function generates one image with size 10000x10000 pixels with given color
    :param folder: folder where save image
    :param color: color of image
    :return: None
    """
    img = Image.new("RGB", (10000, 10000), color)
    img.save(folder / f"{color}.png")


def update_image(image: Image.Image) -> None:
    """
    Function that takes image and inserts inside another image
    :param image:
    :return:
    """
    thumb_size = image.width // 2, image.height // 2
    small_image_path = choice(
        [
            path
            for path in Path(image.filename).parent.glob("*")
            if image.filename not in str(path)
        ]
    )
    small_image = Image.open(small_image_path).resize(thumb_size)
    x1 = thumb_size[0] // 2
    x2 = thumb_size[0] + x1
    y1 = thumb_size[1] // 2
    y2 = thumb_size[1] + y1
    image.paste(small_image, box=(x1, y1, x2, y2))
    image.save(image.filename)
