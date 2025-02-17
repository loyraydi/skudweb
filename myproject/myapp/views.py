# myapp/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from .models import СustomUser, Car_access, Logg
from .forms import UserForm, CarsForm, CustomAuthenticationForm, AdminUserCreationForm
from .filters import UserFilter
from django.db.models import Q
from django.contrib import messages
from django.contrib.auth import login, authenticate
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
import json



# Отображение списка пользователей
@login_required
def user_list(request):
    query = request.GET.get('q', '')  # Получение строки поиска
    users = СustomUser.objects.all()

    if query:
        users = users.filter(
            Q(user_name__icontains=query) |
            Q(email__icontains=query) |
            Q(phone_number__icontains=query) |
            Q(access_level__icontains=query) |
            Q(departments__icontains=query) |
            Q(occupations__icontains=query) |
            Q(id_user__icontains=query)  # Добавляем поиск по ID, если нужно
        )

    paginator = Paginator(users, 10)  # Показывать 10 записей на странице
    page_number = request.GET.get('page')  # Номер текущей страницы
    page_obj = paginator.get_page(page_number)

    return render(request, 'myapp/product_list.html', {
        'users': page_obj,
        'query': query,
   })

# Добавление нового пользователя
@login_required
def user_create(request):
    access_level_choices = ['User', 'Admin', 'Kent', 'Alien']
    form = UserForm(request.POST or None)
    if form.is_valid():
        form.access_level = ','.join(form.cleaned_data['access_level'])
        form.save()
        return redirect('user_list')
    return render(request, 'myapp/product_form.html', {'form': form, 'access_level_choices': access_level_choices})

# Редактирование пользователя
@login_required
def user_update(request, pk):
    access_level_choices = ['User', 'Admin', 'Kent', 'Alien']
    user = get_object_or_404(СustomUser, pk=pk)
    form = UserForm(request.POST or None, instance=user)
    devices = user.user_acesses.get('devices', [])
    auditory = user.user_acesses.get('auditory', [])

    # Преобразуем аудиторные данные в строку для поля ввода
    auditory_input_value = ",".join(auditory)

    if form.is_valid():
        form.save()
        return redirect('user_list')

    return render(request, 'myapp/product_form.html', {'form': form, 'access_level_choices': access_level_choices, 'selected_devices': devices,'auditory_input_value': auditory_input_value})


@login_required
def user_about(request, user_id):
    try:
        user = СustomUser.objects.get(id_user=user_id)                 #get_object_or_404(User, id_user=user_id)

        cars = Car_access.objects.filter(id_user=user_id).first()   #get_object_or_404(Car_access, id_user=user_id)
    except СustomUser.DoesNotExist:
        user = None
        cars = None

    return render(request, 'myapp/product_about.html', {'user': user, 'cars': cars})


# Удаление пользователя
@login_required
def user_delete(request, pk):
    user = get_object_or_404(СustomUser, pk=pk)
    if request.method == 'POST':
        user.delete()
        messages.success(request, f"User {user.user_name} has been deleted.")
        return redirect('user_list')
    return render(request, 'myapp/product_confirm_delete.html', {'user': user})


def custom_login(request):
    form = CustomAuthenticationForm(data=request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('user_list')  # Перенаправляем на домашнюю страницу
            else:
                form.add_error(None, 'Неверный логин или пароль.')  # Добавляем сообщение об ошибке

    return render(request, 'custom_login.html', {'form': form})


@login_required
@csrf_exempt
def create_superuser_ajax(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')

        # Проверяем обязательные поля
        if not username or not password or not email:
            return JsonResponse({'success': False, 'message': 'Логин, пароль и email обязательны.'}, status=400)

        # Проверяем уникальность имени пользователя
        if User.objects.filter(username=username).exists():
            return JsonResponse({'success': False, 'message': 'Пользователь с таким логином уже существует.'}, status=400)

        # Создаём суперпользователя
        try:
            user = User.objects.create_superuser(
                username=username,
                email=email,
                password=password
            )
            user.first_name = first_name
            user.last_name = last_name
            user.save()
            return JsonResponse({'success': True, 'message': f'Суперпользователь {username} успешно создан.'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Ошибка: {str(e)}'}, status=500)

    return JsonResponse({'success': False, 'message': 'Недопустимый запрос.'}, status=405)


@login_required
def get_superusers(request):
    superusers = User.objects.filter(is_superuser=True).values('username', 'email')
    return JsonResponse({'superusers': list(superusers)})


@login_required
def log_list_ajax(request):
    search_query = request.GET.get('search', '')
    sort_by = request.GET.get('sort', 'datetime')

    logs = Logg.objects.all()

    if search_query:
        logs = logs.filter(
            Q(message__icontains=search_query) | Q(level__icontains=search_query)
        )

    logs = logs.order_by(sort_by)

    return render(request, 'partials/log_list_table.html', {'logs': logs})


@login_required
def save_user(request):
    if request.method == "POST":
        form = UserForm(request.POST)

        if form.is_valid():
            user = form.save(commit=False)
            user_acesses = request.POST.get('user_acesses')

            # Преобразуем строку JSON обратно в объект
            if user_acesses:
                user_acesses_data = json.loads(user_acesses)
                user.user_acesses = user_acesses_data
            else:
                user.user_acesses = {}

            user.save()
            return redirect('product_list')  # Перенаправляем на страницу списка пользователей

    return render(request, 'myapp/product_form.html', {'form': form})


@login_required
def edit_access(request, user_id):
    user = get_object_or_404(СustomUser, id_user=user_id)
    car_access = Car_access.objects.filter(id_user=user_id).first()

    # Если данные уже сохранены, разбиваем их на отдельные части (дни и время)
    if car_access:
        selected_days = car_access.time_access.split(';')[0].split(',')
        start_time, end_time = car_access.time_access.split(';')[1].split(',')
    else:
        selected_days = []
        start_time = ''
        end_time = ''

    if request.method == "POST":
        selected_days = request.POST.getlist("days")
        start_time = request.POST.get("start_time")
        end_time = request.POST.get("end_time")

        if selected_days and start_time and end_time:
            formatted_access = f"{','.join(selected_days)};{start_time},{end_time}"
            if car_access:
                car_access.time_access = formatted_access
                car_access.save()
            else:
                Car_access.objects.create(user=user, time_access=formatted_access)

            return redirect('user_about', user_id=user_id)

    return render(request, "myapp/edit_access.html", {
        "user": user,
        "car_access": car_access,
        "selected_days": selected_days,
        "start_time": start_time,
        "end_time": end_time
    })
