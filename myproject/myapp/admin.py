from django.contrib import admin
from django.contrib.auth.models import User, Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.utils.html import format_html
from django.urls import reverse
from django import forms
from django_json_widget.widgets import JSONEditorWidget

from .models import СustomUser, Car_access, Logg, Logg_parking, Logg_access, Device

# Создаем группы пользователей и разрешения
def create_user_groups():
    # Группа администраторов (полный доступ)
    admin_group, _ = Group.objects.get_or_create(name='Администраторы')

    # Группа менеджеров (может просматривать и редактировать, но не удалять)
    manager_group, _ = Group.objects.get_or_create(name='Менеджеры')

    # Группа операторов (только просмотр)
    operator_group, _ = Group.objects.get_or_create(name='Операторы')

    # Получаем все модели из нашего приложения
    models = [СustomUser, Car_access, Logg, Logg_parking, Logg_access, Device]

    # Очищаем существующие разрешения для групп
    admin_group.permissions.clear()
    manager_group.permissions.clear()
    operator_group.permissions.clear()

    # Добавляем разрешения для каждой модели
    for model in models:
        content_type = ContentType.objects.get_for_model(model)
        model_name = model.__name__.lower()

        # Получаем все разрешения для модели
        view_perm = Permission.objects.get(content_type=content_type, codename=f'view_{model_name}')
        add_perm = Permission.objects.get(content_type=content_type, codename=f'add_{model_name}')
        change_perm = Permission.objects.get(content_type=content_type, codename=f'change_{model_name}')
        delete_perm = Permission.objects.get(content_type=content_type, codename=f'delete_{model_name}')

        # Администраторы получают все разрешения
        admin_group.permissions.add(view_perm, add_perm, change_perm, delete_perm)

        # Менеджеры могут просматривать, добавлять и редактировать, но не удалять
        manager_group.permissions.add(view_perm, add_perm, change_perm)

        # Операторы могут только просматривать
        operator_group.permissions.add(view_perm)

# Вызываем функцию создания групп при загрузке admin.py
# Закомментируйте эту строку после первого запуска, чтобы избежать повторного создания групп
#create_user_groups()

# Форма для CustomUser с виджетом JSON для поля user_acesses
class CustomUserForm(forms.ModelForm):
    class Meta:
        model = СustomUser
        fields = '__all__'
        widgets = {
            'user_acesses': JSONEditorWidget(),
        }

# Админка для CustomUser
class CustomUserAdmin(admin.ModelAdmin):
    form = CustomUserForm
    list_display = ['id_user', 'user_name', 'departments', 'occupations', 'access_level', 'reg_status', 'email', 'telegram']
    list_filter = ['departments', 'access_level', 'reg']
    search_fields = ['user_name', 'email', 'phone_number', 'uid_card']
    readonly_fields = ['id_user']
    fieldsets = [
        ('Основная информация', {
            'fields': ['user_name', 'departments', 'occupations', 'access_level']
        }),
        ('Контактная информация', {
            'fields': ['phone_number', 'email', 'telegram']
        }),
        ('Системная информация', {
            'fields': ['uid_card', 'code_activation', 'reg', 'user_acesses'],
            'classes': ['collapse']
        }),
    ]

    def reg_status(self, obj):
        status_map = {
            0: '<span style="color:red;">Не завершил регистрацию</span>',
            1: '<span style="color:green;">Зарегистрирован</span>',
            2: '<span style="color:orange;">Ожидает активации</span>',
        }
        return format_html(status_map.get(obj.reg, ''))
    reg_status.short_description = 'Статус регистрации'

    # Ограничение прав
    def has_add_permission(self, request):
        # Только администраторы и менеджеры могут добавлять
        return request.user.has_perm('myapp.add_сustomuser')

    def has_change_permission(self, request, obj=None):
        # Только администраторы и менеджеры могут изменять
        return request.user.has_perm('myapp.change_сustomuser')

    def has_delete_permission(self, request, obj=None):
        # Только администраторы могут удалять
        return request.user.has_perm('myapp.delete_сustomuser')

    def has_view_permission(self, request, obj=None):
        # Все группы могут просматривать
        return request.user.has_perm('myapp.view_сustomuser')

    # Ограничение полей для разных групп пользователей
    def get_fieldsets(self, request, obj=None):
        fieldsets = super().get_fieldsets(request, obj)

        # Если пользователь не администратор, скрываем системную информацию
        if not request.user.groups.filter(name='Администраторы').exists():
            return [fs for fs in fieldsets if fs[0] != 'Системная информация']

        return fieldsets

    # Ограничение действий для разных групп
    def get_actions(self, request):
        actions = super().get_actions(request)

        # Если пользователь не администратор, убираем действие удаления
        if not request.user.groups.filter(name='Администраторы').exists():
            if 'delete_selected' in actions:
                del actions['delete_selected']

        return actions

# Админка для Car_access
class CarAccessAdmin(admin.ModelAdmin):
    list_display = ['id_user', 'car_plate_number', 'brand_model', 'color', 'time_access']
    search_fields = ['car_plate_number', 'brand_model']
    list_filter = ['time_access']

    # Ограничение прав
    def has_add_permission(self, request):
        return request.user.has_perm('myapp.add_car_access')

    def has_change_permission(self, request, obj=None):
        return request.user.has_perm('myapp.change_car_access')

    def has_delete_permission(self, request, obj=None):
        return request.user.has_perm('myapp.delete_car_access')

    def has_view_permission(self, request, obj=None):
        return request.user.has_perm('myapp.view_car_access')

