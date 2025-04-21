# myapp/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from .models import СustomUser, Car_access, Logg, Device
from .forms import UserForm, CarsForm, CustomAuthenticationForm, AdminUserCreationForm, DeviceForm
from .filters import UserFilter
from django.db.models import Q
from django.contrib import messages
from django.contrib.auth import login, authenticate
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
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
    devices = (user.user_acesses or {}).get('devices', [])
    auditory = (user.user_acesses or {}).get('auditory', [])

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
                return redirect('dashboard')  # Перенаправляем на домашнюю страницу
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
def list_superusers(request):
    users = User.objects.filter(is_superuser=True)
    return JsonResponse({
        'success': True,
        'superusers': [
            {
                'id': u.id,
                'username': u.username,
                'email': u.email,
                'first_name': u.first_name,
                'last_name': u.last_name,
            }
            for u in users
        ]
    })

@login_required
def get_superuser(request, user_id):
    try:
        user = User.objects.get(id=user_id, is_superuser=True)
        return JsonResponse({
            'success': True,
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name
            }
        })
    except User.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Пользователь не найден'}, status=404)

@login_required
def delete_superuser(request, user_id):
    if request.method == 'DELETE':
        # Находим суперпользователя по user_id
        user = get_object_or_404(User, id=user_id)

        # Удаляем пользователя
        try:
            user.delete()
            return JsonResponse({'success': True, 'message': 'Суперпользователь удален.'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Ошибка: {str(e)}'}, status=500)

    return JsonResponse({'success': False, 'message': 'Неверный метод запроса.'}, status=405)

@login_required
def admin_users_page(request):
    return render(request, 'myapp/admin_users.html')

@login_required
def reset_password(request, user_id):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            new_password = data.get('password')

            if not new_password:
                return JsonResponse({'success': False, 'message': 'Пароль обязателен'}, status=400)

            user = User.objects.get(id=user_id, is_superuser=True)
            user.set_password(new_password)
            user.save()

            return JsonResponse({'success': True})
        except User.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Пользователь не найден'}, status=404)
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'message': 'Некорректный формат данных'}, status=400)

    return JsonResponse({'success': False, 'message': 'Метод не поддерживается'}, status=405)

@login_required
def edit_superuser(request, user_id):
    if request.method == 'POST':
        try:
            user = User.objects.get(id=user_id, is_superuser=True)
            user.username = request.POST.get('username')
            user.email = request.POST.get('email')
            user.first_name = request.POST.get('first_name')
            user.last_name = request.POST.get('last_name')

            # Пароль не меняем, если не введён
            password = request.POST.get('password')
            if password:
                user.set_password(password)

            user.save()

            return JsonResponse({'success': True})
        except User.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Суперпользователь не найден'}, status=404)
    return JsonResponse({'success': False, 'message': 'Метод не поддерживается'}, status=405)

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


"""@login_required
def device_form(request, device_id=None):
    device = get_object_or_404(Device, pk=device_id) if device_id else None

    if request.method == "POST":
        form = DeviceForm(request.POST, instance=device)
        if form.is_valid():
            form.save()
            return redirect("device_list")
    else:
        form = DeviceForm(instance=device)

    return render(request, "devices/device_form.html", {"form": form, "device": device})"""
# Отображение списка девайсов
@login_required
def device_list(request):
    query = request.GET.get('q', '')  # Получение строки поиска
    device = Device.objects.all()

    if query:
        device = device.filter(
            Q(ip__icontains=query) |
            Q(mac__icontains=query) |
            Q(name__icontains=query) |
            Q(device_status__icontains=query) |
            Q(id_device__icontains=query)  # Добавляем поиск по ID, если нужно
        )

    paginator = Paginator(device, 10)  # Показывать 10 записей на странице
    page_number = request.GET.get('page')  # Номер текущей страницы
    page_obj = paginator.get_page(page_number)

    return render(request, 'devices/device_list.html', {
        'device': page_obj,
        'query': query,
    })

# Добавление нового пользователя
def device_add(request):
    if request.method == 'POST':
        post_data = request.POST.copy()

        # Проверка включения календаря
        if 'calendar_toggle' in post_data:
            # Собираем calendar_regular в JSON
            calendar_regular = {
                "check_period": "2",
                "open_day": [day.strip() for day in (post_data.get('open_day') or '').split(',') if day.strip()],
                "open_time": post_data.get('open_time', ''),
                "close_day": [day.strip() for day in (post_data.get('close_day') or '').split(',') if day.strip()],
                "close_time": post_data.get('close_time', '')
            }
            post_data['calendar_regular'] = json.dumps(calendar_regular)

            # calendar_exception
            calendar_exception = {
                "open_day": [day.strip() for day in (post_data.get('exception_open_day') or '').split(',') if day.strip()],
                "close_day": [day.strip() for day in (post_data.get('exception_close_day') or '').split(',') if day.strip()],
            }
            post_data['calendar_exception'] = json.dumps(calendar_exception)
        else:
            post_data['calendar_regular'] = 'null'
            post_data['calendar_exception'] = 'null'

        # Обработка активности
        post_data['device_activated'] = 'device_activated' in post_data

        # 💡 Добавим шаблон device_api, если поле пустое
        device_api_input = post_data.get('device_api', '').strip()
        if not device_api_input:
            default_api = {
                "open": [""],
                "checkabe": "",
                "commands": [""]
            }
            post_data['device_api'] = json.dumps(default_api)
        else:
            try:
                # Проверка, валиден ли JSON
                json.loads(device_api_input)
            except json.JSONDecodeError:
                form = DeviceForm(post_data)
                form.add_error('device_api', "Невалидный JSON в API")
                return render(request, 'devices/device_form.html', {'form': form})

        form = DeviceForm(post_data)
        if form.is_valid():
            form.save()
            return redirect('device_list')
        else:
            print("Ошибки формы:", form.errors)

    else:
        form = DeviceForm()

    return render(request, 'devices/device_form.html', {'form': form})


