import unittest
import shades
from PIL import Image

class TestCanvas(unittest.TestCase):


    def setUp(self):
        self.canvas = shades.Canvas()


    def test_canvas_returns_image(self):
        self.assertIsInstance(self.canvas, Image.Image)


    def test_canvas_is_resizable(self):
        canvas = shades.Canvas(height=12, width=3)
        self.assertEqual(canvas.width, 3)
        self.assertEqual(canvas.height, 12)


    def test_random_point_returns_tuple_of_coords(self):
        point = self.canvas.random_point()
        self.assertIsInstance(point[0], int)
        self.assertIsInstance(point[1], int)
        self.assertEqual(len(point), 2)


    def test_grid_shuffle_returns_image(self):
        shuffled_canvas = shades.grid_shuffle(self.canvas, 10, 10)
        self.assertIsInstance(shuffled_canvas, Image.Image)


    def test_grid_shuffle_doesnt_change_image_dimensions(self):
        height = 12
        width = 3
        canvas = shades.Canvas(height=height, width=width)
        shuffled_canvas = shades.grid_shuffle(canvas, 3, 3)
        self.assertEqual(shuffled_canvas.width, width)
        self.assertEqual(shuffled_canvas.height, height)


    def test_pixel_sort_returns_image(self):
        sorted_canvas = shades.grid_shuffle(self.canvas, 10, 10)
        self.assertIsInstance(sorted_canvas, Image.Image)


    def test_pixel_sort_doesnt_change_image_dimensions(self):
        height = 12
        width = 3
        canvas = shades.Canvas(height=height, width=width)
        sorted_canvas = shades.pixel_sort(canvas)
        self.assertEqual(sorted_canvas.width, width)
        self.assertEqual(sorted_canvas.height, height)



if __name__ == '__main__':
    unittest.main()
