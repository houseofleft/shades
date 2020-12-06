from abc import ABC, abstractmethod
import random
import numpy as np
from PIL import Image
from opensimplex import OpenSimplex

def color_clamp(color):
    """
    Ensures a three part iterable is a properly formatted color.

    Parameters:
    color (tuple): RGB tuple

    Returns:
    color (tuple): Same color as input, as integers between 0 and 255
    """
    clamped_color = [max(min(int(i), 255), 0) for i in color]
    return tuple(clamped_color)

def distance_between_points(xy1, xy2):
    """
    Returns the euclidean distance between two points.
    https://en.wikipedia.org/wiki/Euclidean_distance

    Parameters:
    xy1 (coordinate): first point
    xy2 (coordiante): second point

    Returns:
    float: euclidean distance betewen the two points
    """
    return (((xy1[0] - xy2[0]) ** 2) + ((xy1[1] - xy2[1]) ** 2)) ** 0.5

def Canvas(height=700, width=700, color=(240,240,240)):
    """
    Returns an blank image to draw on.

    Parameters:
    height (int): Height of the image in pixels. Defaults to 700.
    width (int): Width of the image in pixels. Defaults to 700.
    color (tuple): Desired RGB of the background. Defaults to 240 mono-grey.

    Returns:
    PIL Image
    """
    return Image.new('RGB', (int(height), int(width)), color_clamp(color))

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

