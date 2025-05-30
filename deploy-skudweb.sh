#!/bin/bash

# Скрипт для развертывания SKUDWEB на Ubuntu 22.04

set -e

echo "🏢 Развертывание системы СКУД - SKUDWEB"
echo "======================================="

# Проверяем, что мы в правильной директории
if [ ! -f "requirement.txt" ]; then
    echo "❌ Ошибка: файл requirement.txt не найден!"
    echo "Убедитесь, что вы находитесь в директории проекта SKUDWEB"
    exit 1
fi

# Обновляем систему
echo "📦 Обновляем систему Ubuntu..."
sudo apt update && sudo apt upgrade -y

# Устанавливаем необходимые пакеты
echo "🔧 Устанавливаем необходимые пакеты..."
sudo apt install -y git curl software-properties-common apt-transport-https ca-certificates netcat

# Устанавливаем Docker если его нет
if ! command -v docker &> /dev/null; then
    echo "🐳 Устанавливаем Docker..."
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
    sudo apt update
    sudo apt install -y docker-ce docker-ce-cli containerd.io
fi

# Устанавливаем Docker Compose если его нет
if ! command -v docker-compose &> /dev/null; then
    echo "🔧 Устанавливаем Docker Compose..."
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
fi

# Добавляем пользователя в группу docker
echo "👤 Настраиваем права пользователя..."
sudo usermod -aG docker $USER

# Создаем директории для Apache
echo "📁 Создаем директории конфигурации..."
mkdir -p apache mysql ssl

# Создаем .env файл если его нет
if [ ! -f ".env" ]; then
    echo "⚙️ Создаем файл окружения..."
    
    # Генерируем пароли
    MYSQL_PASSWORD=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-25)
    MYSQL_ROOT_PASSWORD=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-25)
    SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_urlsafe(50))')
    
    cat > .env << EOF
# Django настройки для SKUDWEB
SECRET_KEY=$SECRET_KEY
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1,$(curl -s ifconfig.me 2>/dev/null || echo "your-domain.com")

# MySQL настройки
MYSQL_DATABASE=skudweb_db
MYSQL_USER=skudweb_user
MYSQL_PASSWORD=$MYSQL_PASSWORD
MYSQL_ROOT_PASSWORD=$MYSQL_ROOT_PASSWORD
MYSQL_HOST=mysql
MYSQL_PORT=3306

# Настройки СКУД системы
SKUD_COMPANY_NAME=Ваша компания
SKUD_ADMIN_EMAIL=admin@yourcompany.com
EOF
    
    echo "✅ Создан файл .env с настройками"
    echo "🔐 MySQL пароль пользователя: $MYSQL_PASSWORD"
    echo "🔐 MySQL root пароль: $MYSQL_ROOT_PASSWORD"
    echo "💾 Сохраните эти пароли в безопасном месте!"
else
    echo "ℹ️  Файл .env уже существует, пропускаем создание"
fi

# Обновляем requirements.txt если нужно
echo "📋 Проверяем зависимости..."
if ! grep -q "mysqlclient" requirement.txt; then
    echo "mysqlclient>=2.1.0" >> requirement.txt
    echo "python-dotenv>=1.0.0" >> requirement.txt
    echo "gunicorn>=21.0.0" >> requirement.txt
    echo "✅ Добавлены зависимости для MySQL"
fi

echo "🏗️  Собираем и запускаем контейнеры..."
docker-compose up -d --build

echo "⏳ Ждем запуска всех сервисов..."
sleep 30

echo "🔍 Проверяем статус контейнеров..."
docker-compose ps

echo "📊 Просматриваем логи Django..."
docker-compose logs --tail=20 web

echo ""
echo "✅ Развертывание SKUDWEB завершено!"
echo "🌐 Веб-интерфейс СКУД: http://$(curl -s ifconfig.me 2>/dev/null || echo 'localhost')"
echo "🗄️  phpMyAdmin: http://$(curl -s ifconfig.me 2>/dev/null || echo 'localhost'):8080"
echo "📊 MySQL порт: 3306"
echo ""
echo "🔧 Команды управления:"
echo "   - Создать суперпользователя: docker-compose exec web python manage.py createsuperuser"
echo "   - Просмотр логов: docker-compose logs -f web"
echo "   - Перезапуск: docker-compose restart"
echo "   - Остановка: docker-compose down"
echo ""
echo "📁 Проект находится в директории: $(pwd)"
echo "🔐 Данные для входа в MySQL сохранены в файле .env"