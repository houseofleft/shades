import random
import math
import numpy as np


class NoiseField():
    """
    An object to return perlin noise from xy coordinates.


    Intitialisation Parameters:
    scale (float): how much noise will vary between coordiantes, for normal effects use 0-1 ranges. Defaults to 0.2
    seed (int): intitial seed for noise. Defaults to random generation
    """

    def __init__(self, scale=0.002, seed=None):
        if seed is None:
            self.seed = random.randint(0,9999)
        else:
            self.seed = seed
        self.scale = scale
        size = 10
        self.x_lin = np.linspace(0, (size*self.scale), size, endpoint=False)
        self.y_lin = np.linspace(0, (size*self.scale), size, endpoint=False)
        self.field = self.perlin_field(self.x_lin, self.y_lin)
        self.x_negative_buffer = 0
        self.y_negative_buffer = 0
        self.buffer_chunks = 500

    def _roundup(self, x, y):
        return int(math.ceil(x / y)) * y

    def buffer_field_right(self, n):
        # y is just gonna stay the same, but x needs to be picking up
        max_lin = self.x_lin[-1]

        additional_x_lin = np.linspace(
            max_lin+self.scale,
            max_lin+(n*self.scale),
            n,
            endpoint=False,
        )
        self.field = np.concatenate(
            [self.field,
             self.perlin_field(additional_x_lin, self.y_lin)],
            axis=1,
        )
        self.x_lin = np.concatenate([self.x_lin, additional_x_lin])

    def buffer_field_bottom(self, n):
        # this time x is the same, and y is changing
        max_lin = self.y_lin[-1]
        additional_y_lin = np.linspace(
            max_lin+self.scale,
            max_lin+(n*self.scale),
            n,
            endpoint=False,
        )
        self.field = np.concatenate(
            [self.field,
             self.perlin_field(self.x_lin, additional_y_lin)],
            axis=0,
        )
        self.y_lin = np.concatenate([self.y_lin, additional_y_lin])

    def buffer_field_left(self, n):
        # y is just gonna stay the same, and x is changing
        min_lin = self.x_lin[0]
        additional_x_lin = np.linspace(
            min_lin-(n*self.scale),
            min_lin,
            n,
            endpoint=False,
        )
        self.field = np.concatenate(
            [self.perlin_field(additional_x_lin, self.y_lin),
             self.field],
            axis=1,
        )
        self.x_lin = np.concatenate([additional_x_lin, self.x_lin])
        self.x_negative_buffer += n
            
    def buffer_field_top(self, n):
        # x is the same, y is changing
        min_lin = self.y_lin[0]
        additional_y_lin = np.linspace(
            min_lin-(n*self.scale),
            min_lin,
            n,
            endpoint=False,
        )
        self.field = np.concatenate(
            [self.perlin_field(self.x_lin, additional_y_lin),
             self.field],
            axis=0,
        )
        self.y_lin = np.concatenate([additional_y_lin, self.y_lin])
        self.y_negative_buffer += n

    def perlin_field(self, x_lin, y_lin):
        """
        generate field from x and y grids
        """
        # remembering the random state (so we can put it back after)
        initial_random_state = np.random.get_state()
        x, y = np.meshgrid(x_lin, y_lin)
        x %= 512
        y %= 512
        # permutation table
        np.random.seed(self.seed)
        p = np.arange(256, dtype=int)
        np.random.shuffle(p)
        p = np.stack([p, p]).flatten()
        # coordinates of the top-left
        xi, yi = x.astype(int), y.astype(int)
        # internal coordinates
        xf, yf = x - xi, y - yi
        # fade factors
        u, v = self.fade(xf), self.fade(yf)
        # noise components
        n00 = self.gradient(p[(p[xi%512] + yi)%512], xf, yf)
        n01 = self.gradient(p[(p[xi%512] + yi + 1)%512], xf, yf - 1)
        n11 = self.gradient(p[(p[((xi%512)+1)%512] + yi + 1)%512], xf - 1, yf - 1)
        n10 = self.gradient(p[(p[((xi%512)+1)%512] + yi)%512], xf - 1, yf)
        # combine noises
        x1 = self.lerp(n00, n10, u)
        x2 = self.lerp(n01, n11, u)
        # putting the random state back in place
        np.random.set_state(initial_random_state)
        field = self.lerp(x1, x2, v)
        field += 0.5
        return field

    def lerp(self, a, b, x):
        "linear interpolation"
        return a + x * (b - a)

    def fade(self, t):
        "6t^5 - 15t^4 + 10t^3"
        return 6 * t**5 - 15 * t**4 + 10 * t**3

    def gradient(self, h, x, y):
        "grad converts h to the right gradient vector and return the dot product with (x,y)"
        vectors = np.array([[0, 1], [0, -1], [1, 0], [-1, 0]])
        g = vectors[h % 4]
        return g[:, :, 0] * x + g[:, :, 1] * y

    def noise(self, xy):
        if self.scale == 0:
            return 0
        x, y = xy 
        x += self.x_negative_buffer
        y += self.y_negative_buffer
        if x < 0:
            x_to_backfill = self._roundup(abs(x), self.buffer_chunks)
            self.buffer_field_left(x_to_backfill)
            x, y = xy
            x += self.x_negative_buffer
            y += self.y_negative_buffer
        if y < 0:
            y_to_backfill = self._roundup(abs(y), self.buffer_chunks)
            self.buffer_field_top(y_to_backfill)
            x, y = xy
            x += self.x_negative_buffer
            y += self.y_negative_buffer
        try:
            return self.field[y][x]
        except IndexError:
            # ran out of generated noise, so need to extend the field
            height, width = self.field.shape
            x_to_extend = x - width + 1
            y_to_extend = y - height + 1
            if x_to_extend > 0:
                x_to_extend = self._roundup(x_to_extend, self.buffer_chunks)
                self.buffer_field_right(x_to_extend)
            if y_to_extend > 0:
                y_to_extend = self._roundup(y_to_extend, self.buffer_chunks)
                self.buffer_field_bottom(y_to_extend)
            return self.noise(xy)


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
            # do the noise, of the noise, or something?
            hm = int(self.noise(xy) * feedback * 100)
            return self.recursive_noise((hm, hm), depth-1, feedback)
  


def noise_fields(scale=0.02, seed=None, limit=1000, buffer=500, channels=3):
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

    return [NoiseField(scale=scale[i], seed=seed[i], limit=limit, buffer=buffer) for i in range(channels)]
