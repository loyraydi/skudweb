FROM python:3.11-slim

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    curl \
    gettext \
    && rm -rf /var/lib/apt/lists/*

# Создание пользователя для безопасности
RUN useradd --create-home --shell /bin/bash app

# Установка рабочей директории
WORKDIR /app

# Копирование и установка зависимостей
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Копирование проекта
COPY . .

# Создание необходимых директорий
RUN mkdir -p /app/staticfiles /app/media /app/logs

# Установка прав доступа
RUN chown -R app:app /app
USER app

# Сбор статических файлов
RUN python manage.py collectstatic --noinput --settings=myproject.settings_production

# Открытие порта
EXPOSE 8000

# Команда запуска
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "3", "--timeout", "120", "myproject.wsgi:application"]