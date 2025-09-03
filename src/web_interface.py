from flask import Flask, render_template, request, jsonify
from control_system import StepperControlSystem, MovementCommand, AxisConfig
from raspberry_pi_hw import RaspberryPiHardware
from config import DEFAULT_AXES_CONFIG, DEFAULT_PIN_CONFIG
import logging

app = Flask(__name__, template_folder='../templates', static_folder='../static')
control_system = None

def create_app(config=None):
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

    # Инициализация аппаратной части
    hardware = RaspberryPiHardware(DEFAULT_PIN_CONFIG)

    # Инициализация системы управления
    control_system = StepperControlSystem(axes_config, hardware)
    
    return app

@app.route('/')
def index():
    return render_template('control_panel.html')

@app.route('/api/move', methods=['POST'])
def api_move():
    try:
        data = request.json
        coordinates = {
            'horizontal': float(data['h_angle']),
            'vertical': float(data['v_angle'])
        }
        
        speed = float(data.get('speed', 10.0))
        
        if control_system.move_to_coordinates(coordinates):
            return jsonify({
                'status': 'success',
                'message': 'Движение начато',
                'target_angles': coordinates
            })
        else:
            return jsonify({
                'status': 'error',
                'message': 'Неверные координаты'
            }), 400
            
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/jog', methods=['POST'])
def api_jog():
    try:
        data = request.json
        axis = data['axis']
        direction = 1 if data['direction'] == 'positive' else -1
        
        control_system.geometric_jog(axis, direction)
        
        return jsonify({
            'status': 'success',
            'axis': axis,
            'direction': 'positive' if direction == 1 else 'negative'
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/home', methods=['POST'])
def api_home():
    try:
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

if __name__ == '__main__':
    create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)