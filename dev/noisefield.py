import numpy as np
import matplotlib.pyplot as plt

class NoiseField():
    def __init__(self, scale=0.3, size=2, seed=0):
        self.seed = seed
        self.scale = scale
        self.width = size
        self.height = size
        self.lin = np.linspace(0, size*self.scale, size, endpoint=False)
        x, y = np.meshgrid(self.lin, self.lin)
        self.field = self.perlin_field(x, y, self.seed)

    def extend_field(self, n, where='right', debug=False):
        # how big are we so far?
        size = max(len(self.field[0]), len(self.field))
        # how big do we need to go?
        new_size = size + n
        # new linear space
        new_lin = np.linspace(0, new_size*self.scale, new_size, endpoint=False)
        x, y = np.meshgrid(new_lin, new_lin)
        try:
            if where == 'right':
                # right slice
                x_length = len(self.field[0])
                y_length = len(self.field)
                new_section = self.perlin_field(x[:y_length,x_length:x_length+n], y[:y_length,x_length:x_length+n], self.seed)
                if debug:
                    import pdb; pdb.set_trace()
                self.field = np.concatenate([self.field, new_section], axis=1)
            elif where == 'bottom':
                # bottom slice
                x_length = len(self.field[0])
                y_length = len(self.field)
                new_section = self.perlin_field(x[y_length:y_length+n,:x_length], y[y_length:y_length+n,:x_length], self.seed)
                self.field = np.concatenate([self.field, new_section], axis=0)
        except Exception as e:
            print(e)
            import pdb; pdb.set_trace()


    def perlin_field(self, x, y, seed=0):
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
        n00 = self.gradient(p[p[xi] + yi], xf, yf)
        n01 = self.gradient(p[p[xi] + yi + 1], xf, yf - 1)
        n11 = self.gradient(p[p[xi + 1] + yi + 1], xf - 1, yf - 1)
        n10 = self.gradient(p[p[xi + 1] + yi], xf - 1, yf)
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

test = NoiseField()
test.extend_field(1)
test.extend_field(4, where='bottom')