# Админка для Logg
class LoggAdmin(admin.ModelAdmin):
    list_display = ['datetime', 'get_message', 'auditory_number']
    search_fields = ['message', 'auditory_number']
    list_filter = ['datetime', 'auditory_number']
    readonly_fields = ['datetime', 'message', 'auditory_number']

    def get_message(self, obj):
        # Ограничиваем длину сообщения для отображения в списке
        if len(obj.message) > 50:
            return f"{obj.message[:50]}..."
        return obj.message
    get_message.short_description = 'Сообщение'

    # Операторы могут только просматривать логи
    def has_add_permission(self, request):
        return request.user.groups.filter(name__in=['Администраторы', 'Менеджеры']).exists()

    def has_change_permission(self, request, obj=None):
        return request.user.groups.filter(name='Администраторы').exists()

    def has_delete_permission(self, request, obj=None):
        return request.user.groups.filter(name='Администраторы').exists()

# Админка для Logg_parking
class LoggParkingAdmin(admin.ModelAdmin):
    list_display = ['datetime', 'id_user', 'get_message']
    search_fields = ['message', 'id_user']
    list_filter = ['datetime', 'id_user']
    readonly_fields = ['datetime', 'id_user', 'message']

    def get_message(self, obj):
        # Ограничиваем длину сообщения для отображения в списке
        if len(obj.message) > 50:
            return f"{obj.message[:50]}..."
        return obj.message
    get_message.short_description = 'Сообщение'

    # Операторы могут только просматривать логи
    def has_add_permission(self, request):
        return request.user.groups.filter(name__in=['Администраторы', 'Менеджеры']).exists()

    def has_change_permission(self, request, obj=None):
        return request.user.groups.filter(name='Администраторы').exists()

    def has_delete_permission(self, request, obj=None):
        return request.user.groups.filter(name='Администраторы').exists()

# Админка для Logg_access
class LoggAccessAdmin(admin.ModelAdmin):
    list_display = ['datetime', 'uid_card', 'action', 'auditory_number']
    search_fields = ['uid_card', 'action', 'auditory_number']
    list_filter = ['datetime', 'action', 'auditory_number']
    readonly_fields = ['datetime', 'uid_card', 'action', 'auditory_number']

    def get_action(self, obj):
        # Ограничиваем длину действия для отображения в списке
        if len(obj.action) > 50:
            return f"{obj.action[:50]}..."
        return obj.action
    get_action.short_description = 'Действие'

    # Операторы могут только просматривать логи
    def has_add_permission(self, request):
        return request.user.groups.filter(name__in=['Администраторы', 'Менеджеры']).exists()

    def has_change_permission(self, request, obj=None):
        return request.user.groups.filter(name='Администраторы').exists()

    def has_delete_permission(self, request, obj=None):
        return request.user.groups.filter(name='Администраторы').exists()

# Форма для Device с виджетом JSON для JSON-полей
class DeviceForm(forms.ModelForm):
    class Meta:
        model = Device
        fields = '__all__'
        widgets = {
            'device_api': JSONEditorWidget(),
            'calendar_regular': JSONEditorWidget(),
            'calendar_exception': JSONEditorWidget(),
        }

# Админка для Device
class DeviceAdmin(admin.ModelAdmin):
    form = DeviceForm
    list_display = ['id_device', 'name', 'ip', 'mac', 'device_status', 'device_activated']
    list_filter = ['device_activated', 'device_status', 'checkable']
    search_fields = ['name', 'ip', 'mac']
    readonly_fields = ['id_device']
    fieldsets = [
        ('Основная информация', {
            'fields': ['id_device', 'name', 'ip', 'mac', 'device_activated', 'device_status']
        }),
        ('Токены и API', {
            'fields': ['token', 'tg_token', 'device_api'],
            'classes': ['collapse']
        }),
        ('Настройки календаря', {
            'fields': ['calendar_regular', 'calendar_exception', 'period'],
            'classes': ['collapse']
        }),
        ('Настройки попыток', {
            'fields': ['trying_open', 'trying_close', 'trying_max', 'trying_delay', 'checkable'],
            'classes': ['collapse']
        }),
    ]

    # Ограничение прав
    def has_add_permission(self, request):
        return request.user.has_perm('myapp.add_device')

    def has_change_permission(self, request, obj=None):
        return request.user.has_perm('myapp.change_device')

    def has_delete_permission(self, request, obj=None):
        return request.user.has_perm('myapp.delete_device')

    def has_view_permission(self, request, obj=None):
        return request.user.has_perm('myapp.view_device')

    # Ограничение полей для разных групп пользователей
    def get_fieldsets(self, request, obj=None):
        fieldsets = super().get_fieldsets(request, obj)

        # Если пользователь не администратор, скрываем некоторые разделы
        if not request.user.groups.filter(name='Администраторы').exists():
            return [fs for fs in fieldsets if fs[0] not in ['Токены и API', 'Настройки попыток']]

        return fieldsets

    # Ограничение действий для разных групп
    def get_actions(self, request):
        actions = super().get_actions(request)

        # Если пользователь не администратор, убираем действие удаления
        if not request.user.groups.filter(name='Администраторы').exists():
            if 'delete_selected' in actions:
                del actions['delete_selected']

        return actions

# Регистрация моделей в админке
admin.site.register(СustomUser, CustomUserAdmin)
admin.site.register(Car_access, CarAccessAdmin)
admin.site.register(Logg, LoggAdmin)
admin.site.register(Logg_parking, LoggParkingAdmin)
admin.site.register(Logg_access, LoggAccessAdmin)
admin.site.register(Device, DeviceAdmin)

# Настройка заголовка и названия админки
admin.site.site_header = 'Панель администрирования системы'
admin.site.site_title = 'Управление системой'
admin.site.index_title = 'Администрирование'