from enum import Enum
from dataclasses import dataclass
from typing import Dict, List, Optional
import threading
import time
import logging

logger = logging.getLogger("StepperControlSystem")

class OperationMode(Enum):
    WORKING = "working"
    CALIBRATION = "calibration"
    HOMING = "homing"

class MovementCommand(Enum):
    MOVE = "move"
    HOLD = "hold"
    DELAYED = "delayed"
    STOP = "stop"
    HOME = "home"

@dataclass
class AxisConfig:
    name: str
    steps_per_degree: float
    max_angle: float
    min_angle: float
    homing_pin: int
    max_speed: float = 10.0
    holding_torque: bool = True

@dataclass
class JogConfig:
    delta_initial: float
    ratio: float
    delta_max: float
    reset_timeout: float

class StepperControlSystem:
    def __init__(self, axes_config: Dict[str, AxisConfig], hardware_interface):
        self.axes = axes_config
        self.hw = hardware_interface
        self.mode = OperationMode.WORKING
        self.current_angles = {name: 0.0 for name in axes_config}
        self.target_angles = {name: 0.0 for name in axes_config}
        self.is_holding = {name: False for name in axes_config}
        
        self.jog_config = {
            'horizontal': JogConfig(0.1, 2.0, 10.0, 2.0),
            'vertical': JogConfig(0.05, 1.8, 5.0, 1.5)
        }
        
        self.jog_multipliers = {name: 0 for name in axes_config}
        self.last_jog_time = {name: 0 for name in axes_config}
        
        self.command_queue = []
        self.is_running = True
        self.lock = threading.Lock()
        
        self.worker_thread = threading.Thread(target=self._command_worker)
        self.worker_thread.daemon = True
        self.worker_thread.start()

    def validate_coordinates(self, coordinates: Dict[str, float]) -> bool:
        try:
            for axis, angle in coordinates.items():
                if axis not in self.axes:
                    raise ValueError(f"Ось {axis} не найдена")
                if not (self.axes[axis].min_angle <= angle <= self.axes[axis].max_angle):
                    raise ValueError(f"Угол {angle} вне диапазона для оси {axis}")
            return True
        except (ValueError, TypeError) as e:
            logger.error(f"Ошибка валидации: {e}")
            return False

    def convert_to_angles(self, coordinates: Dict) -> Dict[str, float]:
        return coordinates

    def plan_trajectory(self, target_angles: Dict[str, float]) -> List[Dict[str, float]]:
        steps = 50
        trajectory = []
        
        for i in range(steps):
            ratio = i / (steps - 1)
            intermediate = {}
            for axis in target_angles:
                start = self.current_angles[axis]
                end = target_angles[axis]
                intermediate[axis] = start + ratio * (end - start)
            trajectory.append(intermediate)
        
        return trajectory

    def execute_movement(self, trajectory: List[Dict[str, float]]):
        for point in trajectory:
            with self.lock:
                for axis, angle in point.items():
                    steps = self._angle_to_steps(axis, angle)
                    self.hw.move_axis(axis, steps)
                    self.current_angles[axis] = angle
            time.sleep(0.01)

    def _angle_to_steps(self, axis: str, angle: float) -> int:
        return int(angle * self.axes[axis].steps_per_degree)

    def _steps_to_angle(self, axis: str, steps: int) -> float:
        return steps / self.axes[axis].steps_per_degree

    def set_holding_torque(self, axis: str, enable: bool):
        self.is_holding[axis] = enable
        self.hw.set_holding_torque(axis, enable)
        logger.info(f"Ток удержания оси {axis}: {'вкл' if enable else 'выкл'}")

    def delayed_positioning(self, coordinates: Dict[str, float], delay_seconds: float):
        def delayed_move():
            time.sleep(delay_seconds)
            self.move_to_coordinates(coordinates)
        
        threading.Thread(target=delayed_move, daemon=True).start()

    def move_to_coordinates(self, coordinates: Dict[str, float]):
        if not self.validate_coordinates(coordinates):
            return False
        
        target_angles = self.convert_to_angles(coordinates)
        trajectory = self.plan_trajectory(target_angles)
        
        with self.lock:
            self.target_angles = target_angles
            self.execute_movement(trajectory)
            
            for axis in coordinates:
                self.set_holding_torque(axis, True)
        
        return True

    def stop_movement(self):
        with self.lock:
            self.hw.emergency_stop()
            for axis in self.axes:
                self.set_holding_torque(axis, False)

    def home_axis(self, axis: str):
        if axis not in self.axes:
            logger.error(f"Ось {axis} не найдена")
            return
        
        self.mode = OperationMode.HOMING
        homing_pin = self.axes[axis].homing_pin
        
        while not self.hw.read_endstop(homing_pin):
            self.hw.move_axis(axis, -10)
            time.sleep(0.1)
        
        self.hw.move_axis(axis, 50)
        time.sleep(0.5)
        
        while not self.hw.read_endstop(homing_pin):
            self.hw.move_axis(axis, -1)
            time.sleep(0.05)
        
        with self.lock:
            self.current_angles[axis] = 0.0
            self.target_angles[axis] = 0.0
        
        self.mode = OperationMode.WORKING
        logger.info(f"Ось {axis} приведена в нулевое положение")

    def geometric_jog(self, axis: str, direction: int):
        """Геометрический джог с проверкой границ"""
        if axis not in self.jog_config:
            logger.error(f"Конфигурация джога для оси {axis} не найдена")
            return

        config = self.jog_config[axis]
        current_time = time.time()

        # Сброс множителя при превышении таймаута
        if current_time - self.last_jog_time[axis] > config.reset_timeout:
            self.jog_multipliers[axis] = 0

        # Расчет текущего шага
        delta = config.delta_initial * (config.ratio ** self.jog_multipliers[axis])
        delta = min(delta, config.delta_max) * direction

        # Вычисление целевого угла с проверкой границ
        target_angle = self.current_angles[axis] + delta
        target_angle = max(self.axes[axis].min_angle, min(target_angle, self.axes[axis].max_angle))

        # Если угол не изменился (достигнут предел), не выполняем движение
        if abs(target_angle - self.current_angles[axis]) < 0.001:
            logger.info(f"Ось {axis} достигла предела: {target_angle}°")
            return

        # Выполнение движения
        self.move_to_coordinates({axis: target_angle})

        # Увеличение множителя для следующего шага
        self.jog_multipliers[axis] += 1
        self.last_jog_time[axis] = current_time

        logger.info(
            f"Джог оси {axis}: Δ={delta:.3f}°, текущий угол: {target_angle:.1f}°, множитель ×{config.ratio ** self.jog_multipliers[axis]:.1f}")

    def reset_jog_multiplier(self, axis: str):
        self.jog_multipliers[axis] = 0
        logger.info(f"Множитель джога оси {axis} сброшен")

    def calibrate_scale(self, axis: str, known_angle: float, measured_steps: int):
        if axis not in self.axes:
            logger.error(f"Ось {axis} не найдена")
            return
        
        new_steps_per_degree = measured_steps / known_angle
        self.axes[axis].steps_per_degree = new_steps_per_degree
        logger.info(f"Ось {axis} откалибрована: {new_steps_per_degree:.3f} шагов/градус")

    def check_linearity(self, axis: str, test_angles: List[float]):
        errors = []
        for target_angle in test_angles:
            self.move_to_coordinates({axis: target_angle})
            time.sleep(1)
            
            measured_angle = self.current_angles[axis]
            error = measured_angle - target_angle
            errors.append((target_angle, error))
            
            logger.info(f"Угол: {target_angle}°, Ошибка: {error:.3f}°")
        
        return errors

    def _command_worker(self):
        while self.is_running:
            if self.command_queue:
                command = self.command_queue.pop(0)
                self._execute_command(command)
            time.sleep(0.1)

    def _execute_command(self, command):
        cmd_type = command.get('type')
        
        if cmd_type == MovementCommand.MOVE:
            self.move_to_coordinates(command['coordinates'])
        elif cmd_type == MovementCommand.HOLD:
            for axis in command['axes']:
                self.set_holding_torque(axis, True)
        elif cmd_type == MovementCommand.DELAYED:
            self.delayed_positioning(
                command['coordinates'],
                command['delay']
            )
        elif cmd_type == MovementCommand.STOP:
            self.stop_movement()
        elif cmd_type == MovementCommand.HOME:
            for axis in command['axes']:
                self.home_axis(axis)

    def add_command(self, command_type: MovementCommand, **kwargs):
        command = {'type': command_type, **kwargs}
        self.command_queue.append(command)

    def shutdown(self):
        self.is_running = False
        self.stop_movement()
        if self.worker_thread.is_alive():
            self.worker_thread.join(timeout=1.0)
        self.hw.cleanup()