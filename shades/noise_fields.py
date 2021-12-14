from abc import ABC, abstractmethod
import random
import numpy as np
from PIL import Image
from opensimplex import OpenSimplex


class NoiseField:
    """
    An object to return perlin noise from xy coordinates.


    Intitialisation Parameters:
    scale (float): how much noise will vary between coordiantes, for normal effects use 0-1 ranges. Defaults to 0.2
    seed (int): intitial seed for noise. Defaults to random generation
    """

    def __init__(self, scale=0.02, seed=None):
        if seed == None:
            self.simplex = OpenSimplex(random.randint(0,999999))
        else:
            self.simplex = OpenSimplex(int(seed))
        self.scale = scale

    def noise(self, xy):
        """
        Return the simplex noise of 2d coordinates

        Parameters:
        xy (iterable of 2 ints): x and y coordinates

        Returns:
        float: noise from xy coordinates (between 0 and 1)
        """
        return (self.simplex.noise2d(xy[0]*self.scale,xy[1]*self.scale)+1)/2


    def recursive_noise(self, xy, depth=1, feedback=0.7):
        """Returns domain warped recursive simplex noise (number between 0 and 1) from xy coordinates.

        Parameters:
        xy (iterable of 2 ints): x and y coordinates
        depth (int): Number of times recursive call is made. Defaults to 1.
        feedback (float): Size of warping affect of recursive noise, for normal effects use 0-1 ranges. Defaults to 0.7.

        Returns:
        float: noise from xy coordinates (between 0 and 1)
        """

        if depth <= 0:
            return self.noise(xy)
        else:
            return self.noise(
                (
                    (xy[0] * self.scale + self.recursive_noise(xy, depth - 1, feedback) * (feedback*300)),
                    (xy[1] * self.scale + self.recursive_noise(xy, depth - 1, feedback) * (feedback*300))
                )
            )


