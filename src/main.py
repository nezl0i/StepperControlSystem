import argparse
import logging
from control_system import StepperControlSystem, AxisConfig
from raspberry_pi_hw import RaspberryPiHardware
from simulated_hw import SimulatedHardware
from config import DEFAULT_AXES_CONFIG, DEFAULT_PIN_CONFIG, LOG_CONFIG

def setup_logging():
    logging.basicConfig(
        level=getattr(logging, LOG_CONFIG['level']),
        format=LOG_CONFIG['format'],
        filename=LOG_CONFIG.get('filename')
    )

def main():
    parser = argparse.ArgumentParser(description='Система управления шаговыми двигателями')
    parser.add_argument('--simulate', action='store_true', help='Режим симуляции без железа')
    parser.add_argument('--config', type=str, help='Файл конфигурации')
    args = parser.parse_args()
    
    setup_logging()
    logger = logging.getLogger("Main")
    
    try:
        # Конвертируем словарь конфигурации в объекты AxisConfig
        axes_config = {}
        for axis_name, axis_data in DEFAULT_AXES_CONFIG.items():
            axes_config[axis_name] = AxisConfig(
                name=axis_name,
                steps_per_degree=axis_data['steps_per_degree'],
                max_angle=axis_data['max_angle'],
                min_angle=axis_data['min_angle'],
                homing_pin=axis_data['homing_pin'],
                max_speed=axis_data.get('max_speed', 10.0),
                holding_torque=axis_data.get('holding_torque', True)
            )

        if args.simulate:
            hardware = SimulatedHardware(DEFAULT_PIN_CONFIG)
            logger.info("Запуск в режиме симуляции")
        else:
            hardware = RaspberryPiHardware(DEFAULT_PIN_CONFIG)
            logger.info("Запуск с реальным оборудованием")
        
        control_system = StepperControlSystem(DEFAULT_AXES_CONFIG, hardware)
        logger.info("Система управления инициализирована")
        
        # Пример работы системы
        control_system.move_to_coordinates({'horizontal': 45.0, 'vertical': 30.0})
        
        # Ожидание завершения
        input("Нажмите Enter для завершения...")
        
    except KeyboardInterrupt:
        logger.info("Программа прервана пользователем")
    except Exception as e:
        logger.error(f"Ошибка при выполнении: {e}")
    finally:
        if 'control_system' in locals():
            control_system.shutdown()
        logger.info("Система завершена")

if __name__ == '__main__':
    main()