# 🎯 Система управления шаговыми двигателями

![Python](https://img.shields.io/badge/Python-3.8%2B-3776AB?logo=python&logoColor=white)
![Raspberry Pi](https://img.shields.io/badge/Raspberry%20Pi-Поддержка-C51A4A?logo=raspberrypi)
![Flask](https://img.shields.io/badge/Веб%20интерфейс-Flask-000000?logo=flask)
![Лицензия](https://img.shields.io/badge/Лицензия-MIT-green)
![Статус](https://img.shields.io/badge/Статус-Активно%20разрабатывается-blue)

Продвинутая система управления шаговыми двигателями на Python с веб-интерфейсом, геометрическим джогом и прецизионным позиционированием. Поддерживает различные драйверы и оборудование.

## 📋 Оглавление

- [✨ Возможности](#-возможности)
- [🏗️ Структура проекта](#️-структура-проекта)
- [🚀 Быстрый старт](#-быстрый-старт)
- [⚙️ Конфигурация](#️-конфигурация)
- [🎮 Использование](#-использование)
- [🌐 Веб-интерфейс](#-веб-интерфейс)
- [🛠️ Поддерживаемое оборудование](#️-поддерживаемое-оборудование)
- [🧪 Тестирование](#-тестирование)
- [🤝 Участие в разработке](#-участие-в-разработке)
- [📝 Лицензия](#-лицензия)
- [📞 Поддержка](#-поддержка)
- [🎯 Планы развития](#-планы-развития)

## ✨ Возможности

### 🎯 Рабочий режим
- **✅ Валидация координат** - Проверка и преобразование входных данных
- **📈 Планирование траектории** - Плавное движение с интерполяцией
- **🔒 Удержание позиции** - Регулировка тока удержания после позиционирования
- **⏰ Отложенное позиционирование** - Выполнение команд по таймеру
- **🛑 Аварийная остановка** - Мгновенная остановка движения

### ⚙️ Режим выверки
- **🏠 Поиск нуля (Homing)** - Автоматический поиск по концевым выключателям
- **📏 Калибровка шкалы** - Коррекция коэффициентов steps-per-degree
- **📊 Проверка линейности** - Измерение и анализ погрешности позиционирования
- **🎯 Тонкая доводка** - Прецизионная регулировка с субградусной точностью

### 🎮 Геометрический джог
- **📐 Адаптивный шаг** - Δₖ = Δ₀ · rᵏ геометрическая прогрессия
- **⚙️ Индивидуальные настройки** - Раздельные параметры для каждой оси
- **🔄 Автосброс** - Автоматический сброс множителя по таймауту
- **👁️ Визуальная обратная связь** - Реальное отображение множителя и предпросмотр

## 🏗️ Структура проекта

```bash
stepper-control-system/
├── 📁 src/                    # Исходный код
│   ├── 🐍 main.py            # Главное приложение
│   ├── 🐍 control_system.py  # Основной класс системы управления
│   ├── 🐍 hardware_interface.py # Абстракция аппаратного слоя
│   ├── 🐍 raspberry_pi_hw.py # Реализация для Raspberry Pi
│   ├── 🐍 web_interface.py   # Веб-сервер на Flask
│   └── 🐍 config.py          # Конфигурационные параметры
├── 📁 templates/             # HTML шаблоны
│   └── 🏗️ control_panel.html # Панель управления
├── 📁 static/               # Статические файлы
│   ├── 📁 css/
│   │   └── 🎨 style.css     # Стили оформления
│   └── 📁 js/
│       └── ⚡ script.js     # Клиентский JavaScript
├── 📁 tests/                # Тесты
│   ├── 🧪 test_control_system.py
│   └── 🧪 test_hardware.py
├── 📄 requirements.txt      # Зависимости Python
├── 📄 LICENSE              # Лицензия MIT
└── 📄 README.md            # Эта документация
```
## 🚀 Быстрый старт
### Установка и настройка
```bash
# 1. Клонирование репозитория
git clone https://github.com/NeZl0i/StepperControlSystem.git
cd StepperControlSystem

# 2. Установка зависимостей
pip install -r requirements.txt

# 3. Настройка конфигурации (отредактируйте под ваше железо)
nano src/config.py
```
### Запуск системы
```bash
# Запуск в основном режиме
python src/main.py

# Запуск с веб-интерфейсом
python src/web_interface.py

# Тестовый режим (без реального оборудования)
python src/main.py --simulate

# Запуск с конкретным config файлом
python src/main.py --config my_config.py
```
### После запуска веб-интерфейса откройте в браузере:
http://localhost:5000

## ⚙️ Конфигурация
### Базовая конфигурация осей
```python
# config.py
AXES_CONFIG = {
    'horizontal': {
        'steps_per_degree': 100.0,    # Шагов на градус вращения
        'max_angle': 360.0,           # Максимальный угол поворота
        'min_angle': 0.0,             # Минимальный угол поворота
        'homing_pin': 5,              # Пин концевого выключателя
        'max_speed': 20.0,            # Макс. скорость (град/сек)
        'holding_torque': True        # Включение удержания позиции
    },
    'vertical': {
        'steps_per_degree': 150.0,
        'max_angle': 90.0,
        'min_angle': 0.0,
        'homing_pin': 6,
        'max_speed': 10.0,
        'holding_torque': True
    }
}
```
### Настройка геометрического джога
```python
JOG_CONFIG = {
    'horizontal': {
        'delta_initial': 0.1,     # Δ₀ - начальный шаг (градусы)
        'ratio': 2.0,             # r - коэффициент прогрессии
        'delta_max': 10.0,        # Δ_max - максимальный шаг
        'reset_timeout': 2.0      # T_reset - время сброса (сек)
    },
    'vertical': {
        'delta_initial': 0.05,
        'ratio': 1.8,
        'delta_max': 5.0,
        'reset_timeout': 1.5
    }
}
```
### Конфигурация пинов
```python
PIN_CONFIG = {
    'horizontal': [17, 18, 27, 22],  # Пины управления двигателем
    'vertical': [23, 24, 25, 4],
    'endstops': [5, 6]              # Пины концевых выключателей
}
```
## 🎮 Использование
### Базовые команды Python API
```python
from src.control_system import StepperControlSystem
from src.raspberry_pi_hw import RaspberryPiHardware

# Инициализация системы
hardware = RaspberryPiHardware(PIN_CONFIG)
system = StepperControlSystem(AXES_CONFIG, hardware)

# Основные операции
system.move_to_coordinates({'horizontal': 45.0, 'vertical': 30.0})
system.geometric_jog('horizontal', 1)  # Положительное направление
system.geometric_jog('vertical', -1)   # Отрицательное направление
system.home_axis('horizontal')         # Поиск нуля
system.stop_movement()                 # Аварийная остановка

# Отложенное выполнение
system.delayed_positioning(
    {'horizontal': 90.0, 'vertical': 45.0},
    delay_seconds=10.0
)
```
### Пример работы с очередью команд
```python
# Добавление команд в очередь
system.add_command('move', coordinates={'horizontal': 30.0})
system.add_command('hold', axes=['horizontal'])
system.add_command('delayed', 
                  coordinates={'vertical': 60.0}, 
                  delay=5.0)
```
## 🌐 Веб-интерфейс
### API Endpoints
```
Метод	Endpoint	Описание                      Параметры

POST	/api/move	Перемещение к координатам    {"h_angle": 45.0, "v_angle": 30.0}
POST	/api/jog	Геометрический джог	     {"axis": "horizontal", "direction": "positive"}
POST	/api/home	Поиск нулевой позиции	     {"axis": "horizontal"}
POST	/api/hold	Управление удержанием	     {"axis": "horizontal", "enable": true}
POST	/api/stop	Аварийная остановка	     {}
GET	/api/status	Получение статуса системы    -
```
### Примеры HTTP запросов
```bash
# Перемещение осей
curl -X POST http://localhost:5000/api/move \
  -H "Content-Type: application/json" \
  -d '{"h_angle": 45.0, "v_angle": 30.0}'

# Джог горизонтальной оси
curl -X POST http://localhost:5000/api/jog \
  -H "Content-Type: application/json" \
  -d '{"axis": "horizontal", "direction": "positive"}'

# Получение статуса системы
curl http://localhost:5000/api/status

# Поиск нуля вертикальной оси
curl -X POST http://localhost:5000/api/home \
  -H "Content-Type: application/json" \
  -d '{"axis": "vertical"}'
```
## 🛠️ Поддерживаемое оборудование
### Контроллеры
- Raspberry Pi (полная поддержка через GPIO)
- Arduino (через последовательный порт)
- Любые другие контроллеры с Python API
### Драйверы двигателей
- ULN2003 (для моторов 28BYJ-48)
- A4988 (Step/Dir драйверы)
- DRV8825 (Высокоточные драйверы)
- TMC2208/TMC2209 (Бесшумные драйверы)
- Любые другие Step/Dir совместимые драйверы
### Датчики и периферия
- Концевые выключатели (механические, оптические)
- Инкрементальные энкодеры (опционально)
- Датчики тока и температуры
- RGB LED индикация состояния
## 🧪 Тестирование
### Запуск тестов
```bash
# Запуск всех тестов
pytest tests/

# С подробным выводом
pytest -v tests/

# С покрытием кода
pytest --cov=src tests/

# Конкретный тестовый файл
pytest tests/test_control_system.py -v

# Тесты с генерацией отчета
pytest --cov=src --cov-report=html tests/
```
### Типы тестов
- Модульные тесты - Тестирование отдельных компонентов
- Интеграционные тесты - Проверка взаимодействия модулей
- Аппаратные тесты - Тесты с реальным железом (требуют подключения)
- Симуляционные тесты - Тесты без реального оборудования
## 📝 Лицензия
Этот проект распространяется под лицензией MIT. Подробнее см. в файле LICENSE.
```text
MIT License
Copyright (c) 2025 NeZl0i
```

