from dataclasses import dataclass
from typing import Dict, List

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

# Конфигурация по умолчанию
DEFAULT_AXES_CONFIG = {
    'horizontal': AxisConfig(
        name='horizontal',
        steps_per_degree=100.0,
        max_angle=360.0,
        min_angle=0.0,
        homing_pin=5,
        max_speed=20.0
    ),
    'vertical': AxisConfig(
        name='vertical',
        steps_per_degree=150.0,
        max_angle=90.0,
        min_angle=0.0,
        homing_pin=6,
        max_speed=10.0
    )
}

DEFAULT_JOG_CONFIG = {
    'horizontal': JogConfig(
        delta_initial=0.1,
        ratio=2.0,
        delta_max=10.0,
        reset_timeout=2.0
    ),
    'vertical': JogConfig(
        delta_initial=0.05,
        ratio=1.8,
        delta_max=5.0,
        reset_timeout=1.5
    )
}

DEFAULT_PIN_CONFIG = {
    'horizontal': [17, 18, 27, 22],
    'vertical': [23, 24, 25, 4],
    'endstops': [5, 6]
}

# Настройки логирования
LOG_CONFIG = {
    'level': 'INFO',
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'filename': 'stepper_system.log'
}