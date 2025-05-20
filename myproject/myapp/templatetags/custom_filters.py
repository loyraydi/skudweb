from django import template
from django.utils.safestring import mark_safe
from datetime import datetime
import hashlib

register = template.Library()

@register.filter(name='add_class')
def add_class(field, css_class):
    """Добавляет CSS-класс к виджету поля формы."""
    if hasattr(field, 'field') and field.field.widget.attrs:
        field.field.widget.attrs['class'] = field.field.widget.attrs.get('class', '') + ' ' + css_class
    elif hasattr(field, 'field'):
        field.field.widget.attrs['class'] = css_class
    return field


@register.filter
def format_datetime(value):
    try:
        dt_object = datetime.strptime(value, "%Y-%m-%d %H:%M:%S.%f")
        return dt_object.strftime("%d %B %Y %H:%M")
    except ValueError:
        return value  # Если формат неправильный, просто выводим как есть

@register.filter
def stringToColor(value):
    """
    Генерирует цвет на основе строки (имени пользователя)
    """
    if not value:
        return "#6c757d"  # Цвет по умолчанию для пустых значений

    # Создаем хеш из строки
    hash_object = hashlib.md5(str(value).encode())
    hash_hex = hash_object.hexdigest()

    # Используем первые 6 символов хеша как HEX-цвет
    color = "#" + hash_hex[:6]

    return color