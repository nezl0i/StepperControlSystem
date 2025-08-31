import argparse
import logging
from control_system import StepperControlSystem
from raspberry_pi_hw import RaspberryPiHardware
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
        if args.simulate:
            from .simulated_hw import SimulatedHardware
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