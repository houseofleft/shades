"""
shades

contains classes and functions relating to Shades' shade object
"""
from abc import ABC, abstractmethod
from typing import Tuple, List

import numpy as np

from PIL import Image

from .noise_fields import NoiseField, noise_fields
from .utils import color_clamp


class Shade(ABC):
    """
    An Abstract base clase Shade.
    Methods are used to mark shapes onto images according to various color rules.

    Initialisation parameters of warp_noise takes two noise_fields affecting how
    much a point is moved across x and y axis.

    warp_size determines the amount that a warp_noise result of 1 (maximum perlin
    value) translates as
    """

    def __init__(
            self,
            color: Tuple[int, int, int] = (0, 0, 0),
            warp_noise: Tuple[NoiseField] = noise_fields(channels=2),
            warp_size: float = 0,
        ):
        self.color = color
        self.warp_noise = warp_noise
        self.warp_size = warp_size

    @abstractmethod
    def determine_shade(self, xy_coords: Tuple[int, int]) -> Tuple[int, int, int]:
        """
        Determines the shade/color for given xy coordinate.
        """

    def adjust_point(self, xy_coords: Tuple[int, int]) -> Tuple[int, int]:
        """
        If warp is applied in shade, appropriately adjusts location of point.
        """
        if self.warp_size == 0:
            return xy_coords
        x_coord = xy_coords[0] + (self.warp_noise[0].noise(xy_coords) * self.warp_size)
        y_coord = xy_coords[1] + (self.warp_noise[1].noise(xy_coords) * self.warp_size)
        return (x_coord, y_coord)

    def point(self, canvas: Image, xy_coords: Tuple[int, int]) -> None:
        """
        Determines colour and draws a point on an image.
        """
        color = self.determine_shade(xy_coords)
        if color is None:
            return
        xy_coords = self.adjust_point(xy_coords)

        if self.in_bounds(canvas, xy_coords):
            canvas.putpixel((int(xy_coords[0]), int(xy_coords[1])), color)


    def in_bounds(self, canvas: Image, xy_coords: Tuple[int, int]) -> bool:
        """
        determined whether xy_coords are within the size of canvas image
        """
        if (xy_coords[0] < 0) or (xy_coords[0] >= canvas.width):
            return False
        if (xy_coords[1] < 0) or (xy_coords[1] >= canvas.height):
            return False
        return True


    def weighted_point(self, canvas: Image, xy_coords: Tuple[int, int], weight: int):
        """
        Determines colour and draws a weighted point on an image.
        """
        color = self.determine_shade(xy_coords)
        if self.warp_size != 0:
            xy_coords = self.adjust_point(xy_coords)

        for x_coord in range(0, weight):
            for y_coord in range(0, weight):
                new_point = (int(xy_coords[0]+x_coord), int(xy_coords[1]+y_coord))
                if self.in_bounds(canvas, new_point):
                    canvas.putpixel(new_point, color)


    def pixels_inside_edge(self, edge_pixels: List) -> List:
        """
        Returns a list of  pixels from inside a edge of points using ray casting algorithm
        https://en.wikipedia.org/wiki/Point_in_polygon
        vertex correction requires improvements, unusual or particularly angular shapes may
        cause difficulties
        """
        inner_pixels = []
        x_coords = {i[0] for i in edge_pixels}
        for x_coord in range(min(x_coords), max(x_coords)+1):
            y_coords = {i[1] for i in edge_pixels if i[0] == x_coord}
            y_coords = [i for i in y_coords if i-1 not in y_coords]
            ray_count = 0
            for y_coord in range(min(y_coords), max(y_coords)+1):
                if y_coord in y_coords and (x_coord, y_coord):
                    ray_count += 1
                if ray_count % 2 == 1:
                    inner_pixels.append((x_coord, y_coord))

        return list(set(inner_pixels + edge_pixels))


    def pixels_between_two_points(self, xy_coord_1: Tuple, xy_coord_2: Tuple) -> List:
        """
        Returns a list of pixels that form a straight line between two points.

        Parameters:
        xy_coord_1 (int iterable): Coordinates for first point.
        xy_coord_2 (int iterable): Coordinates for second point.

        Returns:
        pixels (int iterable): List of pixels between the two points.
        """
        if abs(xy_coord_1[0] - xy_coord_2[0]) > abs(xy_coord_1[1] - xy_coord_2[1]):
            if xy_coord_1[0] > xy_coord_2[0]:
                x_step = -1
            else:
                x_step = 1
            y_step = (abs(xy_coord_1[1] - xy_coord_2[1]) / abs(xy_coord_1[0] - xy_coord_2[0]))
            if xy_coord_1[1] > xy_coord_2[1]:
                y_step *= -1
            i_stop = abs(xy_coord_1[0] - xy_coord_2[0])
        else:
            if xy_coord_1[1] > xy_coord_2[1]:
                y_step = -1
            else:
                y_step = 1
            x_step = (abs(xy_coord_1[0] - xy_coord_2[0]) / abs(xy_coord_1[1] - xy_coord_2[1]))
            if xy_coord_1[0] > xy_coord_2[0]:
                x_step *= -1
            i_stop = abs(xy_coord_1[1]-xy_coord_2[1])

        pixels = []
        x_coord, y_coord = xy_coord_1
        for _ in range(0, int(i_stop) + 1):
            pixels.append((int(x_coord), int(y_coord)))
            x_coord += x_step
            y_coord += y_step
        return pixels


    def line(
            self,
            canvas: Image,
            xy_coords_1: Tuple[int, int],
            xy_coords_2: Tuple[int, int],
            weight: int = 2,
        ) -> None:
        """
        Draws a weighted line on the image.
        """
        for pixel in self.pixels_between_two_points(xy_coords_1, xy_coords_2):
            self.weighted_point(canvas, pixel, weight)


    def fill(self, canvas: Image) -> None:
        """
        Fills the entire image with color.
        """
        # we'll temporarily turn off warping as it isn't needed here
        warp_size_keeper = self.warp_size
        self.warp_size = 0
        for x_coord in range(0, canvas.width):
            for y_coord in range(0, canvas.height):
                self.point(canvas, (x_coord, y_coord))
        #[[self.point(canvas, (x, y)) for x in range(0, canvas.width)]
        # for y in range(0, canvas.height)]
        self.warp_size = warp_size_keeper


    def get_shape_edge(self, list_of_points: List[Tuple[int, int]]) -> List[Tuple]:
        """
        Returns list of coordinates making up the edge of a shape
        """
        edge = self.pixels_between_two_points(
            list_of_points[-1], list_of_points[0])
        for i in range(0, len(list_of_points)-1):
            edge += self.pixels_between_two_points(
                list_of_points[i], list_of_points[i+1])
        return edge


    def shape(self, canvas: Image, points: List[Tuple[int, int]]) -> None:
        """
        Draws a shape on an image based on a list of points.
        """
        edge = self.get_shape_edge(points)
        for pixel in self.pixels_inside_edge(edge):
            self.point(canvas, pixel)


    def shape_outline(
            self,
            canvas: Image,
            points: List[Tuple[int, int]],
            weight: int = 2,
        ) -> None:
        """
        Draws a shape outline on an image based on a list of points.
        """
        for pixel in self.get_shape_edge(points):
            self.weighted_point(canvas, pixel, weight)


    def rectangle(
            self,
            canvas: Image,
            top_corner: Tuple[int, int],
            width: int,
            height: int,
        ) -> None:
        """
        Draws a rectangle on the image.
        """
        for x_coord in range(top_corner[0], top_corner[0] + width):
            for y_coord in range(top_corner[1], top_corner[1] + height):
                self.point(canvas, (x_coord, y_coord))

    def square(
            self,
            canvas: Image,
            top_corner: Tuple[int, int],
            size: int,
        ) -> None:
        """
        Draws a square on the canvas
        """
        self.rectangle(canvas, top_corner, size, size)


    def triangle(
            self,
            canvas,
            xy1: Tuple[int, int],
            xy2: Tuple[int, int],
            xy3: Tuple[int, int],
        ) -> None:
        """
        Draws a triangle on the image.
        This is the same as calling Shade.shape with a list of three points.
        """
        self.shape(canvas, [xy1, xy2, xy3])


    def triangle_outline(
            self,
            canvas,
            xy1: Tuple[int, int],
            xy2: Tuple[int, int],
            xy3: Tuple[int, int],
            weight: int = 2,
        ) -> None:
        """
        Draws a triangle outline on the image.
        Note that this is the same as calling Shade.shape_outline with a list of three points.
        """
        self.shape_outline(canvas, [xy1, xy2, xy3], weight)


    def get_circle_edge(
            self,
            center: Tuple[int, int],
            radius: int,
        ) -> List[Tuple[int, int]]:
        """
        Returns the edge coordinates of a circle
        """
        edge_pixels = []
        circumference = radius * 2 * np.pi
        for i in range(0, int(circumference)+1):
            angle = (i/circumference) * 360
            opposite = np.sin(np.radians(angle)) * radius
            adjacent = np.cos(np.radians(angle)) * radius
            point = (int(center[0] + adjacent), int(center[1] + opposite))
            edge_pixels.append(point)
        return edge_pixels


    def circle(
            self,
            canvas: Image,
            center: Tuple[int, int],
            radius: int,
        ) -> None:
        """
        Draws a circle on the image.
        """
        edge_pixels = self.get_circle_edge(center, radius)
        for pixel in self.pixels_inside_edge(edge_pixels):
            self.point(canvas, pixel)


    def circle_outline(
            self,
            canvas: Image,
            center: Tuple[int, int],
            radius: int,
            weight: int = 2,
        ) -> None:
        """
        Draws a circle outline on the image.
        """
        edge_pixels = self.get_circle_edge(center, radius)
        for pixel in edge_pixels:
            self.weighted_point(canvas, pixel, weight)


    def circle_slice(
            self,
            canvas: Image,
            center: Tuple[int, int],
            radius: int,
            start_angle: int,
            degrees_of_slice: int,
        ) -> None:
        """
        Draws a partial circle based on degrees.
        (will have the appearance of a 'pizza slice' or 'pacman' depending on degrees).
        """
        # due to Shade.pixels_between_two_points vertex correction issues,
        # breaks down shape into smaller parts
        def _internal(canvas, center, radius, start_angle, degrees_of_slice):
            circumference = radius * 2 * np.pi

            start_point = int(
                (((start_angle - 90) % 361) / 360) * circumference)
            slice_length = int((degrees_of_slice / 360) * circumference)
            end_point = start_point + slice_length
            edge_pixels = []

            for i in range(start_point, end_point + 1):
                angle = (i/circumference) * 360
                opposite = np.sin(np.radians(angle)) * radius
                adjacent = np.cos(np.radians(angle)) * radius
                point = (int(center[0] + adjacent), int(center[1] + opposite))
                edge_pixels.append(point)
                if i in [start_point, end_point]:
                    edge_pixels += self.pixels_between_two_points(point, center)

            for pixel in self.pixels_inside_edge(edge_pixels):
                self.point(canvas, pixel)

        if degrees_of_slice > 180:
            _internal(canvas, center, radius, start_angle, 180)
            _internal(canvas, center, radius, start_angle +
                      180, degrees_of_slice - 180)
        else:
            _internal(canvas, center, radius, start_angle, degrees_of_slice)


