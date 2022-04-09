import numpy as np
import matplotlib.pyplot as plt
import pdb

# axis 1 is x
# axis 0 is y
class NoiseField():
    def __init__(self, scale=0.3, size=2, seed=0):
        self.seed = seed
        self.scale = scale
        self.width = size
        self.height = size
        self.lin_start = 0
        self.lin = np.linspace(0, (size*self.scale), size, endpoint=False)
        x, y = np.meshgrid(self.lin, self.lin)
        self.field = self.perlin_field(x, y, self.seed)
        self.negative_padding = 0

    def extend_field_back(self, n):
        size = max(len(self.field[0]), len(self.field))
        linspace = np.linspace(
            -n*self.scale,
            size*self.scale,
            size+n,
            endpoint=False,
        )
        self.lin_start -= n * self.scale
        x, y = np.meshgrid(linspace, linspace)
        x_length = len(self.field[0])
        y_length = len(self.field)
        new_section = self.perlin_field(
            # we're adding on x/axis1 so
            # we need from 0 to n on the x axis
            # then we need (before negative padding added)
            # from n to n + y_length
            # y is first for some stupid reason
            x[n:n+y_length,:n],
            y[n:n+y_length,:n],
            self.seed,
        )
        self.field = np.concatenate([new_section, self.field], axis=1)
        self.negative_padding += n

    def extend_field(self, n, axis=0, debug=False):
        # how big are we so far?
        size = max(len(self.field[0]), len(self.field))
        # how big do we need to go?
        new_size = size + n
        new_lin = np.linspace(
            self.lin_start,
            self.lin_start + (new_size*self.scale),
            new_size,
            endpoint=False,
        )
        x, y = np.meshgrid(new_lin, new_lin)
        if axis == 1:
            # right slice
            x_length = len(self.field[0])
            y_length = len(self.field)
            new_section = self.perlin_field(x[:y_length,x_length:x_length+n], y[:y_length,x_length:x_length+n], self.seed)
            self.field = np.concatenate([self.field, new_section], axis=1)
        else:
            # bottom slice
            x_length = len(self.field[0])
            y_length = len(self.field)
            new_section = self.perlin_field(
                x[y_length + self.negative_padding : y_length + n + self.negative_padding,
                  self.negative_padding : x_length + self.negative_padding],
                y[y_length + self.negative_padding : y_length + n + self.negative_padding,
                  self.negative_padding : x_length + self.negative_padding],
                self.seed,
            )
            self.field = np.concatenate([self.field, new_section], axis=0)
        if debug:
            pdb.set_trace()


    def perlin_field(self, x, y, seed=0):
        """
        generate field from x and y grids
        """
        x %= 512
        y %= 512
        # permutation table
        np.random.seed(seed)
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
        return self.lerp(x1, x2, v)

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

    def show(self):
        plt.imshow(self.field, origin='upper')
        plt.show()


test = NoiseField(scale=0.09)
test.extend_field(100, axis=0)
test.show()
test.extend_field_back(100)
test.show()
test.extend_field(100, axis=0, debug=True)
test.show()
test.extend_field(100, axis=1)
test.show()

# so it looks like after negative paddings added
# bottom is now adding on the top part of the picture to the bottom
# bottom works well until negative padding is added
# so somethings clearly happening there

# doing some diagnostics, looks like left is using the same linear space EVERY time (rather than moving backwards further)

# interestingly, it looks FINE adding on the top or left
# but the next after that looks bad! (even if it's not left or top)

# also calling top twice in a row causes a value error

# what about left?
