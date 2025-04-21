/**
 * Система уведомлений для всего проекта
 */

// Глобальный объект для управления уведомлениями
const AppNotifications = {
    // Показать уведомление
    show: function(message, type = 'success', title = '', duration = 3000) {
        // Создаем уникальный контейнер для уведомлений, если он не существует
        let container = document.getElementById('app-notifications');

        if (!container) {
            container = document.createElement('div');
            container.id = 'app-notifications';
            container.style.position = 'fixed';
            container.style.bottom = '20px';
            container.style.right = '20px';
            container.style.zIndex = '9999';
            document.body.appendChild(container);
        }

        // Создаем уведомление
        const notification = document.createElement('div');
        notification.className = `app-notification app-notification-${type}`;

        // Определяем иконку в зависимости от типа
        let icon = '';
        switch(type) {
            case 'success':
                icon = '<i class="bx bx-check-circle" style="color:#0dc8ee"></i>';
                break;
            case 'error':
                icon = '<i class="bx bx-x-circle" style="color:#dc3545"></i>';
                break;
            case 'warning':
                icon = '<i class="bx bx-error" style="color:#ffc107"></i>';
                break;
            case 'info':
            default:
                icon = '<i class="bx bx-info-circle" style="color:#0dc8ee"></i>';
                break;
        }

        // Создаем содержимое уведомления
        notification.innerHTML = `
            <div class="notification-icon">${icon}</div>
            <div class="notification-content">
                ${title ? `<div class="notification-title">${title}</div>` : ''}
                <div class="notification-message">${message}</div>
            </div>
            <div class="notification-close">&times;</div>
            <div class="notification-progress"></div>
        `;

        // Добавляем стили непосредственно к элементу
        notification.style.backgroundColor = '#212529';
        notification.style.color = 'white';
        notification.style.padding = '15px';
        notification.style.marginBottom = '10px';
        notification.style.borderRadius = '8px';
        notification.style.boxShadow = '0 4px 12px rgba(0, 0, 0, 0.3)';
        notification.style.display = 'flex';
        notification.style.alignItems = 'center';
        notification.style.width = 'auto';
        notification.style.maxWidth = '350px';
        notification.style.transform = 'translateX(100%)';
        notification.style.opacity = '0';
        notification.style.transition = 'transform 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275), opacity 0.4s ease';
        notification.style.overflow = 'hidden';
        notification.style.position = 'relative';

        // Устанавливаем цвет границы в зависимости от типа
        switch(type) {
            case 'success':
                notification.style.borderLeft = '4px solid #4a6cf7';
                break;
            case 'error':
                notification.style.borderLeft = '4px solid #dc3545';
                break;
            case 'warning':
                notification.style.borderLeft = '4px solid #ffc107';
                break;
            case 'info':
            default:
                notification.style.borderLeft = '4px solid #4a6cf7';
                break;
        }

        // Добавляем в контейнер
        container.appendChild(notification);

        // Стили для иконки
        const iconElement = notification.querySelector('.notification-icon');
        iconElement.style.marginRight = '15px';
        iconElement.style.fontSize = '20px';
        iconElement.style.display = 'flex';
        iconElement.style.alignItems = 'center';
        iconElement.style.justifyContent = 'center';

        // Стили для контента
        const contentElement = notification.querySelector('.notification-content');
        contentElement.style.flexGrow = '1';

        // Стили для заголовка
        if (title) {
            const titleElement = notification.querySelector('.notification-title');
            titleElement.style.fontWeight = 'bold';
            titleElement.style.marginBottom = '5px';
            titleElement.style.fontSize = '16px';
        }

        // Стили для сообщения
        const messageElement = notification.querySelector('.notification-message');
        messageElement.style.fontSize = '14px';
        messageElement.style.opacity = '0.9';

        // Стили для кнопки закрытия
        const closeButton = notification.querySelector('.notification-close');
        closeButton.style.cursor = 'pointer';
        closeButton.style.fontSize = '18px';
        closeButton.style.marginLeft = '10px';
        closeButton.style.opacity = '0.7';
        closeButton.style.transition = 'opacity 0.2s';

        // Добавляем обработчик для кнопки закрытия
        closeButton.addEventListener('click', () => {
            this.hide(notification);
        });

        closeButton.addEventListener('mouseover', () => {
            closeButton.style.opacity = '1';
        });

        closeButton.addEventListener('mouseout', () => {
            closeButton.style.opacity = '0.7';
        });

        // Стили для прогресс-бара
        const progressBar = notification.querySelector('.notification-progress');
        progressBar.style.position = 'absolute';
        progressBar.style.bottom = '0';
        progressBar.style.left = '0';
        progressBar.style.height = '3px';
        progressBar.style.backgroundColor = 'rgba(255, 255, 255, 0.5)';
        progressBar.style.width = '100%';
        progressBar.style.transformOrigin = 'left';

        // Показываем уведомление с анимацией
        setTimeout(() => {
            notification.style.transform = 'translateX(0)';
            notification.style.opacity = '1';

            // Анимируем прогресс-бар
            if (progressBar && duration > 0) {
                progressBar.style.transition = `width ${duration}ms linear`;
                progressBar.style.width = '0';
            }
        }, 10);

        // Автоматически скрываем через указанное время
        if (duration > 0) {
            setTimeout(() => {
                this.hide(notification);
            }, duration);
        }

        // Закрываем по клику
        notification.addEventListener('click', (e) => {
            if (!e.target.classList.contains('notification-close')) {
                this.hide(notification);
            }
        });

        return notification;
    },

    // Скрыть уведомление
    hide: function(notification) {
        notification.style.transform = 'translateX(100%)';
        notification.style.opacity = '0';

        // Удаляем элемент после завершения анимации
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 400);
    },

    // Показать уведомление об успехе
    success: function(message, title = '', duration = 3000) {
        return this.show(message, 'success', title, duration);
    },

    // Показать уведомление об ошибке
    error: function(message, title = '', duration = 3000) {
        return this.show(message, 'error', title, duration);
    },

    // Показать предупреждение
    warning: function(message, title = '', duration = 3000) {
        return this.show(message, 'warning', title, duration);
    },

    // Показать информационное уведомление
    info: function(message, title = '', duration = 3000) {
        return this.show(message, 'info', title, duration);
    }
};