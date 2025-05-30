# Используем официальный Python образ
FROM python:3.11-slim

# Устанавливаем системные зависимости
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        postgresql-client \
        build-essential \
        libpq-dev \
        git \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем весь проект (включая venv если нужно)
COPY . .

# Если в проекте есть requirements.txt, используем его
# Если нет - извлекаем зависимости из venv
RUN if [ -f "requirements.txt" ]; then \
        pip install --no-cache-dir -r requirements.txt; \
    elif [ -d "venv" ]; then \
        pip install --no-cache-dir -r venv/pyvenv.cfg || \
        find venv/lib/python*/site-packages -name "*.dist-info" -exec basename {} .dist-info \; | sort -u > temp_requirements.txt && \
        pip install --no-cache-dir -r temp_requirements.txt; \
    else \
        echo "No requirements.txt or venv found"; \
    fi

# Если нет requirements.txt, создаем его из текущего окружения
RUN if [ ! -f "requirements.txt" ]; then \
        pip freeze > requirements.txt; \
    fi

# Создаем пользователя для запуска приложения
RUN adduser --disabled-password --gecos '' appuser && chown -R appuser /app
USER appuser

# Открываем порт
EXPOSE 8000

# Команда по умолчанию
CMD ["sh", "-c", "python manage.py migrate && python manage.py collectstatic --noinput && gunicorn --bind 0.0.0.0:8000 $(find . -name 'wsgi.py' -exec dirname {} \\; | head -1 | xargs basename).wsgi:application"]