class BlockColor(Shade):
    """
    Type of shade that will always fill with defined color without variation.
    """
    def determine_shade(self, xy_coords: Tuple[int, int]) -> Tuple[int, int, int]:
        """
        Ignores xy coordinates and returns defined color.
        """
        return self.color


class NoiseGradient(Shade):
    """
    Type of shade that will produce varying gradient based on noise fields.

    Unique Parameters:
    color_variance: How much noise is allowed to affect the color from the central shade
    color_fields: A noise field for each channel (r,g,b)
    """

    def __init__(
            self,
            color: Tuple[int, int, int] = (0, 0, 0),
            warp_noise: Tuple[NoiseField, NoiseField, NoiseField] = noise_fields(channels=3),
            warp_size: int = 0,
            color_variance: int = 70,
            color_fields: Tuple[NoiseField, NoiseField, NoiseField] = noise_fields(channels=3),
        ):
        super().__init__(color, warp_noise, warp_size)
        self.color_variance = color_variance
        self.color_fields = tuple(color_fields)


    def determine_shade(self, xy_coords: Tuple[int, int]) -> Tuple[int, int, int]:
        """
        Measures noise from coordinates and affects color based upon return.
        """
        def apply_noise(i):
            noise = self.color_fields[i].noise(xy_coords) - 0.5
            color_affect = noise * (2*self.color_variance)
            return self.color[i] + color_affect
        return color_clamp([apply_noise(i) for i in range(len(self.color))])


