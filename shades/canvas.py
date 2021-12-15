import numpy as np
from PIL import Image
from random import randint
from utils import *


def Canvas(height=700, width=700, color=(240, 240, 240), color_mode='RGB'):
    """
    Returns an blank image to draw on.

    Parameters:
    height (int): Height of the image in pixels. Defaults to 700.
    width (int): Width of the image in pixels. Defaults to 700.
    color (tuple): Desired RGB of the background. Defaults to 240 mono-grey.

    Returns:
    PIL Image
    """
    image = Image.new(color_mode, (int(height), int(width)), color_clamp(color))
    # adding methods or state is pretty restricted by PIL design
    # but a couple of QOL object variables
    image.x_center = int(image.width/2)
    image.y_center = int(image.height/2)
    image.center = (image.x_center, image.y_center)
    return image

def random_point(canvas):
    """
    Returns a random set of coordinates on an image.

    Paramters:
    canvas (PIL Image): Image on which to find random point

    Returns:
    Tuple of ints
    """
    return (randint(0, canvas.width), randint(0, canvas.height))

def pixel_sort(canvas, key=sum, interval=None):
    """
    Returns sorted version of canvas

    Parameters:
    canvas (PIL Image)
    key (function): key to sort pixels by, defaults to sum

    Returns:
    PIL Image
    """
    if interval is None:
        interval = canvas.height
    canvas_array = np.array(canvas)
    pixels = canvas_array.reshape(
        canvas.width * canvas.height,
        len(canvas_array[0][0])
    )
    splits = int(len(pixels) / interval)
    intervals = np.array_split(pixels, splits)
    intervals = np.array([sorted(i, key=key) for i in intervals])
    pixels = intervals.reshape(canvas.width, canvas.height, len(canvas_array[0][0]))
    return Image.fromarray(pixels)

def shuffle(canvas, x_grids, y_grids):
    """
    Segments the canvas into a grid, and switches the sections of the grid

    TODO: lets dummy this function, but getting it to swap to halfs first
    """
    pass