class Shade(ABC):
    """
    An Abstract base clase Shade. Methods are used to mark shapes onto images according to various color rules.

    Initialisation Parameters:
    color (tuple): RGB color of shade
    transparency (float): How transparent a shade should be. 0 is opaque. 1 is invisible.
    warp_noise (two NoiseField objects): NoiseFields to warp position of marks made.
    warp_size (int): How much warp_noise is allowed to alter the mark in pixels.
    """

    def __init__(self, color=(0,0,0), transparency=0, warp_noise=(NoiseField(),NoiseField()), warp_size=0):
        self.color = color
        self.transparency = transparency
        self.warp_noise = warp_noise
        self.warp_size = warp_size

    @abstractmethod
    def determine_shade(self, xy):
        """
        Determines the shade/color for xy coordinates.

        Parameters:
        xy: xy coordinates in the form of a tuple (x,y).
        canvas: a PIL image.

        Returns:
        Tuple: Color in form of three long tuple i.e. (255, 124, 133).
        """
        pass

    def apply_transparency(self, xy, canvas, color):
        """
        If transparency settings are applied, appropriately adjusts color

        Parameters:
        xy (iterable): xy coordinates
        canvas (PIL image): Image mark is to be made on.
        color (tuple): Initial color before transparency has been applied.

        Returns:
        color (tuple)
        """
        initial_color = canvas.getpixel((int(xy[0]),int(xy[1])))
        new_color = [int(initial_color[i] + ((color[i] - initial_color[i]) * (1-self.transparency))) for i in range(0,3)]
        return tuple(new_color)

    def adjust_point(self, xy):
        """
        If warp is applied in shade, appropriately adjusts location of point.

        Parameters:
        xy (iterable): xy coordinates

        Returns:
        tuple of x and y
        """
        x = xy[0] + (self.warp_noise[0].noise(xy) * self.warp_size)
        y = xy[1] + (self.warp_noise[1].noise(xy) * self.warp_size)
        return (x,y)

    def point(self, canvas, xy):
        """
        Determines colour and draws a point on an image.

        Parameters:
        xy (iterable): xy coordinates.
        canvas (PIL Image): Image to draw point on.

        (no returns)
        """
        color = self.determine_shade(xy)
        if self.warp_size != 0:
            xy = self.adjust_point(xy)

        try:
            color = self.apply_transparency(xy, canvas, color)
            canvas.putpixel((int(xy[0]),int(xy[1])), color)
        except:
            pass

    def weighted_point(self, canvas, xy, weight):
        """
        Determines colour and draws a weighted point on an image.

        Parameters:
        xy (iterable): xy coordinates.
        canvas (PIL Image): Image to draw point on.
        wieght (int): Weight of point

        (no returns)
        """
        color = self.determine_shade(xy)
        if self.warp_size != 0:
            xy = self.adjust_point(xy)

        try:
            color = self.apply_transparency(xy, canvas, color)
            for x in range(0,weight):
                for y in range(0,weight):
                    try:
                        canvas.putpixel((int(xy[0]+x),int(xy[1]+y)), color)
                    except:
                        pass
        except:
            pass

    def pixels_inside_edge(self, edge_pixels):
        """
        Returns a list of  pixels from inside a edge of points using ray casting algorithm
        https://en.wikipedia.org/wiki/Point_in_polygon
        vertex correction still needs some perfecting, unusual or particularly angular shapes may cause difficulties

        Parameters:
        edge_pixels (coordinates iterables): a list of coordinates (ie. (4,7))

        Returns:
        pixels within edge (list)
        """
        inner_pixels = []
        xs = set([b[0] for b in edge_pixels])
        for x in range(min(xs), max(xs)+1):
            ys = set([b[1] for b in edge_pixels if b[0] == x])
            ys = [y for y in ys if y-1 not in ys]
            ray_count = 0
            for y in range(min(ys), max(ys)+1):
                if y in ys and (x,y):
                    ray_count += 1
                if ray_count % 2 == 1:
                    inner_pixels.append((x,y))

        return list(set(inner_pixels + edge_pixels))

    def pixels_between_two_points(self, xy1, xy2):
        """
        Returns a list of pixels that form a straight line between two points.

        Parameters:
        xy1 (int iterable): Coordinates for first point.
        xy2 (int iterable): Coordinates for second point.

        Returns:
        pixels (int iterable): List of pixels between the two points.
        """
        if abs(xy1[0] - xy2[0]) > abs(xy1[1] - xy2[1]):
            if xy1[0] > xy2[0]:
                x_step = -1
            else:
                x_step = 1
            y_step = ( abs(xy1[1] - xy2[1]) / abs(xy1[0] - xy2[0]) )
            if xy1[1] > xy2[1]:
               y_step *= -1
            i_stop = abs(xy1[0] - xy2[0])
        else:
            if xy1[1] > xy2[1]:
                y_step = -1
            else:
                y_step = 1
            x_step = ( abs(xy1[0] - xy2[0]) / abs(xy1[1] - xy2[1]) )
            if xy1[0] > xy2[0]:
               x_step *= -1
            i_stop = abs(xy1[1]-xy2[1])

        pixels = []
        x, y = xy1
        for i in range(0, int(i_stop) + 1):
            pixels.append((int(x),int(y)))
            x += x_step
            y += y_step
        return pixels

        return x_step, y_step, int(i_stop)

    def line(self, canvas, xy1, xy2, weight=2):
        """
        Draws a weighted line on the image.

        Parameters:
        canvas (PIL Image): Image to draw on.
        xy1 (iterable): Coordinates for start of line.
        xy2 (iterable): Coordinates for end of line.
        weight (int): thickness of line in pixels.

        (no returns)
        """
        for pixel in self.pixels_between_two_points(xy1, xy2):
            self.weighted_point(canvas, pixel, weight)

    def fill(self, canvas):
        """
        Fills the entire image with color.

        Takes as arguments:
        canvas (PIL Image): Image to on.

        (no returns)
        """
        # we'll temporarily turn off warping as it isn't needed here
        warp_size_keeper = self.warp_size
        self.warp_size = 0
        [[self.point(canvas, (x,y)) for x in range(0, canvas.width)] for y in range(0, canvas.height)]
        self.warp_size = warp_size_keeper

    def get_shape_edge(self, list_of_points):
        """
        Returns list of coordinates making up the edge of a shape

        Parameters:
        list_of_points (coordinates iterable): List of points with which to make shape (these will connect in the order given)

        Returns:
        edge (list of coordinates): Coordinates making up the edge of shape
        """
        edge = self.pixels_between_two_points(list_of_points[-1], list_of_points[0])
        for i in range(0, len(list_of_points)-1):
            edge += self.pixels_between_two_points(list_of_points[i], list_of_points[i+1])
        return edge

    def shape(self, canvas, list_of_points):
        """
        Draws a shape on an image based on a list of points.

        Parameters:
        canvas (PIL Image): Image to draw on.
        list_of_points (coordinates iterable): List of points with which to make shape (these will connect in the order given)

        (no returns)
        """
        edge = self.get_shape_edge(list_of_points)
        for pixel in self.pixels_inside_edge(edge):
            self.point(canvas, pixel)

    def shape_outline(self, canvas, list_of_points, weight=2):
        """
        Draws a shape outline on an image based on a list of points.

        Parameters:
        canvas (PIL Image): Image to draw on.
        list_of_points (coordinates iterable): List of points with which to make shape (these will connect in the order given)
        weight: Weight of outline

        (no returns)
        """
        for pixel in self.get_shape_edge(list_of_points):
            self.weighted_point(canvas, pixel, weight)

    def rectangle(self, canvas, xy, width, height):
        """
        Draws a rectangle on the image.

        Parameters:
        canvas (PIL Image): Image to draw on.
        xy (iterable): Top left corner of rectangle.
        width (int): Width of rectangle.
        height (int): Height of rectangle.

        (no returns)
        """
        [[self.point(canvas, (x,y)) for x in range(int(xy[0]), int(xy[0] + width))] for y in range(int(xy[1]), int(xy[1] + height))]

    def triangle(self, canvas, xy1, xy2, xy3):
        """
        Draws a triangle on the image.
        Note that this is the same as calling Shade.shape with a list of three points.

        Parameters:
        canvas (PIL Image): Image to draw on.
        xy1 (int iterable): Coordinates for first point of triangle.
        xy2 (int iterable): Coordinates for second point of triangle.
        xy3 (int iterable): Coordinates for third point of triangle.

        (no returns)
        """
        self.shape(canvas, [xy1, xy2, xy3])

    def triangle_outline(self, canvas, xy1, xy2, xy3, weight=2):
        """
        Draws a triangle outline on the image.
        Note that this is the same as calling Shade.shape_outline with a list of three points.

        Parameters:
        canvas (PIL Image): Image to draw on.
        xy1 (int iterable): Coordinates for first point of triangle.
        xy2 (int iterable): Coordinates for second point of triangle.
        xy3 (int iterable): Coordinates for third point of triangle.
        weight (int): Weight of outline

        (no returns)
        """
        self.shape_outline(canvas, [xy1, xy2, xy3], weight)

    def get_circle_edge(self, xy, radius):
        """
        Returns the edge coordinates of a circle

        Parameters:
        xy (coordinates): center of circle
        radius: radius of circle

        Returns:
        list of points (coordinates iterable)
        """
        edge_pixels = []
        circumference = radius * 2 * np.pi
        for c in range(0, int(circumference)+1):
            angle = (c/circumference) * 360
            opposite = np.sin(np.radians(angle)) * radius
            adjacent = np.cos(np.radians(angle)) * radius
            point = ( int(xy[0] + adjacent), int(xy[1] + opposite) )
            edge_pixels.append(point)
        return edge_pixels

    def circle(self, canvas, xy, radius):
        """
        Draws a circle on the image.

        Parameters:
        canvas (PIL Image): Image to draw on.
        xy (int iterable): Coordinates for center of circle.
        radius (int): Radius of the circle

        (no returns)
        """
        edge_pixels = self.get_circle_edge(xy, radius)
        for pixel in self.pixels_inside_edge(edge_pixels):
            self.point(canvas, pixel)

    def circle_outline(self, canvas, xy, radius, weight=2):
        """
        Draws a circle outline on the image.

        Parameters:
        canvas (PIL Image): Image to draw on.
        xy (int iterable): Coordinates for center of circle.
        radius (int): Radius of the circle
        weight (int): Weight of the outline

        (no returns)
        """
        edge_pixels = self.get_circle_edge(xy, radius)
        for pixel in edge_pixels:
            self.weighted_point(canvas, pixel, weight)

    def pizza_slice(self, canvas, xy, radius, start_angle, degrees_of_slice):
        """
        Draws a partial circle based on degrees.
        (will have the appearance of a 'pizza slice' or 'pacman' depending on degrees).

        Parameters:
        canvas (PIL Image): Image to draw on.
        xy (int iterable): Coordinates for the center
        radius (int): Radius of the circle
        start_angle (int): degree point to start on. Will start from 12 o'clock position, and move clockwise around
        degrees_of_slice (int): degree point to move around circle from
        """

        # due to Shade.pixels_between_two_points vertex correction issues, breaks down shape into smaller parts
        def _internal(canvas, xy, radius, start_angle, degrees_of_slice):
            circumference = radius * 2 * np.pi

            start_point = int( ( ( (start_angle - 90) % 361 ) / 360 ) * circumference )
            slice_length = int( ( degrees_of_slice / 360 ) * circumference )
            end_point = start_point + slice_length
            edge_pixels = []

            for c in range(start_point, end_point + 1):
                angle = (c/circumference) * 360
                opposite = np.sin(np.radians(angle)) * radius
                adjacent = np.cos(np.radians(angle)) * radius
                point = ( int(xy[0] + adjacent), int(xy[1] + opposite) )
                edge_pixels.append(point)
                if c == start_point or c == end_point:
                    edge_pixels += self.pixels_between_two_points(point, xy)

            for pixel in self.pixels_inside_edge(edge_pixels):
                self.point(canvas, pixel)

        if degrees_of_slice > 180:
            _internal(canvas, xy, radius, start_angle, 180)
            _internal(canvas, xy, radius, start_angle + 180, degrees_of_slice - 180)
        else:
            _internal(canvas, xy, radius, start_angle, degrees_of_slice)


