"""
canvas

contains functions/classes relating to Shades' canvas object
"""
from random import randint, shuffle
from typing import List, Callable

import numpy as np

from PIL import Image

from .utils import color_clamp


def Canvas(
        height: int = 700,
        width: int = 700,
        color: List[int] = (240, 240, 240),
        color_mode: str = 'RGB',
    ) -> Image:
    """
    Returns an blank image to draw on.
    A function due to PIL library restrictions
    Although in effect used as class so follows naming conventions
    for color_mode 'RGB' and 'HSB' supported
    ('RGBA' and 'HSBA' accepted, but may produce unexpected results)
    """
    image = Image.new(color_mode, (int(width), int(height)),
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


def pixel_sort(canvas: Image, key: Callable = sum, interval: int = None) -> Image:
    """
    Returns a color sorted version of canvas.
    Accepts a custom function for sorting color tuples in key
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
        canvas.height,
        canvas.width,
        len(canvas_array[0][0]),
    )
    return Image.fromarray(pixels)


def grid_shuffle(canvas: Image, x_grids: int, y_grids: int):
    """
    Returns and image, with grid sections shuffled
    """
    # first off, we need to find some basics like the grid size
    x_size = int(canvas.width / x_grids)
    y_size = int(canvas.height / y_grids)
    # and maybe let's make a list of all the grid corners?
    corners = []
    for x_coord in range(0, canvas.width - x_size + 1, x_size):
        for y_coord in range(0, canvas.height - y_size + 1, y_size):
            corners.append((x_coord, y_coord))
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

        for x_coord in range(x_size):
            for y_coord in range(y_size):
                a_coords = (corner_a[0] + x_coord, corner_a[1] + y_coord)
                b_coords = (corner_b[0] + x_coord, corner_b[1] + y_coord)
                # now swap the pixels
                a_val = canvas.getpixel(a_coords)
                canvas.putpixel(a_coords, canvas.getpixel(b_coords))
                canvas.putpixel(b_coords, a_val)

    return canvas
