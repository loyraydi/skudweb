from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter(name='add_class')
def add_class(field, css_class):
    """Добавляет CSS-класс к виджету поля формы."""
    if hasattr(field, 'field') and field.field.widget.attrs:
        field.field.widget.attrs['class'] = field.field.widget.attrs.get('class', '') + ' ' + css_class
    elif hasattr(field, 'field'):
        field.field.widget.attrs['class'] = css_class
    return field
