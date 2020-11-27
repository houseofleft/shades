import shades
from PIL import Image

canvas = Image.new('RGB', (200,200))
shade = shades.NoiseGradient(color=(200,200,200))
shade.fill(canvas)

canvas.show()
