import unittest
import shades
import numpy as np

class TestNoiseFields(unittest.TestCase):


    def setUp(self):
        self.noise_field = shades.NoiseField()


    def test_noise_returns_number_between_0_and_1(self):
        noise = self.noise_field.noise((4, 4))
        self.assertTrue(0 <= noise <= 1)


    def test_noise_work_for_negative_cases(self):
        noise = self.noise_field.noise((-2, -2))
        self.assertIsInstance(noise, float)


    def test_recursive_noise_returns_number_between_0_and_1(self):
        noise = self.noise_field.recursive_noise((4, 4))
        self.assertTrue(0 <= noise <= 1)


    def test_recursive_noise_work_for_negative_cases(self):
        noise = self.noise_field.recursive_noise((-2, -2))
        self.assertIsInstance(noise, float)


    def test_buffers_dont_affect_noise_calls(self):
        coords = (5, 5)
        before = self.noise_field.noise(coords)
        self.noise_field.noise((600, 600))
        self.noise_field.noise((-600, 600))
        after = self.noise_field.noise(coords)
        self.assertEqual(before, after)


    def test_noise_creation_doesnt_affect_random_state(self):
        before = np.random.get_state()[1]
        self.noise_field.noise((600, 600))
        self.noise_field.noise((-600, 600))
        after = np.random.get_state()[1]
        self.assertTrue((before[1] == after[1]).any())


    def test_noise_field_helper_function_returns_noise_fields(self):
        noise_fields = shades.noise_fields()
        self.assertIsInstance(noise_fields[0], shades.NoiseField)


    def test_noise_field_function_returns_list_size_of_channels(self):
        channels = 5
        noise_fields = shades.noise_fields(channels=channels)
        self.assertEqual(len(noise_fields), channels)


if __name__ == '__main__':
    unittest.main()
