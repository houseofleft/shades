from canvas import *
from noise_fields import *
from inks import *
from utils import *


canvas = Canvas(color_mode='RGB', height=1000, width=1000)
ink = NoiseGradient((200, 200, 200), noise_fields=noise_fields(scale=0.002))

import random
for i in range(3):
    ink.circle(canvas, random_point(canvas), random.randint(200, 600))

canvas = pixel_sort(canvas, interval=500)

canvas.show()
