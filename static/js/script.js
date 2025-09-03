// static/js/script.js
const API_BASE = window.location.origin;

let statusInterval;

// Инициализация
document.addEventListener('DOMContentLoaded', function() {
    updateStatus();
    setupEventListeners();
    startStatusPolling();
});

function setupEventListeners() {
    // Обработка формы перемещения
    document.getElementById('moveForm').addEventListener('submit', function(e) {
        e.preventDefault();
        moveToCoordinates();
    });

    // Обновление значения скорости
    document.getElementById('speed').addEventListener('input', function() {
        document.getElementById('speedValue').textContent = this.value + ' град/сек';
    });
}

function startStatusPolling() {
    statusInterval = setInterval(updateStatus, 2000);
}

async function updateStatus() {
    try {
        const response = await fetch(`${API_BASE}/api/status`);
        const data = await response.json();
        
        if (data.status === 'operational') {
            updateUI(data);
        }
    } catch (error) {
        console.error('Ошибка получения статуса:', error);
        showError('Не удалось получить статус системы');
    }
}

function updateUI(data) {
    // Обновление текущих позиций
    document.getElementById('currentH').textContent = data.current_angles.horizontal.toFixed(1) + '°';
    document.getElementById('currentV').textContent = data.current_angles.vertical.toFixed(1) + '°';
    
    // Обновление статуса удержания
    const holding = data.is_holding.horizontal || data.is_holding.vertical;
    document.getElementById('holdingStatus').textContent = holding ? 'Вкл' : 'Выкл';
    document.getElementById('holdingStatus').style.color = holding ? '#2ed573' : '#ff4757';
    
    // Обновление множителей джога
    document.getElementById('hMultiplier').textContent = `×${Math.pow(2, data.jog_multipliers.horizontal).toFixed(1)}`;
    document.getElementById('vMultiplier').textContent = `×${Math.pow(1.8, data.jog_multipliers.vertical).toFixed(1)}`;
    
    // Обновление индикатора статуса
    const indicator = document.querySelector('.status-indicator');
    indicator.classList.add('connected');
}

async function moveToCoordinates() {
    console.log("Функция moveToCoordinates вызвана");

    const hAngle = parseFloat(document.getElementById('hAngle').value);
    const vAngle = parseFloat(document.getElementById('vAngle').value);
    const speed = parseFloat(document.getElementById('speed').value);

    console.log("Параметры:", { hAngle, vAngle, speed }); // Отладочное сообщение

    try {
        const response = await fetch(`${API_BASE}/api/move`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                h_angle: hAngle,
                v_angle: vAngle,
                speed: speed
            })
        });

        console.log("Ответ сервера:", response); // Отладочное сообщение

        const data = await response.json();
        
        if (data.status === 'success') {
            showSuccess('Движение начато');
        } else {
            showError(data.message || 'Ошибка перемещения');
        }
    } catch (error) {
        console.error('Ошибка:', error);
        showError('Не удалось выполнить перемещение');
    }
}

async function jog(axis, direction) {
    try {
        const response = await fetch(`${API_BASE}/api/jog`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                axis: axis,
                direction: direction // отправляем как строку
            })
        });

        const data = await response.json();

        if (data.status === 'success') {
            showSuccess(`Джог оси ${axis} (${direction}) выполнен`);
            updateStatus(); // Обновляем статус после движения
        } else {
            showError(data.message || 'Ошибка джога');
        }
    } catch (error) {
        console.error('Ошибка:', error);
        showError('Не удалось выполнить джог');
    }
}

async function homeAxis(axis) {
    try {
        const response = await fetch(`${API_BASE}/api/home`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                axis: axis
            })
        });

        const data = await response.json();
        
        if (data.status === 'success') {
            showSuccess(`Поиск нуля оси ${axis} выполнен`);
        } else {
            showError(data.message || 'Ошибка поиска нуля');
        }
    } catch (error) {
        console.error('Ошибка:', error);
        showError('Не удалось выполнить поиск нуля');
    }
}

async function emergencyStop() {
    if (!confirm('Вы уверены, что хотите выполнить аварийную остановку?')) {
        return;
    }

    try {
        const response = await fetch(`${API_BASE}/api/stop`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({})
        });

        const data = await response.json();
        
        if (data.status === 'success') {
            showSuccess('Аварийная остановка выполнена', 'warning');
        } else {
            showError(data.message || 'Ошибка остановки');
        }
    } catch (error) {
        console.error('Ошибка:', error);
        showError('Не удалось выполнить остановку');
    }
}

function showSuccess(message, type = 'success') {
    showNotification(message, type);
}

function showError(message) {
    showNotification(message, 'error');
}

function showNotification(message, type = 'info') {
    // Реализация уведомлений (можно использовать toast библиотеку)
    console.log(`[${type}] ${message}`);
    alert(`[${type.toUpperCase()}] ${message}`);
}