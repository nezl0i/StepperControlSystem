from flask import Flask, render_template, request, jsonify
from control_system import StepperControlSystem, AxisConfig
from raspberry_pi_hw import RaspberryPiHardware
from config import DEFAULT_AXES_CONFIG, DEFAULT_PIN_CONFIG
from flask_cors import CORS
import argparse
import logging

app = Flask(__name__, template_folder='../templates', static_folder='../static')
CORS(app)  # Включаем CORS для всех доменов
control_system = None

def parse_arguments():
    parser = argparse.ArgumentParser(description='Web интерфейс управления шаговыми двигателями')
    parser.add_argument('--simulate', action='store_true', help='Режим симуляции без реального оборудования')
    parser.add_argument('--port', type=int, default=5000, help='Порт для веб-сервера')
    parser.add_argument('--host', type=str, default='0.0.0.0', help='Хост для веб-сервера')
    return parser.parse_args()


def init_control_system(simulate=False):
    """Инициализация системы управления"""
    global control_system

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

    # Выбираем аппаратную часть в зависимости от режима
    if simulate:
        from simulated_hw import SimulatedHardware
        hardware = SimulatedHardware(DEFAULT_PIN_CONFIG)
        logging.info("🚀 Запуск в режиме СИМУЛЯЦИИ")
    else:
        try:
            hardware = RaspberryPiHardware(DEFAULT_PIN_CONFIG)
            print("🔧 Запуск с РЕАЛЬНЫМ оборудованием")
        except Exception as e:
            logging.error(f"⚠️  Ошибка инициализации реального оборудования: {e}")
            logging.info("🔄 Переключаемся в режим симуляции")
            from simulated_hw import SimulatedHardware
            hardware = SimulatedHardware(DEFAULT_PIN_CONFIG)

    # Инициализация системы управления
    control_system = StepperControlSystem(axes_config, hardware)
    logging.info("✅ Система управления инициализирована")
    return control_system


@app.before_request
def before_request():
    """Инициализация перед первым запросом"""
    global control_system
    if control_system is None:
        control_system = init_control_system()


@app.route('/')
def index():
    return render_template('control_panel.html')


@app.route('/api/move', methods=['POST'])
def api_move():
    try:
        print("Получен запрос на /api/move")  # Отладочное сообщение
        print("Заголовки:", request.headers)   # Отладочное сообщение
        if control_system is None:
            print("Система не инициализирована")  # Отладочное сообщение
            return jsonify({
                'status': 'error',
                'message': 'Система не инициализирована'
            }), 500

        data = request.json
        print("Полученные данные:", data)  # Отладочное сообщение
        coordinates = {
            'horizontal': float(data['h_angle']),
            'vertical': float(data['v_angle'])
        }

        print("Преобразованные координаты:", coordinates)  # Отладочное сообщение

        speed = float(data.get('speed', 10.0))

        if control_system.move_to_coordinates(coordinates, speed):
            print("Движение успешно начато")  # Отладочное сообщение
            return jsonify({
                'status': 'success',
                'message': 'Движение начато',
                'target_angles': coordinates,
                'speed': speed
            })
        else:
            print("Неверные координаты")  # Отладочное сообщение
            return jsonify({
                'status': 'error',
                'message': 'Неверные координаты'
            }), 400

    except Exception as e:
        print(f"Ошибка в api_move: {str(e)}")  # Отладочное сообщение
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@app.route('/api/jog', methods=['POST'])
def api_jog():
    try:
        if control_system is None:
            return jsonify({
                'status': 'error',
                'message': 'Система не инициализирована'
            }), 500

        data = request.json
        axis = data['axis']
        direction_str = data['direction']

        # Преобразуем строковое направление в числовое
        direction = 1 if direction_str == 'positive' else -1

        control_system.geometric_jog(axis, direction)

        return jsonify({
            'status': 'success',
            'axis': axis,
            'direction': direction_str,
            'current_angle': control_system.current_angles.get(axis, 0)
        })

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@app.route('/api/home', methods=['POST'])
def api_home():
    try:
        if control_system is None:
            return jsonify({
                'status': 'error',
                'message': 'Система не инициализирована'
            }), 500

        data = request.json
        axis = data['axis']

        control_system.home_axis(axis)

        return jsonify({
            'status': 'success',
            'axis': axis,
            'message': 'Поиск нуля выполнен'
        })

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@app.route('/api/stop', methods=['POST'])
def api_stop():
    try:
        if control_system is None:
            return jsonify({
                'status': 'error',
                'message': 'Система не инициализирована'
            }), 500

        control_system.stop_movement()

        return jsonify({
            'status': 'success',
            'message': 'Все движения остановлены'
        })

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@app.route('/api/status', methods=['GET'])
def api_status():
    try:
        if control_system is None:
            return jsonify({
                'status': 'error',
                'message': 'Система не инициализирована'
            }), 500

        return jsonify({
            'status': 'operational',
            'current_angles': control_system.current_angles,
            'is_holding': control_system.is_holding,
            'jog_multipliers': control_system.jog_multipliers
        })

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@app.route('/api/health', methods=['GET'])
def api_health():
    """Проверка здоровья системы"""
    return jsonify({
        'status': 'healthy' if control_system is not None else 'not_initialized',
        'initialized': control_system is not None
    })


if __name__ == '__main__':
    args = parse_arguments()
    # Инициализация при прямом запуске
    control_system = init_control_system(simulate=args.simulate)
    app.run(host='0.0.0.0', port=5000, debug=True)