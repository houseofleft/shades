import unittest
import shades

from typing import Tuple


class TestUtils(unittest.TestCase):


    def test_color_clamp_returns_tuple(self):
        clamped_color = shades.color_clamp((200, 200, 200))
        self.assertIsInstance(clamped_color, Tuple)


    def test_color_clamp_between_bounds(self):
        clamped_color = shades.color_clamp((-400, 894, 256))
        for i in clamped_color:
            self.assertTrue(0 <= i <= 255)


    def test_distance_between_points(self):
        point_one = (0, 0)
        point_two = (15, 15)
        expected_return = 21.2132
        actual_return = shades.distance_between_points(point_one, point_two)
        self.assertAlmostEqual(actual_return, expected_return, 4)


    def test_randomly_shift_point_returns_tuple(self):
        shifted_point = shades.randomly_shift_point((4, 4), (-10, 10))
        self.assertIsInstance(shifted_point, Tuple)


    def test_randomly_shift_point_is_within_specified_bounds(self):
        shifted_point = shades.randomly_shift_point((0, 0), ((-10, 10), (-99, 99)))
        self.assertTrue(-10 <= shifted_point[0] <= 10)
        self.assertTrue(-99 <= shifted_point[1] <= 99)
        shifted_point = shades.randomly_shift_point((0, 0), ((-99, 99), (-10, 10)))
        self.assertTrue(-99 <= shifted_point[0] <= 99)
        self.assertTrue(-10 <= shifted_point[1] <= 10)


if __name__ == "__main__":
    unittest.main()
