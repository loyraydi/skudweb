from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from .views import (
    create_superuser_ajax, custom_login, get_superusers, log_list_ajax, edit_access,
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
    path('users/delete/<int:pk>/', views.user_delete, name='user_delete'),

    # Аутентификация
    path('login/', custom_login, name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),

    # Админка
    path('create-superuser/', create_superuser_ajax, name='create_superuser_ajax'),
    path('get-superusers/', get_superusers, name='get_superusers'),

    # Логи
    path('logs/ajax/', log_list_ajax, name='log_list_ajax'),

    # Доступ к автомобилям
    path('user/<int:user_id>/edit_access/', edit_access, name='edit_access'),

    # 📌 Устройства (Devices)
    path('devices/', device_list, name='device_list'),  # Страница списка устройств
    path('devices/add/', device_add, name='device_add'),  # Страница добавления устройства
    path('devices/edit/<int:pk>', device_edit, name='device_edit'),  # Страница добавления устройства
    path('devices/delete/<int:pk>/', DeviceDeleteView, name='device_delete'),  # Страница удаления устройства
]
