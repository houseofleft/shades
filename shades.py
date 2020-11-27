from PIL import Image
from abc import ABC, abstractmethod
import random
from perlin_noise import PerlinNoise

def color_clamp(number):
    return max(min(int(number),255),0)

class NoiseField:
    """
    # An object to return perlin noise from xy coordinates.


    Intitialisation Parameters:
    scale (float): how much noise will vary between coordiantes, for normal effects use 0-1 ranges. Defaults to 0.5
    seed (int): intitial seed for noise. Defaults to random generation
    """

    def __init__(self, scale=0.5, seed=None):
        self.perlin_noise = PerlinNoise(octaves = scale*50, seed = seed)

    def noise(self, xy):
        """Return the perlin noise of 2d coordinates

        Parameters:
        xy (iterable of 2 ints): x and y coordinates

        Returns:
        float: noise from xy coordinates (between 0 and 1)

        """

        return self.perlin_noise((xy[0]/1000,xy[1]/1000))

    def recursive_noise(self, xy, depth=1, feedback=0.5):
        """Returns domain warped recursive perlin noise (number between 0 and 1) from xy coordinates.

        Parameters:
        xy (iterable of 2 ints): x and y coordinates
        depth (int): Number of times recursive call is made. Defaults to 1.
        feedback (float): Size of warping affect of recursive noise, for normal effects use 0-1 ranges. Defaults to 0.5.

        Returns:
        float: noise from xy coordinates (between 0 and 1)

        """

        if depth <= 0:
            return self.noise(xy)
        else:
            return self.noise((xy[0]+self.recursive_noise(xy, depth-1, feedback)*feedback*200,xy[1]+self.recursive_noise(xy, depth -1, feedback)*feedback*200))

class Shade(ABC):

    def __init__(self, color=(0,0,0), transparency=0, warp_noise=(NoiseField(),NoiseField()), warp_size=0):
        self.color = color
        self.transparency = transparency
        self.warp_noise = warp_noise
        self.warp_size = warp_size

    @abstractmethod
    def determine_shade(self, xy):
        '''determines the color for xy coordiantes based on shade.
        arguments:
            xy: xy coordinates in the form of a tuple (x,y)
            canvas: a PIL image'''
        return color

    def apply_transparency(self, xy, canvas, color):
        '''if transparency settings are applied, appropriately adjusts color
        argument:
            xy: xy coordinates in the form of a tuple (x,y)
            canvas: a PIL image
            color: initial color before transparency has been applied'''
        initial_color = canvas.getpixel((int(xy[0]),int(xy[1])))
        new_color = [int(initial_color[i] + ((color[i] - initial_color[i]) * (1-self.transparency))) for i in range(0,3)]
        return tuple(new_color)

    def adjust_point(self, xy):
        '''if warp is applied, appropriately adjusts location of pont
        arguments:
            xy: xy coordinates in the form of a tuple (x,y)'''
        x = xy[0] + (self.warp_noise[0].noise(xy) * self.warp_size)
        y = xy[1] + (self.warp_noise[1].noise(xy) * self.warp_size)
        return (x,y)


    def point(self, xy, canvas):
        '''determines colour and marks a point on an image.
        takes as arguments:
            xy: xy coordinates in the form of a tuple (x,y)
            canvas: a PIL image'''
        color = self.determine_shade(xy)
        color = self.apply_transparency(xy, canvas, color)
        if self.warp_size != 0:
            xy = self.adjust_point(xy)
        canvas.putpixel(xy, color)

    def fill(self, canvas):
        '''fills the entire image with color.
        takes as arguments:
            canvas: a PIL image'''
        # we'll temporarily turn off warping as it isn't needed here
        warp_size_keeper = self.warp_size
        self.warp_size = 0
        for x in range(0,canvas.width):
            for y in range(0,canvas.height):
                self.point((x,y), canvas)
        self.warp_size = warp_size_keeper

    def rectangle(self, canvas, xy, width, height):
        for x in range(int(xy[0]), int(xy[0] + width)):
            for y in range(int(xy[1]), int(xy[1] + height)):
                self.point((x,y), canvas)

    def circle(self, canvas, xy, radius):
        for h in range(0, int(radius)):
            circumfurence = radius * 2 * math.pi
            for c in [x for x in range(0, (int(circumfurence)+1))]:
                angle = (c/circumfurence) * 360
                opposite = math.sin(math.radians(angle)) * h
                adjacent = math.cos(math.radians(angle)) * h
                self.point((xy[0] + adjacent, xy[1] + opposite), canvas)

    def line(self, canvas, xy1, xy2):
        # first figuring out which is biggest distance, that step will be one
        # this is so that line is iterated through in distances of one pixel
        if abs(xy1[0] - xy2[0]) > abs(xy[1] - xy2[1]):
            if xy1[0] > xy2[0]:
                x_step = -1
            else:
                x_step = 1
            y_step = ( abs(xy1[1] - xy2[1]) / abs(xy1[0] - xy2[0]) )
            if xy1[1] > xy2[1]:
                y_step *= -1
            istop = abs(xy1[0] - xy2[0])
        else:
            if xy1[1] > xy2[1]:
                y_step = -1
            else:
                y_step = 1
            x_step = (abs(xy1[0]-xy2[0])/abs(xy1[1]-xy2[1]))
            if xy1[0] > xy2[0]:
                x_step *= 1
            istop = abs(xy1[1]-xy2[1])
        x = xy1[0]
        y = xy1[1]
        for i in range(0, int(istop)):
            self.point((x,y), canvas)
            x += x_step
            y += y_step

class BlockColor(Shade):

    def determine_shade(self, xy):
        return self.color

class NoiseGradient(Shade):

    def __init__(self, color=(0,0,0), transparency=0, warp_noise=NoiseField(), warp_size=0, color_variance=70, noise_fields=[NoiseField() for i in range(3)]):
        super().__init__(color, transparency, warp_noise, warp_size)
        self.color_variance = color_variance
        self.noise_fields = tuple(noise_fields)

    def determine_shade(self, xy):
        color = [0,0,0]
        for i in range(0,3):
            noise = self.noise_fields[0].noise(xy) - 0.5
            color_affect = noise * (2*self.color_variance)
            color[i] = self.color[i] + color_affect
            color[i] = color_clamp(color[i])
        return tuple(color)

class DomainWarpingGradient(Shade):

    def __init__(self, color=(0,0,0), transparency=0, warp_noise=NoiseField(), warp_size=0, color_variance=70, noise_fields=[NoiseField() for i in range(3)], depth=1, feedback=0.5):
        super().__init__(color, transparency, warp_noise, warp_size)
        self.noise_fields = tuple(noise_fields)

    def determine_shade(self, xy):
        color = [0,0,0]
        for i in range(0,3):
            noise = self.noise_fields[0].recursive_noise(xy, depth, feedback) - 0.5
            color_affect = noise * (2*color_variance)
            color[i] = self.color[i] + color_affect
            color[i] = color_clamp(color[i])
        return tuple(color)

