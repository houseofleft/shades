from .canvas import *
from .noise_fields import *
from .inks import *
from .utils import *

canvas = Canvas()
ink = NoiseGradient(noise_fields=noise_fields(scale=0.1))

ink.fill(canvas)
canvas.show()
