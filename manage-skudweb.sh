#!/bin/bash

# Скрипт для управления SKUDWEB системой

show_help() {
    echo "🏢 Управление системой СКУД - SKUDWEB"
    echo "===================================="
    echo ""
    echo "Использование: $0 [команда]"
    echo ""
    echo "Основные команды:"
    echo "  start          - Запустить все сервисы СКУД"
    echo "  stop           - Остановить все сервисы"
    echo "  restart        - Перезапустить все сервисы"
    echo "  rebuild        - Пересобрать и запустить контейнеры"
    echo "  status         - Показать статус всех сервисов"
    echo ""
    echo "Управление Django:"
    echo "  migrate        - Выполнить миграции БД"
    echo "  createsuperuser - Создать администратора СКУД"
    echo "  collectstatic  - Собрать статические файлы"
    echo "  shell          - Открыть Django shell"
    echo "  dbshell        - Открыть MySQL shell"
    echo ""
    echo "Логи и мониторинг:"
    echo "  logs           - Показать логи всех сервисов"
    echo "  logs-web       - Показать логи Django"
    echo "  logs-mysql     - Показать логи MySQL"
    echo "  logs-apache    - Показать логи Apache"
    echo ""
    echo "Резервное копирование:"
    echo "  backup-db      - Создать резервную копию БД СКУД"
    echo "  restore-db     - Восстановить БД из резервной копии"
    echo "  backup-full    - Полное резервное копирование"
    echo ""
    echo "Доступ к сервисам:"
    echo "  urls           - Показать URL всех сервисов"
    echo "  mysql-info     - Показать информацию для подключения к MySQL"
    echo ""
}

get_server_ip() {
    curl -s ifconfig.me 2>/dev/null || echo "localhost"
}

case "$1" in
    start)
        echo "🚀 Запускаем сервисы СКУД..."
        docker-compose up -d
        echo "✅ Сервисы запущены"
        ;;
    stop)
        echo "⏹️  Останавливаем сервисы СКУД..."
        docker-compose down
        echo "✅ Сервисы остановлены"
        ;;
    restart)
        echo "🔄 Перезапускаем сервисы СКУД..."
        docker-compose restart
        echo "✅ Сервисы перезапущены"
        ;;
    rebuild)
        echo "🏗️  Пересобираем контейнеры СКУД..."
        docker-compose down
        docker-compose up -d --build
        echo "✅ Контейнеры пересобраны и запущены"
        ;;
    status)
        echo "📊 Статус сервисов СКУД:"
        docker-compose ps
        ;;
    migrate)
        echo "🗃️  Выполняем миграции БД СКУД..."
        docker-compose exec web python manage.py migrate
        echo "✅ Миграции выполнены"
        ;;
    createsuperuser)
        echo "👤 Создаем администратора СКУД..."
        docker-compose exec web python manage.py createsuperuser
        ;;
    collectstatic)
        echo "📦 Собираем статические файлы..."
        docker-compose exec web python manage.py collectstatic --noinput
        echo "✅ Статические файлы собраны"
        ;;
    shell)
        echo "🐚 Открываем Django shell..."
        docker-compose exec web python manage.py shell
        ;;
    dbshell)
        echo "🗄️  Открываем MySQL shell..."
        docker-compose exec mysql mysql -u skudweb_user -p skudweb_db
        ;;
    logs)
        echo "📊 Показываем логи всех сервисов..."
        docker-compose logs -f
        ;;
    logs-web)
        echo "📊 Показываем логи Django..."
        docker-compose logs -f web
        ;;
    logs-mysql)
        echo "📊 Показываем логи MySQL..."
        docker-compose logs -f mysql
        ;;
    logs-apache)
        echo "📊 Показываем логи Apache..."
        docker-compose logs -f apache
        ;;
    backup-db)
        echo "💾 Создаем резервную копию БД СКУД..."
        BACKUP_FILE="skudweb_backup_$(date +%Y%m%d_%H%M%S).sql"
        docker-compose exec mysql mysqldump -u skudweb_user -p skudweb_db > "$BACKUP_FILE"
        echo "✅ Резервная копия сохранена: $BACKUP_FILE"
        ;;
    restore-db)
        if [ -z "$2" ]; then
            echo "❌ Укажите файл резервной копии: $0 restore-db backup.sql"
            exit 1
        fi
        echo "🔄 Восстанавливаем БД СКУД из $2..."
        docker-compose exec -T mysql mysql -u skudweb_user -p skudweb_db < "$2"
        echo "✅ БД восстановлена"
        ;;
    backup-full)
        echo "💾 Создаем полное резервное копирование СКУД..."
        BACKUP_DIR="skudweb_full_backup_$(date +%Y%m%d_%H%M%S)"
        mkdir -p "$BACKUP_DIR"
        
        # Резервная копия БД
        docker-compose exec mysql mysqldump -u skudweb_user -p skudweb_db > "$BACKUP_DIR/database.sql"
        
        # Копируем медиа файлы
        docker cp $(docker-compose ps -q web):/app/media "$BACKUP_DIR/"
        
        # Копируем конфигурацию
        cp -r apache mysql .env docker-compose.yml "$BACKUP_DIR/"
        
        echo "✅ Полное резервное копирование сохранено в: $BACKUP_DIR"
        ;;
    urls)
        SERVER_IP=$(get_server_ip)
        echo "🌐 URL сервисов СКУД:"
        echo "   Веб-интерфейс СКУД: http://$SERVER_IP"
        echo "   phpMyAdmin:         http://$SERVER_IP:8080"
        echo "   MySQL:              $SERVER_IP:3306"
        ;;
    mysql-info)
        echo "🗄️  Информация для подключения к MySQL:"
        echo "   Хост: $(get_server_ip):3306"
        echo "   База данных: skudweb_db"
        echo "   Пользователь: skudweb_user"
        echo "   Пароль: (см. файл .env)"
        echo ""
        echo "📊 phpMyAdmin: http://$(get_server_ip):8080"
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        echo "❌ Неизвестная команда: $1"
        echo ""
        show_help
        exit 1
        ;;
esac