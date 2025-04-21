# SKUDWEB

## Описание проекта

SKUDWEB - это веб-приложение для администрирования СКУДа и настраиваемых релле. Проект разработан для решения [основная проблема или цель проекта].

## Функциональные возможности

- [Основная функция 1]
- [Основная функция 2]
- [Основная функция 3]
- [Другие ключевые возможности]

## Технологии

Проект разработан с использованием следующих технологий:

- Django
- PostgreSQL


## Установка и запуск

### Предварительные требования

- Django (5.1.2)
- Python 3.12
- PostgreSQL

### Шаги по установке

1. Клонируйте репозиторий:
   ```
   git clone https://github.com/loyraydi/skudweb.git
   ```

2. Установите зависимости:
   ```
   py intall -r requirement.txt
   ```

3. Настройте переменные окружения:
    - Откройте файл `skudweb/myproject/settings.py` в директории проекта
    - Добавьте необходимые переменные окружения:
      ```
      DATABASES = {
          "default": {
              'ENGINE': 'django.db.backends.mysql',
              'NAME': 'myapp',
              'USER': 'root',
              'PASSWORD': '',
              'HOST': '127.0.0.1',
              'ssl': {'ca': None},
              'OPTIONS': {'ssl_mode': 'DISABLED'},
      ```

4. Запустите проект:
   ```
   py manage.py runserver 127.0.0.1:8000
   ```

## Использование

[Инструкции по использованию проекта с примерами]

## Структура проекта

```
skudweb/
├── myproject/          # Статические файлы
├── myapp/              # Исходный код
│   ├── static/         # CSS/SCSS/JS/IMG файлы
│   ├── templates/      # Страницы приложения
│   ├── templatetags/   # Кастомные фильтры
│   ├── filters.py      # Фильтры от Django
│   ├── forms.py        # Формы
│   ├── models.py       # Модели БД
│   ├── urls.py         # URL - страниц
│   ├── views.py        # Представления моделей
├── manage.py           # Испольняемый файл проекта
├── requirement.txt     # Библеотеки .venv
└── README.md           # Документация проекта
```




## Контакты

aohameow - @aohameow

Ссылка на проект: [https://github.com/loyraydi/skudweb](https://github.com/loyraydi/skudweb)