class BlockColor(Shade):
    """
    Type of shade that will always fill with defined color without variation.

    Initialisation Parameters:
    color (tuple): RGB color of shade
    transparency (float): How transparent a shade should be. 0 is opaque. 1 is invisible.
    warp_noise (two NoiseField objects): NoiseFields to warp position of marks made.
    warp_size (int): How much warp_noise is allowed to alter the mark in pixels.
    """
    def determine_shade(self, xy):
        """
        Ignores xy coordinates and returns defined color.

        Parameters:
        xy (iterable): xy coordinates

        Returns:
        color in form of tuple
        """
        return self.color

class NoiseGradient(Shade):
    """
    Type of shade that will produce varying gradient based on noise fields.

    Initialisation Parameters:
    color (tuple): central RGB color of shade. Defaults to black.
    transparency (float): How transparent a shade should be. 0 is opaque. 1 is invisible. Defaults to 0.
    warp_noise (two NoiseField objects): NoiseFields to warp position of marks made. Defaults to initalisation of NoiseField().
    warp_size (int): How much warp_noise is allowed to alter the mark in pixels. Defaults to 0.
    color_variance (int): How much noise is allowed to affect the color from the central shade
    noise_fields (iterable of NoiseFields): A noise field for each channel (r,g,b). Defaults to three initialisations of NoiseField().
    """
    def __init__(self, color=(0,0,0), transparency=0, warp_noise=(NoiseField(),NoiseField()), warp_size=0, color_variance=70, noise_fields=[NoiseField() for i in range(3)]):
        super().__init__(color, transparency, warp_noise, warp_size)
        self.color_variance = color_variance
        self.noise_fields = tuple(noise_fields)

    def determine_shade(self, xy):
        """
        Measures noise from coordinates and affects color based upon return.

        Parameters:
        xy (iterable): xy coordinates

        Returns:
        color in form of tuple
        """
        def apply_noise(i):
            noise = self.noise_fields[i].noise(xy) - 0.5
            color_affect = noise * (2*self.color_variance)
            return self.color[i] + color_affect
        return color_clamp([apply_noise(i) for i in range(0,3)])

