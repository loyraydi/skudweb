#!/bin/bash

# Скрипт для развертывания Django приложения на Ubuntu 22.04

echo "🚀 Начинаем развертывание Django приложения..."

# Обновляем систему
echo "📦 Обновляем систему..."
sudo apt update && sudo apt upgrade -y

# Устанавливаем Docker
echo "🐳 Устанавливаем Docker..."
sudo apt install -y apt-transport-https ca-certificates curl software-properties-common
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io

# Устанавливаем Docker Compose
echo "🔧 Устанавливаем Docker Compose..."
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Добавляем пользователя в группу docker
echo "👤 Настраиваем права пользователя..."
sudo usermod -aG docker $USER

# Создаем директорию для проекта
echo "📁 Создаем директорию проекта..."
mkdir -p ~/django-app
cd ~/django-app

# Создаем .env файл
echo "⚙️ Создаем файл окружения..."
cat > .env << EOF
SECRET_KEY=$(python3 -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')
DEBUG=False
DATABASE_URL=postgresql://django_user:django_password@db:5432/django_db
ALLOWED_HOSTS=localhost,127.0.0.1