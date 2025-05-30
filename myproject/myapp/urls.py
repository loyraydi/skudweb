from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from .views import (
    create_superuser_ajax, custom_login, get_superuser, edit_access,
    device_list,DeviceDeleteView,device_add,
    dashboard, get_dashboard_data, device_edit
)

urlpatterns = [
    path('', dashboard, name='dashboard'),  # Главная страница
    path('get-logs/', get_dashboard_data, name='get_logs'),  # API для логов
    path("dashboard-data/", get_dashboard_data, name="get_dashboard_data"),
    path('users_list', views.user_list, name='user_list'),
    path('create/', views.user_create, name='user_create'),
    path('update/<int:pk>/', views.user_update, name='user_update'),
    path('users/<int:user_id>/', views.user_about, name='user_about'),
    path('users/<int:user_id>/update-field/', views.update_user_field, name='update_user_field'),
    path('users/delete/<int:pk>/', views.user_delete, name='user_delete'),

    # Аутентификация
    path('login/', custom_login, name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),

    # Админка
    path('admin-users/', views.admin_users_page, name='admin_users_page'),
    path('admin-users/create/', views.create_superuser_ajax, name='create_superuser_ajax'),
    path('admin-users/list/', views.list_superusers, name='get_superusers'),  # <== Обновлено!
    path('delete_superuser/<int:user_id>/', views.delete_superuser, name='delete_superuser'),
    path('get_superuser/<int:user_id>/', views.get_superuser, name='get_superuser'),
    path('reset_password/<int:user_id>/', views.reset_password, name='reset_password'),
    path('edit_superuser/<int:user_id>/', views.edit_superuser, name='edit_superuser'),

    # Логи
    path('logs/', views.logs_page, name='logs_page'),
    path('logs/api/system/', views.system_logs_api, name='system_logs_api'),
    path('logs/api/user/', views.user_logs_api, name='user_logs_api'),
    path('logs/api/device/', views.device_logs_api, name='device_logs_api'),
    path('logs/api/detail/', views.log_detail_api, name='log_detail_api'),
    path('logs/api/delete/', views.delete_log_api, name='delete_log_api'),

    # Доступ к автомобилям
    path('user/<int:user_id>/edit_access/', edit_access, name='edit_access'),

    # 📌 Устройства (Devices)
    path('devices/', device_list, name='device_list'),  # Страница списка устройств
    path('devices/add/', device_add, name='device_add'),  # Страница добавления устройства
    path('devices/edit/<int:pk>', device_edit, name='device_edit'),  # Страница добавления устройства
    path('devices/delete/<int:pk>/', DeviceDeleteView, name='device_delete'),  # Страница удаления устройства
    path('device/<int:pk>/', views.device_detail, name='device_detail'),
    path('device/<int:device_id>/update-field/', views.update_device_field, name='update_device_field'),
]