class DomainWarpGradient(Shade):
    """
    Type of shade that will produce varying gradient based on recursive noise fields.
    Because of the exponential nature of recursive calls, this shade can lead to long run times.

    Initialisation Parameters:
    color (tuple): central RGB color of shade. Defaults to black.
    transparency (float): How transparent a shade should be. 0 is opaque. 1 is invisible. Defaults to 0.
    warp_noise (two NoiseField objects): NoiseFields to warp position of marks made. Defaults to initalisation of NoiseField().
    warp_size (int): How much warp_noise is allowed to alter the mark in pixels. Defaults to 0.
    color_variance (int): How much noise is allowed to affect the color from the central shade
    noise_fields (iterable of NoiseFields): A noise field for each channel (r,g,b). Defaults to three initialisations of NoiseField().
    depth (int): Number of recursive calls of noise to make. Defaults to 1.
    feedback (float): The size of effect of recursive noise calls. For normal affects set within 0-1 range. Defaults to 0.7.
    """
    def __init__(self, color=(0,0,0), transparency=0, warp_noise=(NoiseField(),NoiseField()), warp_size=0, color_variance=70, noise_fields=[NoiseField() for i in range(3)], depth=1, feedback=0.7):
        super().__init__(color, transparency, warp_noise, warp_size)
        self.color_variance = color_variance
        self.noise_fields = tuple(noise_fields)
        self.depth = depth
        self.feedback = feedback

    def determine_shade(self, xy):
        """
        Determines shade based on xy coordinates.

        Parameters:
        xy (iterable): xy coordinates

        Returns:
        color in form of tuple
        """
        def apply_noise(i):
            noise = self.noise_fields[i].recursive_noise(xy, self.depth, self.feedback) - 0.5
            color_affect = noise * (2*self.color_variance)
            return self.color[i] + color_affect
        return color_clamp([apply_noise(i) for i in range(0,3)])

