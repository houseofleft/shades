from PIL import Image
from utils import *


def Canvas(height=700, width=700, color=(240, 240, 240)):
    """
    Returns an blank image to draw on.

    Parameters:
    height (int): Height of the image in pixels. Defaults to 700.
    width (int): Width of the image in pixels. Defaults to 700.
    color (tuple): Desired RGB of the background. Defaults to 240 mono-grey.

    Returns:
    PIL Image
    """
    image = Image.new('RGB', (int(height), int(width)), color_clamp(color))
    # adding methods or state is pretty restricted by PIL design
    # but a couple of QOL object variables
    image.x_center = int(image.width/2)
    image.y_center = int(image.height/2)
    image.center = (image.x_center, image.y_center)
    return image
