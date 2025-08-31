# tests/test_hardware.py
import unittest
from unittest.mock import patch, MagicMock
from src.raspberry_pi_hw import RaspberryPiHardware

class TestRaspberryPiHardware(unittest.TestCase):
    @patch('src.raspberry_pi_hw.GPIO')
    def test_initialization(self, mock_gpio):
        pin_config = {'test_axis': [1, 2, 3, 4], 'endstops': [5]}
        hardware = RaspberryPiHardware(pin_config)
        
        self.assertTrue(mock_gpio.setmode.called)
        self.assertTrue(mock_gpio.setup.called)

    @patch('src.raspberry_pi_hw.GPIO')
    def test_move_axis(self, mock_gpio):
        pin_config = {'test_axis': [1, 2, 3, 4]}
        hardware = RaspberryPiHardware(pin_config)
        
        hardware.move_axis('test_axis', 100)
        
        self.assertTrue(mock_gpio.output.called)

if __name__ == '__main__':
    unittest.main()