class SwirlOfShades(Shade):
    """
    Type of shade that will select from list of other shades based on recursive noise field.
    Because of the exponential nature of recursive calls, this shade can lead to long run times.

    Initialisation Parameters:
    warp_noise (two NoiseField objects): NoiseFields to warp position of marks made. Defaults to initalisation of NoiseField().
    warp_size (int): How much warp_noise is allowed to alter the mark in pixels. Defaults to 0.
    color_variance (int): How much noise is allowed to affect the color from the central shade
    noise_field (NoiseFields): A noise field for selection of shade.
    depth (int): Number of recursive calls of noise to make. Defaults to 1. Setting to 0 will non-recursive noise is used.
    feedback (float): The size of effect of recursive noise calls. For normal affects set within 0-1 range. Defaults to 0.7.
    shades (list of iterables): Determines when shades are select, items in list must be in form of (lower_bound, upper_bound, Shade). For example passing in a list of [(0,0.4,BlockColor(color=(0,0,0))),(0.6,0.8,NoiseGradient(color=(255,255,255)))] will mean that when a noise value of between 0 and 0.4 is recieved, a pixel will be shaded black, when a value of between 0.6 and 0.8 is recieved a pixel will be shaded with a white noise gradient. If a number outside of that range is recieved, nothing will happen. If overlapping ranges are present, the first item in the list will be selected over the others.
    """
    def __init__(self, warp_noise=(NoiseField(),NoiseField()), warp_size=0, color_variance=70, noise_field=NoiseField(), depth=1, feedback=0.7, shades=[]):
        super().__init__(transparency = 0, warp_noise = warp_noise, warp_size = warp_size)
        self.color_variance = color_variance
        self.noise_field = noise_field
        self.depth = depth
        self.feedback = feedback
        self.shades = shades
        self.transparent = BlockColor(transparency=1)

    def determine_shade(self, xy):
        """
        Determines shade based on xy coordinates.

        Parameters:
        xy (iterable): xy coordinates

        Returns:
        color in form of tuple
        """
        noise = self.noise_field.recursive_noise(xy, self.depth, self.feedback)
        shades = [s for s in self.shades if noise > s[0] and noise < s[1]]
        if len(shades) > 0:
            shade = shades[0][2]
            return shade.determine_shade(xy)

