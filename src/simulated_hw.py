import time
from hardware_interface import HardwareInterface

class SimulatedHardware(HardwareInterface):
    def __init__(self, pin_config: dict):
        self.pin_config = pin_config
        self.endstop_states = {pin: False for pin in pin_config.get('endstops', [])}
        self.current_positions = {axis: 0 for axis in pin_config.keys() if axis != 'endstops'}
        print("🎮 Симуляция аппаратуры инициализирована")
        print(f"📌 Конфигурация пинов: {pin_config}")

    def move_axis(self, axis: str, steps: int):
        direction = "вперед" if steps > 0 else "назад"
        print(f"🎯 Симуляция: Движение оси {axis}: {abs(steps)} шагов {direction}")

        # Обновляем текущую позицию
        self.current_positions[axis] += steps
        print(f"📊 Ось {axis} новая позиция: {self.current_positions[axis]} шагов")

        time.sleep(0.001 * abs(steps))

    def set_holding_torque(self, axis: str, enable: bool):
        state = "включен" if enable else "выключен"
        print(f"🔒 Симуляция: Ток удержания оси {axis}: {state}")

    def read_endstop(self, pin: int) -> bool:
        # В симуляции всегда возвращаем false (концевик не нажат)
        return self.endstop_states.get(pin, False)

    def emergency_stop(self):
        print("🛑 СИМУЛЯЦИЯ: АВАРИЙНАЯ ОСТАНОВКА - Все двигатели отключены")

    def cleanup(self):
        print("🧹 Ресурсы симуляции освобождены")

    def get_current_position(self, axis: str) -> int:
        """Дополнительный метод для отладки"""
        return self.current_positions.get(axis, 0)