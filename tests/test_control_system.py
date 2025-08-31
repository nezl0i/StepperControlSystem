# tests/test_control_system.py
import unittest
from unittest.mock import Mock
from src.control_system import StepperControlSystem, AxisConfig

class TestStepperControlSystem(unittest.TestCase):
    def setUp(self):
        self.hw_mock = Mock()
        axes_config = {
            'test_axis': AxisConfig(
                name='test_axis',
                steps_per_degree=100.0,
                max_angle=360.0,
                min_angle=0.0,
                homing_pin=1
            )
        }
        self.system = StepperControlSystem(axes_config, self.hw_mock)

    def test_validate_coordinates_valid(self):
        result = self.system.validate_coordinates({'test_axis': 180.0})
        self.assertTrue(result)

    def test_validate_coordinates_invalid_axis(self):
        result = self.system.validate_coordinates({'invalid_axis': 180.0})
        self.assertFalse(result)

    def test_validate_coordinates_out_of_range(self):
        result = self.system.validate_coordinates({'test_axis': 400.0})
        self.assertFalse(result)

    def test_angle_to_steps_conversion(self):
        steps = self.system._angle_to_steps('test_axis', 180.0)
        self.assertEqual(steps, 18000)

    def test_steps_to_angle_conversion(self):
        angle = self.system._steps_to_angle('test_axis', 9000)
        self.assertEqual(angle, 90.0)

if __name__ == '__main__':
    unittest.main()