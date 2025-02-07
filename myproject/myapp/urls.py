# myapp/urls.py
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from .forms import CustomAuthenticationForm
from .views import create_superuser_ajax
from .views import custom_login, get_superusers, log_list_ajax, edit_access

urlpatterns = [
    path('', views.user_list, name='user_list'),
    path('create/', views.user_create, name='user_create'),
    path('update/<int:pk>/', views.user_update, name='user_update'),
    path('users/<int:user_id>/', views.user_about, name='user_about'),  # Страница для одного пользователя
    path('users/delete/<int:pk>/', views.user_delete, name='user_delete'),
    # Страница входа
    path('login/', custom_login, name='login'),
    # Страница выхода
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('create-superuser/', create_superuser_ajax, name='create_superuser_ajax'),
    path('get-superusers/', get_superusers, name='get_superusers'),
    path('logs/ajax/', log_list_ajax, name='log_list_ajax'),
    path('user/<int:user_id>/edit_access/', edit_access, name='edit_access'),

]
