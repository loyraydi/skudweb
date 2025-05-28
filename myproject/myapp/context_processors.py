def user_permissions(request):
    """
    Добавляет информацию о правах пользователя в контекст шаблона
    """
    context = {}

    if request.user.is_authenticated:
        # Проверяем, является ли пользователь администратором или менеджером
        is_admin = request.user.groups.filter(name='Администраторы').exists() or request.user.is_superuser
        is_manager = request.user.groups.filter(name='Менеджеры').exists()

        context['is_admin'] = is_admin
        context['is_manager'] = is_manager
        context['is_operator'] = not (is_admin or is_manager)
    else:
        context['is_admin'] = False
        context['is_manager'] = False
        context['is_operator'] = False

    return context  # Обязательно возвращаем словарь!