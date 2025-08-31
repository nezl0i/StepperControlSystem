from flask import Flask, render_template, request, jsonify
from control_system import StepperControlSystem, MovementCommand
from raspberry_pi_hw import RaspberryPiHardware
import logging

app = Flask(__name__)
control_system = None

def create_app(config=None):
    global control_system
    
    # Конфигурация по умолчанию
    default_config = {
        'axes': {
            'horizontal': {
                'steps_per_degree': 100.0,
                'max_angle': 360.0,
                'min_angle': 0.0,
                'homing_pin': 5,
                'max_speed': 20.0
            },
            'vertical': {
                'steps_per_degree': 150.0,
                'max_angle': 90.0,
                'min_angle': 0.0,
                'homing_pin': 6,
                'max_speed': 10.0
            }
        },
        'pins': {
            'horizontal': [17, 18, 27, 22],
            'vertical': [23, 24, 25, 4],
            'endstops': [5, 6]
        }
    }
    
    config = config or default_config
    
    # Инициализация аппаратной части
    hardware = RaspberryPiHardware(config['pins'])
    
    # Инициализация системы управления
    control_system = StepperControlSystem(config['axes'], hardware)
    
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