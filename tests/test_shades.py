import unittest
import shades
import numpy as np


def marks_canvas_test(func):
    """
    works as a wrapper over drawing on self.canvas
    to check that a mark is made
    """
    def _decorator(self):
        canvas_copy = self.canvas.copy()
        func(self)
        copy_array = np.array(canvas_copy)
        canvas_array = np.array(self.canvas)
        self.assertFalse((copy_array == canvas_array).all())
    return _decorator


def shade_test(func):
    """
    decorator for function simply returning a shade
    will check that the shade produces color for coords
    """
    def _decorator(self):
        shade = func(self)
        color = shade.determine_shade((5, 5))
        self.assertIsInstance(color, tuple)
        for i in color:
            self.assertIsInstance(i, int)
            self.assertTrue(0 <= i <= 255)

    return _decorator


class TestShades(unittest.TestCase):


    def setUp(self):
        self.shade = shades.BlockColor()
        self.canvas = shades.Canvas()


    def test_adjust_point_returns_point(self):
        adjusted_point = self.shade.adjust_point((4, 5))
        self.assertIsInstance(adjusted_point, tuple)


    def test_adjust_point_affects_point(self):
        points = [(34, 45), (0, 49), (1, 100)]
        self.shade.warp_size = 100
        self.shade.warp_noise = shades.noise_fields(scale=0.5, channels=2)
        adjusted_points = [self.shade.adjust_point(i) for i in points]
        self.assertNotEqual(points, adjusted_points)


    def test_point_marks_canvas(self):
        canvas_copy = self.canvas.copy()
        self.shade.point(self.canvas, (10, 10))
        copy_array = np.array(canvas_copy)
        canvas_array = np.array(self.canvas)
        self.assertFalse((copy_array == canvas_array).all())


    def test_in_bounds(self):
        canvas = shades.Canvas(width=10, height=10)
        in_bound = self.shade.in_bounds(canvas, (4, 4))
        out_bound = self.shade.in_bounds(canvas, (999, 999))
        self.assertTrue(in_bound)
        self.assertFalse(out_bound)


    def test_pixels_inside_edge(self):
        edge = [(1, 1), (1, 2), (1, 3), (2, 1), (2, 3), (3, 1), (3, 2), (3, 3)]
        inside_edge = self.shade.pixels_inside_edge(edge)
        self.assertIn((2, 2), inside_edge)


    def test_pixels_between_two_points(self):
        between_points = self.shade.pixels_between_two_points((1, 1), (3, 1))
        self.assertIn((2, 1), between_points)


    def test_get_shape_edge_returns_list(self):
        result = self.shade.get_shape_edge([(1, 1), (1, 10), (10, 1)])
        self.assertIsInstance(result, list)


    def test_get_circle_edge_returns_list(self):
        result = self.shade.get_circle_edge((10, 10), 3)
        self.assertIsInstance(result, list)


    @marks_canvas_test
    def test_fill(self):
        self.shade.fill(self.canvas)


    @marks_canvas_test
    def test_line(self):
        self.shade.line(self.canvas, (0, 0), (100, 100), 2)


    @marks_canvas_test
    def test_point(self):
        self.shade.point(self.canvas, (10, 10))


    @marks_canvas_test
    def test_shape(self):
        self.shade.shape(self.canvas, [(0, 0), (100, 0), (100, 100)])


    @marks_canvas_test
    def test_shape_outline(self):
        self.shade.shape_outline(self.canvas, [(0, 0), (100, 0), (100, 100)])


    @marks_canvas_test
    def test_rectangle(self):
        self.shade.rectangle(self.canvas, (0, 0), 10, 10)


    @marks_canvas_test
    def test_triangle(self):
        self.shade.triangle(self.canvas, (0, 0), (10, 10), (0, 10))


    @marks_canvas_test
    def test_triangle_outline(self):
        self.shade.triangle_outline(self.canvas, (0, 0), (10, 10), (0, 10))


    @marks_canvas_test
    def test_circle(self):
        self.shade.circle(self.canvas, (10, 10), 5)


    @marks_canvas_test
    def test_circle_outline(self):
        self.shade.circle_outline(self.canvas, (10, 10), 5)


    @marks_canvas_test
    def test_circle_slice(self):
        self.shade.circle_slice(self.canvas, (10, 10), 3, 5, 23)

    @shade_test
    def test_block_color(self):
        return shades.BlockColor()

    @shade_test
    def test_noise_gradient(self):
        return shades.NoiseGradient()

    @shade_test
    def test_domain_warp_gradient(self):
        return shades.DomainWarpGradient()

    @shade_test
    def test_swirl_of_shades(self):
        return shades.SwirlOfShades([
            (0, 0.5, shades.BlockColor()),
            (0.5, 1, shades.BlockColor()),
            ])

    @shade_test
    def test_linear_gradient(self):
        return shades.LinearGradient([
            ((0, 0, 0), 0),
            ((100, 100, 100), 0),
        ])

    @shade_test
    def test_horizontal_gradient(self):
        return shades.HorizontalGradient([
            ((0, 0, 0), 0),
            ((100, 100, 100), 0),
        ])

    @shade_test
    def test_verical_gradient(self):
        return shades.VerticalGradient([
            ((0, 0, 0), 0),
            ((100, 100, 100), 0),
        ])


if __name__ == '__main__':
    unittest.main()
