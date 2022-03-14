from abc import ABC, abstractmethod
import random
import math
import numpy as np
from scipy.interpolate import griddata
from PIL import Image
from scipy.ndimage import zoom
from opensimplex import OpenSimplex


class NoiseField:
    """
    An object to return perlin noise from xy coordinates.


    Intitialisation Parameters:
    scale (float): how much noise will vary between coordiantes, for normal effects use 0-1 ranges. Defaults to 0.2
    seed (int): intitial seed for noise. Defaults to random generation
    """

    def __init__(self, scale=0, seed=None, limit=1200):
        if seed is None:
            np.random.seed(random.randint(0, 9999999))
        else:
            np.random.seed(seed)
        self.scale = scale
        if self.scale == 0:
            self.field = np.zeros((limit, limit))
        else:
            self.field = self._create_noise_field(limit)

    def _create_noise_field(self, limit):
        # majority of the below code is from:
        # https://github.com/pvigier/perlin-numpy
        # avoiding rounding errors
        limit = math.ceil(limit / 120) * 120
        shape = (limit, limit)
        factors = [1, 2, 3, 4, 5, 6, 8, 10, 12, 15, 20, 24, 30, 40, 60, 120]
        res = factors[math.floor(self.scale * len(factors))]
        res = (res, res)
        delta = (res[0] / shape[0], res[1] / shape[1])
        d = (shape[0] // res[0], shape[1] // res[1])
        grid = np.mgrid[0:res[0]:delta[0], 0:res[1]:delta[1]].transpose(1, 2, 0) % 1
        # Gradients
        angles = 2*np.pi*np.random.rand(res[0]+1, res[1]+1)
        gradients = np.dstack((np.cos(angles), np.sin(angles)))
        g00 = gradients[0:-1, 0:-1].repeat(d[0], 0).repeat(d[1], 1)
        g10 = gradients[1:, 0:-1].repeat(d[0], 0).repeat(d[1], 1)
        g01 = gradients[0:-1, 1:].repeat(d[0], 0).repeat(d[1], 1)
        g11 = gradients[1:, 1:].repeat(d[0], 0).repeat(d[1], 1)
        # Ramps
        n00 = np.sum(grid * g00, 2)
        n10 = np.sum(np.dstack((grid[:, :, 0]-1, grid[:, :, 1])) * g10, 2)
        n01 = np.sum(np.dstack((grid[:, :, 0], grid[:, :, 1]-1)) * g01, 2)
        n11 = np.sum(np.dstack((grid[:, :, 0]-1, grid[:, :, 1]-1)) * g11, 2)
        # Interpolation
        t = 6*grid**5 - 15*grid**4 + 10*grid**3
        n0 = n00*(1-t[:, :, 0]) + t[:, :, 0]*n10
        n1 = n01*(1-t[:, :, 0]) + t[:, :, 0]*n11
        field = np.sqrt(2)*((1-t[:, :, 1])*n0 + t[:, :, 1]*n1)
        field = (field + 1) / 2
        return field

    def noise(self, xy):
        """
        Return the simplex noise of 2d coordinates

        Parameters:
        xy (iterable of 2 ints): x and y coordinates

        Returns:
        float: noise from xy coordinates (between 0 and 1)
        """
        try:
            return self.field[xy[0]][xy[1]]
        except:
            import pdb
            pdb.set_trace()

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
                    (xy[0] * self.scale + self.recursive_noise(xy,
                     depth - 1, feedback) * (feedback*300)),
                    (xy[1] * self.scale + self.recursive_noise(xy,
                     depth - 1, feedback) * (feedback*300))
                )
            )


def noise_fields(scale=0.02, seed=None, channels=3):
    """
    Create multiple NoiseField objects in one go.
    This is because there are lots of uses where you will need one noise field for each (e.g) axis or color channel

    Parameters:
    scale (float or iterable of floats): Scale for all noise objects, or one for each
    seed (int or iterable of ints): Random seed for all noies objects, or one for each
    channels (int): Number of NoiseFields to return in a list

    Returns:
    iterable of NoiseFields
    """

    if not isinstance(scale, list):
        scale = [scale for i in range(channels)]
    if not isinstance(seed, list):
        seed = [seed for i in range(channels)]

    return [NoiseField(scale=scale[i], seed=seed[i]) for i in range(channels)]
