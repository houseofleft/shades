import numpy as np
from PIL import Image
from random import randint, shuffle
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
    image = Image.new(color_mode, (int(height), int(width)),
                      color_clamp(color))
    # adding methods or state is pretty restricted by PIL design
    # but a couple of QOL object variables
    image.x_center = int(image.width/2)
    image.y_center = int(image.height/2)
    image.center = (image.x_center, image.y_center)
    image.random_point = lambda: (
        randint(0, image.width), randint(0, image.height)
    )
    return image


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
        interval = canvas.height * canvas.width
    canvas_array = np.array(canvas)
    pixels = canvas_array.reshape(
        canvas.width * canvas.height,
        len(canvas_array[0][0])
        )
    splits = int(len(pixels) / interval)
    intervals = np.array_split(pixels, splits)
    intervals = np.array([sorted(i, key=key) for i in intervals])
    pixels = intervals.reshape(
        canvas.width, canvas.height, len(canvas_array[0][0]))
    return Image.fromarray(pixels)


def grid_shuffle(canvas, x_grids, y_grids):
    """
    Segments the canvas into a grid, and switches the sections of the grid
    TODO: lets dummy this function, but getting it to swap to halfs first
    """
    # first off, we need to find some basics like the grid size
    x_size = int(canvas.width / x_grids)
    y_size = int(canvas.height / y_grids)
    # and maybe let's make a list of all the grid corners?
    corners = []
    for x in range(0, canvas.width - x_size + 1, x_size):
        for y in range(0, canvas.height - y_size + 1, y_size):
            corners.append((x, y))
    # now shuffle
    shuffle(corners)
    # now iterate through in pairs swapping pixels
    # at the moment the below will error if there's an odd number
    for i in range(0, len(corners), 2):
        corner_a = corners[i]
        try:
            corner_b = corners[i+1]
        except IndexError:
            corner_b = corners[0]

        for x in range(x_size):
            for y in range(y_size):
                a_coords = (corner_a[0] + x, corner_a[1] + y)
                b_coords = (corner_b[0] + x, corner_b[1] + y)
                # now swap the pixels
                try:
                    a_val = canvas.getpixel(a_coords)
                    canvas.putpixel(a_coords, canvas.getpixel(b_coords))
                    canvas.putpixel(b_coords, a_val)
                except:
                    import pdb
                    pdb.set_trace()

    return canvas
