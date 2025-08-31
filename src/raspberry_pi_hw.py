import RPi.GPIO as GPIO
import time
from hardware_interface import HardwareInterface

class RaspberryPiHardware(HardwareInterface):
    def __init__(self, pin_config: dict):
        GPIO.setmode(GPIO.BCM)
        self.pin_config = pin_config
        
        all_pins = []
        for pins in pin_config.values():
            all_pins.extend(pins)
        
        for pin in set(all_pins):
            GPIO.setup(pin, GPIO.OUT if pin not in [5, 6, 13, 19] else GPIO.IN)

    def move_axis(self, axis: str, steps: int):
        if axis not in self.pin_config:
            raise ValueError(f"Ось {axis} не найдена в конфигурации")
        
        pins = self.pin_config[axis]
        direction = 1 if steps > 0 else -1
        steps = abs(steps)
        
        for _ in range(steps):
            for i, pin in enumerate(pins):
                GPIO.output(pin, GPIO.HIGH if i == 0 else GPIO.LOW)
            time.sleep(0.001)
            for pin in pins:
                GPIO.output(pin, GPIO.LOW)

    def set_holding_torque(self, axis: str, enable: bool):
        pass

    def read_endstop(self, pin: int) -> bool:
        return GPIO.input(pin) == GPIO.HIGH

    def emergency_stop(self):
        for pins in self.pin_config.values():
            for pin in pins:
                GPIO.output(pin, GPIO.LOW)

    def cleanup(self):
        GPIO.cleanup()