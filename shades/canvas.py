from abc import ABC, abstractmethod
import random
import numpy as np
from PIL import Image
from opensimplex import OpenSimplex
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
    return Image.new('RGB', (int(height), int(width)), color_clamp(color))
