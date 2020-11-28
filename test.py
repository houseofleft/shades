import shades
from PIL import Image
import random

canvas = shades.Canvas(50, 50)
shade = shades.DomainWarpingGradient(color=(200,200,250))

shade.fill(canvas)

canvas.show()
