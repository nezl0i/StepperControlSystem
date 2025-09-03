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
//        console.error('Ошибка получения статуса:', error);
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
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            body: JSON.stringify({
                h_angle: hAngle,
                v_angle: vAngle,
                speed: speed
            })
        });

        console.log("Статус ответа:", response.status);
        console.log("Заголовки ответа:", response.headers);

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        console.log("Данные ответа:", data);
        
        if (data.status === 'success') {
            showSuccess('Движение начато');
            updateStatus();
        } else {
            showError(data.message || 'Ошибка перемещения');
        }
    } catch (error) {
        console.error('Ошибка:', error);
        showError(`Ошибка связи с сервером: ${error.message}`);
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
    // Создаем контейнер для уведомлений если его нет
    let container = document.getElementById('notification-container');
    if (!container) {
        container = document.createElement('div');
        container.id = 'notification-container';
        container.className = 'notification-container';
        document.body.appendChild(container);
    }

    // Создаем уведомление
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;

    // Иконка в зависимости от типа
    let icon = '💡';
    switch (type) {
        case 'success':
            icon = '✅';
            break;
        case 'error':
            icon = '❌';
            break;
        case 'warning':
            icon = '⚠️';
            break;
        case 'info':
            icon = 'ℹ️';
            break;
    }

    notification.innerHTML = `
        <span class="notification-icon">${icon}</span>
        <span class="notification-content">${message}</span>
        <button class="notification-close" onclick="this.parentElement.remove()">×</button>
    `;

    // Добавляем уведомление в контейнер
    container.appendChild(notification);

    // Анимация появления
    setTimeout(() => {
        notification.classList.add('show');
    }, 10);

    // Автоматическое скрытие через 5 секунд
    const autoRemove = setTimeout(() => {
        hideNotification(notification);
    }, 5000);

    // Останавливаем таймер при наведении
    notification.addEventListener('mouseenter', () => {
        clearTimeout(autoRemove);
    });

    // Запускаем таймер снова когда убираем мышь
    notification.addEventListener('mouseleave', () => {
        setTimeout(() => {
            hideNotification(notification);
        }, 3000);
    });

    // Обработчик закрытия по клику на крестик
    notification.querySelector('.notification-close').addEventListener('click', () => {
        clearTimeout(autoRemove);
        hideNotification(notification);
    });
}

function hideNotification(notification) {
    notification.classList.remove('show');
    notification.classList.add('hide');

    // Удаляем элемент после анимации
    setTimeout(() => {
        if (notification.parentElement) {
            notification.parentElement.removeChild(notification);
        }
    }, 300);
}

function showSuccess(message) {
    showNotification(message, 'success');
}

function showError(message) {
    showNotification(message, 'error');
}

function showWarning(message) {
    showNotification(message, 'warning');
}

function showInfo(message) {
    showNotification(message, 'info');
}

// Примеры использования:
// showSuccess('Движение успешно начато!');
// showError('Ошибка подключения к серверу');
// showWarning('Достигнут предел движения');
// showInfo('Система инициализирована');