class DomainWarpGradient(Shade):
    """
    Type of shade that will produce varying gradient based on recursive noise fields.

    Unique Parameters:
    color_variance: How much noise is allowed to affect the color from the central shade
    color_fields: A noise field for each channel (r,g,b)
    depth: Number of recursions within noise to make
    feedback: Affect of recursive calls, recomended around 0-2
    """

    def __init__(
            self,
            color: Tuple[int, int, int] = (0, 0, 0),
            warp_noise: Tuple[NoiseField, NoiseField] = noise_fields(channels=2),
            warp_size: int = 0,
            color_variance: int = 70,
            color_fields: Tuple[NoiseField, NoiseField, NoiseField] = noise_fields(channels=3),
            depth: int = 2,
            feedback: float = 0.7,
        ):
        super().__init__(color, warp_noise, warp_size)
        self.color_variance = color_variance
        self.color_fields = tuple(color_fields)
        self.depth = depth
        self.feedback = feedback


    def determine_shade(self, xy_coords: Tuple[int, int]) -> Tuple[int, int, int]:
        """
        Determines shade based on xy coordinates.
        """
        def apply_noise(i):
            noise = self.color_fields[i].recursive_noise(
                xy_coords, self.depth, self.feedback) - 0.5
            color_affect = noise * (2*self.color_variance)
            return self.color[i] + color_affect
        return color_clamp([apply_noise(i) for i in range(len(self.color))])


