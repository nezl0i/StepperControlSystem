import time
from hardware_interface import HardwareInterface

class SimulatedHardware(HardwareInterface):
    def __init__(self, pin_config: dict):
        self.pin_config = pin_config
        self.endstop_states = {pin: False for pin in pin_config.get('endstops', [])}
        print("Симуляция аппаратуры инициализирована")

    def move_axis(self, axis: str, steps: int):
        direction = "вперед" if steps > 0 else "назад"
        print(f"Движение оси {axis}: {abs(steps)} шагов {direction}")
        time.sleep(0.001 * abs(steps))

    def set_holding_torque(self, axis: str, enable: bool):
        state = "включен" if enable else "выключен"
        print(f"Ток удержания оси {axis}: {state}")

    def read_endstop(self, pin: int) -> bool:
        return self.endstop_states.get(pin, False)

    def emergency_stop(self):
        print("АВАРИЙНАЯ ОСТАНОВКА: Все двигатели отключены")

    def cleanup(self):
        print("Ресурсы симуляции освобождены")