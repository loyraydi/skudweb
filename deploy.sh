#!/bin/bash

set -e

echo "🚀 Развертывание SKUDWEB на сервере..."

# Проверка наличия .env файла
if [ ! -f .env ]; then
    echo "❌ Файл .env не найден! Создайте его на основе .env.example"
    exit 1
fi

# Загрузка переменных окружения
source .env

echo "📋 Конфигурация:"
echo "   База данных: $MYSQL_DATABASE"
echo "   Пользователь БД: $MYSQL_USER"
echo "   Django порт: $DJANGO_PORT"
echo "   phpMyAdmin порт: $PHPMYADMIN_PORT"

# Остановка существующих контейнеров
echo "🛑 Остановка существующих контейнеров..."
docker-compose down

# Создание необходимых директорий
echo "📁 Создание директорий..."
mkdir -p mysql-init mysql-config nginx ssl logs

# Сборка и запуск контейнеров
echo "🔨 Сборка и запуск контейнеров..."
docker-compose up --build -d

# Ожидание готовности MySQL
echo "⏳ Ожидание готовности MySQL..."
timeout=60
while ! docker-compose exec mysql mysqladmin ping -h localhost --silent; do
    sleep 2
    timeout=$((timeout - 2))
    if [ $timeout -le 0 ]; then
        echo "❌ MySQL не запустился в течение 60 секунд"
        docker-compose logs mysql
        exit 1
    fi
done

echo "✅ MySQL готов!"

# Выполнение миграций
echo "🔄 Выполнение миграций Django..."
docker-compose exec django python manage.py makemigrations --settings=myproject.settings_production
docker-compose exec django python manage.py migrate --settings=myproject.settings_production

# Создание суперпользователя
echo "👤 Создание суперпользователя..."
docker-compose exec django python manage.py shell --settings=myproject.settings_production << EOF
from django.contrib.auth.models import User
from django.contrib.auth.models import Group

# Создание суперпользователя
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@skudweb.local', 'admin123')
    print('✅ Суперпользователь создан: admin/admin123')
else:
    print('ℹ️  Суперпользователь уже существует')

# Создание групп пользователей
groups = ['Администраторы', 'Менеджеры', 'Операторы']
for group_name in groups:
    group, created = Group.objects.get_or_create(name=group_name)
    if created:
        print(f'✅ Группа "{group_name}" создана')
    else:
        print(f'ℹ️  Группа "{group_name}" уже существует')

# Добавление админа в группу администраторов
admin_user = User.objects.get(username='admin')
admin_group = Group.objects.get(name='Администраторы')
admin_user.groups.add(admin_group)
print('✅ Админ добавлен в группу Администраторы')
EOF

# Сбор статических файлов
echo "📦 Сбор статических файлов..."
docker-compose exec django python manage.py collectstatic --noinput --settings=myproject.settings_production

# Проверка статуса сервисов
echo "🔍 Проверка статуса сервисов..."
docker-compose ps

echo ""
echo "🎉 Развертывание завершено успешно!"
echo ""
echo "🌐 Доступные сервисы:"
echo "   🖥️  Django приложение: http://localhost:$DJANGO_PORT"
echo "   🗄️  phpMyAdmin: http://localhost:$PHPMYADMIN_PORT"
echo "   🌍 Nginx (если настроен): http://localhost"
echo ""
echo "📋 Данные для входа:"
echo "   🔐 Django Admin:"
echo "       URL: http://localhost:$DJANGO_PORT/admin/"
echo "       Логин: admin"
echo "       Пароль: admin123"
echo ""
echo "   🗄️  phpMyAdmin:"
echo "       URL: http://localhost:$PHPMYADMIN_PORT"
echo "       Сервер: mysql"
echo "       Логин: $MYSQL_USER"
echo "       Пароль: $MYSQL_PASSWORD"
echo ""
echo "📝 Полезные команды:"
echo "   docker-compose logs -f django    # Просмотр логов Django"
echo "   docker-compose logs -f mysql     # Просмотр логов MySQL"
echo "   docker-compose exec django bash  # Вход в контейнер Django"
echo "   docker-compose down              # Остановка всех сервисов"