class SwirlOfShades(Shade):
    """
    Type of shade that will select from list of other shades based on recursive noise field.

    Unique Parameters:
    swirl_field: a NoiseField from which the selection of the shade is made
    depth: Number of recursive calls to make from swirl_field.noise (defaults to 0)
    feedback: Affect of recursive calls from swirl_field.noise
    shades: this one is very specific, and determines when shades are used.
            must be list of tuples of this form:
            (lower_bound, upper_bound, Shade)

    because the 'shades' arguments potentially confusing, here's an example.
    The below will color white when noise of 0 - 0.5 is returned, and black if noise of 0.5 - 1
    [(0, 0.5, shades.BlockColor((255, 255, 255)), (0.5, 1, shades.BlockColor((0, 0, 0)))]
    """
    def __init__(
            self,
            shades: List[Tuple[float, float, Shade]],
            warp_noise: Tuple[NoiseField, NoiseField] = noise_fields(channels=2),
            warp_size: int = 0,
            color_variance: int = 70,
            swirl_field: NoiseField = NoiseField(),
            depth: int = 1,
            feedback: float = 0.7,
        ):
        super().__init__(warp_noise=warp_noise, warp_size=warp_size)
        self.color_variance = color_variance
        self.swirl_field = swirl_field
        self.depth = depth
        self.feedback = feedback
        self.shades = shades


    def determine_shade(self, xy_coords: Tuple[int, int]):
        """
        Determines shade based on xy coordinates.
        """
        noise = self.swirl_field.recursive_noise(xy_coords, self.depth, self.feedback)
        shades = [i for i in self.shades if i[0] <= noise < i[1]]
        if len(shades) > 0:
            shade = shades[0][2]
            return shade.determine_shade(xy_coords)
        return None


