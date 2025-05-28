from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import redirect
from django.contrib import messages
from django.urls import reverse
from functools import wraps
from django.http import JsonResponse

def group_required(*group_names):
    """Декоратор, который проверяет, принадлежит ли пользователь к одной из указанных групп"""
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if request.user.is_authenticated:
                if request.user.is_superuser or any(request.user.groups.filter(name=group_name).exists() for group_name in group_names):
                    return view_func(request, *args, **kwargs)
            messages.error(request, "У вас нет прав для выполнения этого действия")
            return redirect('dashboard')
        return _wrapped_view
    return decorator

def admin_or_manager_required(view_func):
    """Декоратор, который проверяет, является ли пользователь администратором или менеджером"""
    decorated_view_func = group_required('Администраторы', 'Менеджеры')(view_func)
    return decorated_view_func

def admin_required(view_func):
    """Декоратор, который проверяет, является ли пользователь администратором"""
    decorated_view_func = group_required('Администраторы')(view_func)
    return decorated_view_func

def redirect_if_not_permitted(permission_check):
    """
    Декоратор, который перенаправляет пользователя на страницу списка,
    если у него нет необходимых прав, и показывает сообщение об ошибке.
    Для AJAX-запросов возвращает JSON-ответ с ошибкой вместо редиректа.
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if permission_check(request.user):
                return view_func(request, *args, **kwargs)
            else:
                # Проверяем, является ли запрос AJAX
                is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest' or \
                          request.content_type == 'application/json' or \
                          request.GET.get('format') == 'json' or \
                          request.path.startswith('/api/')

                if is_ajax:
                    # Для AJAX-запросов возвращаем JSON с ошибкой
                    return JsonResponse({
                        'success': False,
                        'error': 'access_denied',
                        'message': "У вас нет прав для выполнения этого действия"
                    }, status=403)
                else:
                    # Для обычных запросов делаем редирект
                    messages.error(request, "У вас нет прав для выполнения этого действия")
                    return redirect('dashboard')
        return _wrapped_view
    return decorator