def device_edit(request, pk):
    device = get_object_or_404(Device, pk=pk)

    if request.method == 'POST':
        post_data = request.POST.copy()

        # Проверка включения календаря
        if 'calendar_toggle' in post_data:
            # Собираем calendar_regular в JSON
            calendar_regular = {
                "check_period": "2",
                "open_day": [day.strip() for day in (post_data.get('open_day') or '').split(',') if day.strip()],
                "open_time": post_data.get('open_time', ''),
                "close_day": [day.strip() for day in (post_data.get('close_day') or '').split(',') if day.strip()],
                "close_time": post_data.get('close_time', '')
            }
            post_data['calendar_regular'] = json.dumps(calendar_regular)

            # Собираем calendar_exception в JSON
            calendar_exception = {
                "open_day": [day.strip() for day in (post_data.get('exception_open_day') or '').split(',') if day.strip()],
                "close_day": [day.strip() for day in (post_data.get('exception_close_day') or '').split(',') if day.strip()],
            }
            post_data['calendar_exception'] = json.dumps(calendar_exception)
        else:
            post_data['calendar_regular'] = 'null'
            post_data['calendar_exception'] = 'null'

        # Обработка флага активности
        post_data['device_activated'] = 'device_activated' in post_data

        # Проверка валидности JSON для device_api
        device_api_input = post_data.get('device_api', '').strip()
        if device_api_input:
            try:
                json.loads(device_api_input)
            except json.JSONDecodeError:
                form = DeviceForm(post_data, instance=device)
                form.add_error('device_api', "Невалидный JSON в API")
                return render(request, 'devices/device_form.html', {'form': form, 'device': device})

        form = DeviceForm(post_data, instance=device)
        if form.is_valid():
            form.save()
            return redirect('device_list')
        else:
            print("Ошибки формы:", form.errors)

    else:
        # Предзаполнение полей из JSON при GET-запросе
        try:
            calendar_regular = json.loads(device.calendar_regular) if device.calendar_regular and device.calendar_regular != 'null' else {}
            calendar_exception = json.loads(device.calendar_exception) if device.calendar_exception and device.calendar_exception != 'null' else {}
        except json.JSONDecodeError:
            calendar_regular = {}
            calendar_exception = {}

        device.open_day = ', '.join(calendar_regular.get('open_day', []))
        device.open_time = calendar_regular.get('open_time', '')
        device.close_day = ', '.join(calendar_regular.get('close_day', []))
        device.close_time = calendar_regular.get('close_time', '')
        device.exception_open_day = ', '.join(calendar_exception.get('open_day', []))
        device.exception_close_day = ', '.join(calendar_exception.get('close_day', []))

        form = DeviceForm(instance=device)

    return render(request, 'devices/device_form.html', {'form': form, 'device': device})

@login_required
def DeviceDeleteView(request, pk):
    device = get_object_or_404(Device, pk=pk)
    if request.method == 'POST':
        device.delete()
        messages.success(request, f"User {device.name} has been deleted.")
        return redirect('device_list')
    return render(request, 'devices/device_confirm_delete.html', {'device': device})


@login_required
def dashboard(request):
    return render(request, "myapp/dashboard.html")


@login_required
def get_dashboard_data(request):
    """API для получения последних логов и последнего пользователя."""

    # Получаем последние 5 логов
    latest_logs = Logg.objects.order_by("-datetime")[:5]
    logs_data = [
        {"datetime": log.datetime, "message": log.message, "auditory": log.auditory_number}
        for log in latest_logs
    ]

    # Получаем последнего пользователя
    last_user = СustomUser.objects.order_by("-id_user").first()
    last_user_data = {
        "user_name": last_user.user_name if last_user else "Нет пользователей",
        "occupations": last_user.occupations if last_user else "",
        "id_user": last_user.id_user if last_user else None,
    }
    last_device = Device.objects.order_by("-id_device").first()
    last_device_data = {
        "device_name": last_device.name if last_device else "Нет Devices",
        "activated": last_device.device_activated if last_device else "",
        "id_device": last_device.id_device if last_device else None,
    }
    return JsonResponse({"logs": logs_data, "last_user": last_user_data, "last_device": last_device_data})