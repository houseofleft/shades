from canvas import *
from noise_fields import *
from inks import *
from utils import *

nice = Canvas(200, 200)
cool = BlockColor()

cool.line(nice, (0, 0), (nice.width, nice.height), 3)

nice.show()
