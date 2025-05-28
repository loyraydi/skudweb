from django.shortcuts import redirect
from django.contrib import messages
from django.http import JsonResponse
import re

class PermissionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # URL-паттерны, требующие прав администратора или менеджера
        self.admin_manager_patterns = [
            r'^/users/create/',
            r'^/users/\d+/update/',
            r'^/devices/add/',
            r'^/devices/edit/\d+',
        ]
        # URL-паттерны, требующие прав администратора
        self.admin_patterns = [
            r'^/users/delete/\d+/',
            r'^/devices/delete/\d+/',
        ]

    def __call__(self, request):
        # Проверяем только авторизованных пользователей
        if request.user.is_authenticated:
            path = request.path_info

            # Проверка URL для администраторов и менеджеров
            if any(re.match(pattern, path) for pattern in self.admin_manager_patterns):
                if not (request.user.is_superuser or
                        request.user.groups.filter(name__in=['Администраторы', 'Менеджеры']).exists()):

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
                            'message': "У вас нет прав для доступа к этой странице"
                        }, status=403)
                    else:
                        # Для обычных запросов делаем редирект
                        messages.error(request, "У вас нет прав для доступа к этой странице")
                        return redirect('user_list')

            # Проверка URL только для администраторов
            if any(re.match(pattern, path) for pattern in self.admin_patterns):
                if not (request.user.is_superuser or
                        request.user.groups.filter(name='Администраторы').exists()):

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
                            'message': "У вас нет прав для доступа к этой странице"
                        }, status=403)
                    else:
                        # Для обычных запросов делаем редирект
                        messages.error(request, "У вас нет прав для доступа к этой странице")
                        return redirect('user_list')

        response = self.get_response(request)
        return response