class LinearGradient(Shade):
    """
    Type of shade that will determine color based on transition between various 'color_points'

    Initialisation parameters:
    color_points (list of pairs): Groups of colours and the coordinate (based on axis) at which they should appear. Something like: [((255,10,23), 60), ((240, 240, 240), 200), ((0, 255, 0), 500)]
    axis (int): 0 for horizontal gradient, 1 for vertical
    transparency (float): How transparent a shade should be. 0 is opaque. 1 is invisible.
    warp_noise (two NoiseField objects): NoiseFields to warp position of marks made.
    warp_size (int): How much warp_noise is allowed to alter the mark in pixels.
    """
    def __init__(self, color_points, axis=0, transparency=0, warp_noise=(NoiseField(),NoiseField()), warp_size=0):
        super().__init__(transparency=transparency, warp_noise=warp_noise, warp_size=warp_size)
        self.color_points = color_points
        self.axis = axis

    def determine_shade(self, xy):
        """
        Determines shade based on xy coordinates.

        Parameters:
        xy (iterable): xy coordinates

        Returns:
        color in form of tuple
        """
        larger = [i[1] for i in self.color_points if i[1] >= xy[self.axis]]
        smaller = [i[1] for i in self.color_points if i[1] < xy[self.axis]]
        if len(smaller) == 0:
            next = min(larger)
            next_color = [i[0] for i in self.color_points if i[1] == next][0]
            return next_color
        elif len(larger) == 0:
            last = max(smaller)
            last_color = [i[0] for i in self.color_points if i[1] == last][0]
            return last_color

        next = min(larger)
        last = max(smaller)

        next_color = [i[0] for i in self.color_points if i[1] == next][0]
        last_color = [i[0] for i in self.color_points if i[1] == last][0]
        distance_from_next = abs(next - xy[self.axis])
        distance_from_last = abs(last - xy[self.axis])
        from_last_to_next = distance_from_last / (distance_from_next + distance_from_last)

        color = [0, 0, 0]
        for i in range(3):
            color_difference = (last_color[i] - next_color[i]) * from_last_to_next
            color[i] = last_color[i] - color_difference

        return color_clamp(color)

class VerticalGradient(LinearGradient):
    """
    Type of shade that will determine color based on transition between various 'color_points'

    Initialisation parameters:
    color_points (list of pairs): Groups of colours and the y coordinate at which they should appear. Something like: [((255,10,23), 60), ((240, 240, 240), 200), ((0, 255, 0), 500)]
    transparency (float): How transparent a shade should be. 0 is opaque. 1 is invisible.
    warp_noise (two NoiseField objects): NoiseFields to warp position of marks made.
    warp_size (int): How much warp_noise is allowed to alter the mark in pixels.
    """
    def __init__(self, color_points, transparency=0, warp_noise=(NoiseField(),NoiseField()), warp_size=0):
        super().__init__(color_points=color_points, axis=1, transparency=transparency, warp_noise=warp_noise, warp_size=warp_size)

class HorizontalGradient(LinearGradient):
    """
    Type of shade that will determine color based on transition between various 'color_points'

    Initialisation parameters:
    color_points (list of pairs): Groups of colours and the x coordinate at which they should appear. Something like: [((255,10,23), 60), ((240, 240, 240), 200), ((0, 255, 0), 500)]
    transparency (float): How transparent a shade should be. 0 is opaque. 1 is invisible.
    warp_noise (two NoiseField objects): NoiseFields to warp position of marks made.
    warp_size (int): How much warp_noise is allowed to alter the mark in pixels.
    """
    def __init__(self, color_points, transparency=0, warp_noise=(NoiseField(),NoiseField()), warp_size=0):
        super().__init__(color_points=color_points, axis=0, transparency=transparency, warp_noise=warp_noise, warp_size=warp_size)

class PointGradient(Shade):
    """
    Type of shade that will determine color based on proximity to various 'color_points'

    Initialisation parameters:
    color_points (list of pairs): Groups of colours and the coordinates at which they should appear. Something like: [((255,10,23), (34, 60)), ((240, 240, 240), (100, 200)), ((0, 255, 0), (500,600))]
    axis (int): 0 for horizontal gradient, 1 for vertical
    transparency (float): How transparent a shade should be. 0 is opaque. 1 is invisible.
    warp_noise (two NoiseField objects): NoiseFields to warp position of marks made.
    warp_size (int): How much warp_noise is allowed to alter the mark in pixels.
    """
    def __init__(self, color_points, axis=0, transparency=0, warp_noise=(NoiseField(),NoiseField()), warp_size=0):
        super().__init__(transparency=transparency, warp_noise=warp_noise, warp_size=warp_size)
        self.color_points = color_points
        self.axis = axis

    def determine_shade(self,xy):
        """
        Determines shade based on xy coordinates.

        Parameters:
        xy (iterable): xy coordinates

        Returns:
        color in form of tuple
        """
        colors = [i[0] for i in self.color_points]
        weights = [1/distance_between_points(xy, i[1]) for i in self.color_points]
        color = [np.average([c[i] for c in colors], weights=weights) for i in range(3)]
        return color_clamp(color)
