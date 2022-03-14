import numpy as np
import matplotlib.pyplot as plt

def _f(t):
    return 6*t**5 - 15*t**4 + 10*t**3

def generate_perlin_noise(width, height, scale):
    shape = (width, height)
    if scale == 0:
        return np.zeros(shape)
    else:
        res = max(1, int(scale * 50))
        res = (res, res)
    delta = (res[0] / shape[0], res[1] / shape[1])
    d = (shape[0] // res[0], shape[1] // res[1])
    grid = np.mgrid[0:res[0]:delta[0],0:res[1]:delta[1]].transpose(1, 2, 0) % 1
    # Gradients
    angles = 2*np.pi*np.random.rand(res[0]+1, res[1]+1)
    gradients = np.dstack((np.cos(angles), np.sin(angles)))
    g00 = gradients[0:-1,0:-1].repeat(d[0], 0).repeat(d[1], 1)
    g10 = gradients[1:,0:-1].repeat(d[0], 0).repeat(d[1], 1)
    g01 = gradients[0:-1,1:].repeat(d[0], 0).repeat(d[1], 1)
    g11 = gradients[1:,1:].repeat(d[0], 0).repeat(d[1], 1)
    # Ramps
    n00 = np.sum(grid * g00, 2)
    n10 = np.sum(np.dstack((grid[:,:,0]-1, grid[:,:,1])) * g10, 2)
    n01 = np.sum(np.dstack((grid[:,:,0], grid[:,:,1]-1)) * g01, 2)
    n11 = np.sum(np.dstack((grid[:,:,0]-1, grid[:,:,1]-1)) * g11, 2)
    # Interpolation
    t = _f(grid)
    n0 = n00*(1-t[:,:,0]) + t[:,:,0]*n10
    n1 = n01*(1-t[:,:,0]) + t[:,:,0]*n11
    return np.sqrt(2)*((1-t[:,:,1])*n0 + t[:,:,1]*n1) 


noise = generate_perlin_noise(1000, 1000, 0.01)
plt.figure()
plt.imshow(noise, cmap='gray')
plt.show()


def bilinterpol(a, b, pts):
    i = sorted(pts)
    (a1, b1, x11), (_a1, b2, x12), (a2, _b1, x21), (_a2, _b2, x22) = i
    if a1 != _a1 or a2 != _a2 or b1 != _b1 or b2 != _b2:
        print('The given points do not form a rectangle')
    if not a1 <= a <= a2 or not b1 <= b <= b2:
        print('The (a, b) coordinates are not within the rectangle')
    Y = (x11 * (a2 - a) * (b2 - b) +
            x21 * (a - a1) * (b2 - b) +
            x12 * (a2 - a) * (b - b1) +
            x22 * (a - a1) * (b - b1)
           ) / ((a2 - a1) * (b2 - b1) + 0.0)
    return Y