class LinearGradient(Shade):
    """
    Type of shade that will determine color based on transition between various 'color_points'

    Unique Parameters:
    color_points: Groups of colours and coordinate at which they should appear
    axis: 0 for horizontal gradient, 1 for vertical

    Here's an example of color_points
    in this, anything before 50 (on whichever axis specified) will be black,
    anything after 100 will be white
    between 50 and 100 will be grey, with tone based on proximity to 50 or 100
    [((0, 0, 0), 50), ((250, 250, 250), 100)]
    """

    def __init__(
            self,
            color_points: List[Tuple[int, Tuple[int, int, int]]],
            axis: int = 0,
            warp_noise: Tuple[NoiseField, NoiseField] = noise_fields(channels=2),
            warp_size: int = 0,
        ):
        super().__init__(warp_noise=warp_noise, warp_size=warp_size)
        self.color_points = color_points
        self.axis = axis


    def determine_shade(self, xy_coords):
        """
        Determines shade based on xy coordinates.

        Parameters:
        xy (iterable): xy coordinates

        Returns:
        color in form of tuple
        """
        larger = [i[1] for i in self.color_points if i[1] >= xy_coords[self.axis]]
        smaller = [i[1] for i in self.color_points if i[1] < xy_coords[self.axis]]
        if len(smaller) == 0:
            next_item = min(larger)
            next_color = [i[0] for i in self.color_points if i[1] == next_item][0]
            return next_color
        if len(larger) == 0:
            last_item = max(smaller)
            last_color = [i[0] for i in self.color_points if i[1] == last_item][0]
            return last_color

        next_item = min(larger)
        last_item = max(smaller)

        next_color = [i[0] for i in self.color_points if i[1] == next_item][0]
        last_color = [i[0] for i in self.color_points if i[1] == last_item][0]
        distance_from_next = abs(next_item - xy_coords[self.axis])
        distance_from_last = abs(last_item - xy_coords[self.axis])
        from_last_to_next = distance_from_last / (distance_from_next + distance_from_last)

        color = [0 for i in len(next_color)]
        for i, _ in enumerate(next_color):
            color_difference = (
                last_color[i] - next_color[i]) * from_last_to_next
            color[i] = last_color[i] - color_difference

        return color_clamp(color)


class VerticalGradient(LinearGradient):
    """
    Type of shade that will determine color based on transition between various 'color_points'

    Unique Parameters:
    color_points: Groups of colours and coordinate at which they should appear

    Here's an example of color_points
    in this, anything before 50 (on y axis) will be black,
    anything after 100 will be white
    between 50 and 100 will be grey, with tone based on proximity to 50 or 100
    """
    def __init__(
        self,
        color_points: List[Tuple[int, Tuple[int, int, int]]],
        warp_noise: Tuple[NoiseField, NoiseField] = noise_fields(channels=2),
        warp_size: int = 0,
    ):
        super().__init__(
            color_points=color_points,
            axis=1,
            warp_noise=warp_noise,
            warp_size=warp_size,
        )


class HorizontalGradient(LinearGradient):
    """
    Type of shade that will determine color based on transition between various 'color_points'

    Unique Parameters:
    color_points: Groups of colours and coordinate at which they should appear

    Here's an example of color_points
    in this, anything before 50 (on x axis) will be black,
    anything after 100 will be white
    between 50 and 100 will be grey, with tone based on proximity to 50 or 100
    """

    def __init__(self,
        color_points: List[Tuple[int, Tuple[int, int, int]]],
        warp_noise: Tuple[NoiseField, NoiseField] = noise_fields(channels=2),
        warp_size: int = 0,
    ):
        super().__init__(
            color_points=color_points,
            axis=0,
            warp_noise=warp_noise,
            warp_size=warp_size,
        )
