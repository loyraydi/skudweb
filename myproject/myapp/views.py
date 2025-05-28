# myapp/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from .models import СustomUser, Car_access, Logg, Device, Logg_parking, Logg_access, Auditory
from .forms import UserForm, CarsForm, CustomAuthenticationForm, AdminUserCreationForm, DeviceForm
from .filters import UserFilter
from django.db.models import Q
from django.contrib import messages
from django.contrib.auth import login, authenticate
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User, Group
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
import json
from django.views.decorators.http import require_http_methods
from .decorators import admin_or_manager_required, admin_required, redirect_if_not_permitted
from django.contrib.auth.models import Group



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
@admin_or_manager_required
def user_create(request):
    access_level_choices = ['User', 'Admin', 'Kent', 'Alien']
    form = UserForm(request.POST or None)

    # Получаем только устройства со статусом "normal"
    devices_list = Device.objects.all()

    if form.is_valid():
        form.access_level = ','.join(form.cleaned_data['access_level'])
        form.save()
        return redirect('user_list')

    return render(request, 'myapp/product_form.html', {
        'form': form,
        'access_level_choices': access_level_choices,
        'devices_list': devices_list,
        'selected_devices': []
    })

@login_required
@redirect_if_not_permitted(lambda user: user.groups.filter(name__in=['Администраторы', 'Менеджеры']).exists())
def user_update(request, pk):
    access_level_choices = ['User', 'Admin', 'Kent', 'Alien']
    user = get_object_or_404(СustomUser, pk=pk)
    form = UserForm(request.POST or None, instance=user)

    # Получаем выбранные устройства пользователя
    selected_devices = (user.user_acesses or {}).get('devices', [])
    auditory = (user.user_acesses or {}).get('auditory', [])

    # Получаем все устройства, но помечаем, какие из них выбраны у пользователя
    devices_list = list(Device.objects.all().values('id_device', 'name', 'device_status').distinct())

    # Добавляем флаг is_selected для каждого устройства
    for device in devices_list:
        device_id_with_hash = f"#{device['id_device']}"
        device['is_selected'] = device_id_with_hash in selected_devices

    # Преобразуем аудиторные данные в строку для поля ввода
    auditory_input_value = ",".join(auditory)

    if request.method == 'POST':
        if form.is_valid():
            # Обработка POST запроса и сохранение данных
            user_acesses_json = request.POST.get('user_acesses')
            if user_acesses_json:
                try:
                    user_acesses = json.loads(user_acesses_json)
                    user.user_acesses = user_acesses
                except json.JSONDecodeError:
                    pass

            form.save()
            return redirect('user_about', user_id=pk)

    return render(request, 'myapp/product_form.html', {
        'form': form,
        'access_level_choices': access_level_choices,
        'devices_list': devices_list,
        'selected_devices': selected_devices,
        'auditory_input_value': auditory_input_value
    })

@login_required(login_url='login')
def user_about(request, user_id):
    # Проверка, авторизован ли пользователь
    if not request.user.is_authenticated:
        return redirect('login')

    try:
        user = СustomUser.objects.get(id_user=user_id)
        cars = Car_access.objects.filter(id_user=user_id).first()

        # Получаем списки выборов для полей формы
        access_level_choices = СustomUser._meta.get_field('access_level').choices
        reg_choices = СustomUser._meta.get_field('reg').choices

    except СustomUser.DoesNotExist:
        user = None
        cars = None
        access_level_choices = []
        reg_choices = []

    return render(request, 'myapp/product_about.html', {  # Убедитесь, что путь к шаблону правильный
        'user': user,
        'cars': cars,
        'access_level_choices': access_level_choices,
        'reg_choices': reg_choices,
        'is_authenticated': request.user.is_authenticated
    })


@login_required(login_url='login')
@redirect_if_not_permitted(lambda user: user.groups.filter(name__in=['Администраторы', 'Менеджеры']).exists())
def update_user_field(request, user_id):
    if request.method == 'POST':
        field_name = request.POST.get('field_name')
        field_value = request.POST.get('field_value')

        user = get_object_or_404(СustomUser, id_user=user_id)

        # Обновляем поле в зависимости от его типа
        if field_name == 'access_level':
            # Преобразуем строку с разделителями в список
            user.access_level = field_value.split(',') if field_value else []
            print(f"Обновляем access_level: {user.access_level}")  # Для отладки
        elif field_name == 'auditory':
            # Разбиваем строку с аудиториями на список
            auditory_list = field_value.split(',') if field_value else []

            # Обновляем user_acesses
            user_acesses = user.user_acesses or {}
            user_acesses['auditory'] = auditory_list
            user.user_acesses = user_acesses

            print(f"Обновляем auditory: {auditory_list}")  # Для отладки
            print(f"Новый user_acesses: {user.user_acesses}")  # Для отладки
        elif field_name == 'user_acesses':
            # Преобразуем строку JSON в словарь
            user.user_acesses = json.loads(field_value) if field_value else {}
        elif field_name in ['brand_model', 'color', 'time_access']:
            # Обработка полей автомобиля
            try:
                from .models import Car_access  # Импортируем модель Car_access
                car_access = Car_access.objects.filter(id_user=user.id_user).first()

                if car_access:
                    # Обновляем существующую запись
                    setattr(car_access, field_name, field_value)
                    car_access.save()
                    print(f"Обновлено поле {field_name} автомобиля: {field_value}")
                else:
                    print(f"Автомобиль для пользователя {user.user_name} не найден")

            except Exception as e:
                print(f"Ошибка при обновлении поля автомобиля: {e}")
        else:
            # Для обычных полей просто устанавливаем значение
            setattr(user, field_name, field_value)

        user.save()

        # Перенаправляем обратно на страницу пользователя
        return redirect('user_about', user_id=user_id)

    # Если запрос не POST, перенаправляем на страницу пользователя
    return redirect('user_about', user_id=user_id)

# Удаление пользователя
@login_required
@admin_or_manager_required
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
@admin_or_manager_required
def create_superuser_ajax(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        role = request.POST.get('role')  # Получаем выбранную роль

        # Проверяем обязательные поля
        if not username or not password or not email:
            return JsonResponse({'success': False, 'message': 'Логин, пароль и email обязательны.'}, status=400)

        # Проверяем уникальность имени пользователя
        if User.objects.filter(username=username).exists():
            return JsonResponse({'success': False, 'message': 'Пользователь с таким логином уже существует.'}, status=400)

        # Устанавливаем статусы в зависимости от роли
        is_staff = False
        is_superuser = False

        if role == 'Администраторы':
            is_staff = True
            is_superuser = True
        elif role == 'Менеджеры':
            is_staff = True
            is_superuser = False
        elif role == 'Операторы':
            is_staff = False
            is_superuser = False

        # Создаём пользователя
        try:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                is_staff=is_staff,
                is_superuser=is_superuser
            )
            user.first_name = first_name
            user.last_name = last_name
            user.save()

            # Добавляем пользователя в соответствующую группу
            if role:
                try:
                    group = Group.objects.get(name=role)
                    user.groups.add(group)
                except Group.DoesNotExist:
                    pass

            return JsonResponse({'success': True, 'message': f'Пользователь {username} успешно создан.'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Ошибка: {str(e)}'}, status=500)

    return JsonResponse({'success': False, 'message': 'Недопустимый запрос.'}, status=405)

@login_required
@redirect_if_not_permitted(lambda user: user.groups.filter(name__in=['Администраторы', 'Менеджеры']).exists())
def list_superusers(request):
    # Получаем ВСЕХ пользователей, а не только суперпользователей
    users = User.objects.all()

    # Создаем список пользователей с их ролями
    user_list = []
    for u in users:
        # Получаем группы пользователя
        groups = list(u.groups.all().values('id', 'name'))

        # Определяем роль на основе групп
        role = None
        group_id = None

        if groups:
            # Берем первую группу (если их несколько)
            group = groups[0]
            role = group['name']
            group_id = group['id']
        elif u.is_superuser:
            # Если пользователь суперпользователь, но не входит ни в одну группу,
            # считаем его администратором
            role = 'Администраторы'

        user_list.append({
            'id': u.id,
            'username': u.username,
            'email': u.email,
            'first_name': u.first_name,
            'last_name': u.last_name,
            'role': role or '',  # Убедимся, что role никогда не будет None
            'group_id': group_id,
            'is_superuser': u.is_superuser  # Добавляем флаг суперпользователя
        })

    return JsonResponse({
        'success': True,
        'superusers': user_list
    })


@login_required
@redirect_if_not_permitted(lambda user: user.groups.filter(name__in=['Администраторы', 'Менеджеры']).exists())
def get_superusers(request):
    from django.contrib.auth import get_user_model
    from django.db.models import Q
    import json

    User = get_user_model()

    # Получаем ВСЕХ пользователей, а не только суперпользователей
    users = User.objects.all()
    print(f"Total users found: {users.count()}")

    # Создаем список пользователей с их ролями
    user_list = []
    for u in users:
        # Получаем группы пользователя
        groups = list(u.groups.all().values('id', 'name'))

        # Определяем роль на основе групп
        role = None
        group_id = None

        if groups:
            # Берем первую группу (если их несколько)
            group = groups[0]
            role = group['name']
            group_id = group['id']
        elif u.is_superuser:
            # Если пользователь суперпользователь, но не входит ни в одну группу,
            # считаем его администратором
            role = 'Администраторы'

        # Выводим отладочную информацию
        print(f"User ID: {u.id}, Username: {u.username}")
        print(f"Is superuser: {u.is_superuser}")
        print(f"Groups: {groups}")
        print(f"Selected role: {role}")

        user_list.append({
            'id': u.id,
            'username': u.username,
            'email': u.email,
            'first_name': u.first_name,
            'last_name': u.last_name,
            'role': role or '',  # Убедимся, что role никогда не будет None
            'group_id': group_id,
            'is_superuser': u.is_superuser  # Добавляем флаг суперпользователя
        })

    return JsonResponse({
        'success': True,
        'superusers': user_list
    })

@login_required
@redirect_if_not_permitted(lambda user: user.groups.filter(name__in=['Администраторы', 'Менеджеры']).exists())
def get_superuser(request, user_id):
    try:
        from django.contrib.auth import get_user_model
        import json

        User = get_user_model()

        # Получаем пользователя без фильтра по is_superuser
        user = User.objects.get(id=user_id)

        # Получаем группы пользователя
        groups = list(user.groups.all().values('id', 'name'))

        # Определяем роль на основе групп
        role = None
        group_id = None

        if groups:
            # Берем первую группу (если их несколько)
            group = groups[0]
            role = group['name']
            group_id = group['id']
        elif user.is_superuser:
            # Если пользователь суперпользователь, но не входит ни в одну группу,
            # считаем его администратором
            role = 'Администраторы'

        # Выводим отладочную информацию
        print(f"Getting user: {user.id}, {user.username}")
        print(f"Is superuser: {user.is_superuser}")
        print(f"Groups: {groups}")
        print(f"Selected role: {role}")

        return JsonResponse({
            'success': True,
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'role': role or '',  # Убедимся, что role никогда не будет None
                'group_id': group_id,
                'is_superuser': user.is_superuser  # Добавляем флаг суперпользователя
            }
        })
    except User.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Пользователь не найден'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Ошибка: {str(e)}'}, status=500)

@login_required
@admin_or_manager_required
def delete_superuser(request, user_id):
    if request.method == 'DELETE':
        try:
            from django.contrib.auth import get_user_model
            User = get_user_model()

            # Находим пользователя по user_id без фильтра по is_superuser
            user = User.objects.get(id=user_id)

            # Удаляем пользователя
            user.delete()
            return JsonResponse({'success': True, 'message': 'Пользователь удален.'})
        except User.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Пользователь не найден'}, status=404)
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Ошибка: {str(e)}'}, status=500)

    return JsonResponse({'success': False, 'message': 'Неверный метод запроса.'}, status=405)

@login_required
@redirect_if_not_permitted(lambda user: user.groups.filter(name__in=['Администраторы', 'Менеджеры']).exists())
def admin_users_page(request):
    return render(request, 'myapp/admin_users.html')

@login_required
@admin_or_manager_required
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
@admin_or_manager_required
def edit_superuser(request, user_id):
    if request.method == 'POST':
        try:
            from django.contrib.auth import get_user_model
            from django.contrib.auth.models import Group
            User = get_user_model()

            # Находим пользователя по user_id без фильтра по is_superuser
            user = User.objects.get(id=user_id)

            user.username = request.POST.get('username')
            user.email = request.POST.get('email')
            user.first_name = request.POST.get('first_name')
            user.last_name = request.POST.get('last_name')

            # Обновляем роль пользователя
            role = request.POST.get('role')
            if role:
                # Удаляем пользователя из всех групп
                user.groups.clear()

                # Добавляем пользователя в выбранную группу
                try:
                    group = Group.objects.get(name=role)
                    user.groups.add(group)

                    # Устанавливаем статусы в зависимости от роли
                    if role == 'Администраторы':
                        user.is_staff = True
                        user.is_superuser = True
                    elif role == 'Менеджеры':
                        user.is_staff = True
                        user.is_superuser = False
                    elif role == 'Операторы':
                        user.is_staff = False
                        user.is_superuser = False
                except Group.DoesNotExist:
                    pass

            # Пароль не меняем, если не введён
            password = request.POST.get('password')
            if password:
                user.set_password(password)

            user.save()

            return JsonResponse({'success': True})
        except User.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Пользователь не найден'}, status=404)
    return JsonResponse({'success': False, 'message': 'Метод не поддерживается'}, status=405)


@login_required
def logs_page(request):
    """Отображение страницы с логами"""
    return render(request, 'logs_page.html')

@login_required
def system_logs_api(request):
    """API для получения системных логов"""
    page = int(request.GET.get('page', 1))
    per_page = int(request.GET.get('per_page', 12))
    sort = request.GET.get('sort', 'datetime')
    direction = request.GET.get('direction', 'desc')
    search = request.GET.get('search', '')
    auditory = request.GET.get('filter', '')

    # Получаем логи из базы данных
    logs = Logg.objects.all()

    # Применяем фильтры
    if search:
        logs = logs.filter(message__icontains=search)
    if auditory:
        logs = logs.filter(auditory_number__icontains=auditory)

    # Применяем сортировку
    order_by = f"{'-' if direction == 'desc' else ''}{sort}"
    logs = logs.order_by(order_by)

    # Пагинация
    paginator = Paginator(logs, per_page)
    logs_page = paginator.get_page(page)

    # Формируем ответ
    logs_data = []
    for log in logs_page:
        logs_data.append({
            'id': log.id,
            'datetime': log.datetime,
            'auditory_number': log.auditory_number,
            'message': log.message
        })

    return JsonResponse({
        'logs': logs_data,
        'total_count': paginator.count,
        'total_pages': paginator.num_pages,
        'current_page': page
    })

@login_required
def user_logs_api(request):
    """API для получения логов пользователей"""
    page = int(request.GET.get('page', 1))
    per_page = int(request.GET.get('per_page', 12))
    sort = request.GET.get('sort', 'datetime')
    direction = request.GET.get('direction', 'desc')
    search = request.GET.get('search', '')
    username = request.GET.get('filter', '')

    # Получаем логи из базы данных
    logs = Logg_access.objects.all()

    # Применяем фильтры
    if search:
        logs = logs.filter(message__icontains=search)
    if username:
        logs = logs.filter(username__icontains=username)

    # Применяем сортировку
    order_by = f"{'-' if direction == 'desc' else ''}{sort}"
    logs = logs.order_by(order_by)

    # Пагинация
    paginator = Paginator(logs, per_page)
    logs_page = paginator.get_page(page)

    # Формируем ответ
    logs_data = []
    for log in logs_page:
        # Получаем имя пользователя по uid_card
        user_name = None
        if log.uid_card:
            # Предполагаем, что у вас есть модель User с полем uid_card
            # Замените User на вашу модель пользователей
            try:
                user = СustomUser.objects.filter(uid_card=log.uid_card).first()
                if user:
                    # Используйте подходящее поле для имени пользователя
                    user_name = user.user_name  # или user.get_full_name() или другое поле
            except Exception as e:
                print(f"Ошибка при поиске пользователя: {e}")

        logs_data.append({
            'id': log.id,
            'datetime': log.datetime,
            'uid_card': log.uid_card,
            'action': log.action,
            'auditory_number': log.auditory_number,
            'username': user_name  # Добавляем имя пользователя в ответ
        })

    return JsonResponse({
        'logs': logs_data,
        'total_count': paginator.count,
        'total_pages': paginator.num_pages,
        'current_page': page
    })

@login_required
def device_logs_api(request):
    """API для получения логов устройств"""
    page = int(request.GET.get('page', 1))
    per_page = int(request.GET.get('per_page', 12))
    sort = request.GET.get('sort', 'datetime')
    direction = request.GET.get('direction', 'desc')
    search = request.GET.get('search', '')
    device_id = request.GET.get('filter', '')

    # Получаем логи из базы данных
    logs = Logg_parking.objects.all()

    # Применяем фильтры
    if search:
        logs = logs.filter(message__icontains=search)
    if device_id:
        logs = logs.filter(device_id__icontains=device_id)

    # Применяем сортировку
    order_by = f"{'-' if direction == 'desc' else ''}{sort}"
    logs = logs.order_by(order_by)

    # Пагинация
    paginator = Paginator(logs, per_page)
    logs_page = paginator.get_page(page)

    # Формируем ответ
    logs_data = []
    for log in logs_page:
        logs_data.append({
            'id': log.id,
            'datetime': log.datetime,
            'id_user': log.id_user,
            'message': log.message
        })

    return JsonResponse({
        'logs': logs_data,
        'total_count': paginator.count,
        'total_pages': paginator.num_pages,
        'current_page': page
    })

@login_required
def log_detail_api(request):
    """API для получения деталей лога"""
    log_id = request.GET.get('id')
    log_type = request.GET.get('log_type', 'system')

    if not log_id:
        return JsonResponse({'success': False, 'message': 'ID лога не указан'})

    try:
        # Выбираем модель в зависимости от типа лога
        if log_type == 'system':
            log = Logg.objects.get(id=log_id)
            log_data = {
                'id': log.id,
                'datetime': log.datetime,
                'auditory_number': log.auditory_number,
                'message': log.message
            }
        elif log_type == 'user':
            log = Logg_access.objects.get(id=log_id)
            log_data = {
                'id': log.id,
                'datetime': log.datetime,
                'uid_card': log.uid_card,
                'action': log.action,
                'auditory_number': log.auditory_number
            }
        elif log_type == 'device':
            log = Logg_parking.objects.get(id=log_id)
            log_data = {
                'id': log.id,
                'datetime': log.datetime,
                'id_user': log.id_user,
                'message': log.message
            }
        else:
            return JsonResponse({'success': False, 'message': 'Неизвестный тип лога'})

        return JsonResponse({'success': True, 'log': log_data})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})

@login_required
@redirect_if_not_permitted(lambda user: user.groups.filter(name__in=['Администраторы', 'Менеджеры']).exists())
@require_http_methods(["POST"])
def delete_log_api(request):
    """API для удаления лога"""
    try:
        data = json.loads(request.body)
        log_id = data.get('id')
        log_type = data.get('log_type', 'system')

        if not log_id:
            return JsonResponse({'success': False, 'message': 'ID лога не указан'})

        # Выбираем модель в зависимости от типа лога
        if log_type == 'system':
            log = Logg.objects.get(id=log_id)
        elif log_type == 'user':
            log = Logg_access.objects.get(id=log_id)
        elif log_type == 'device':
            log = Logg_parking.objects.get(id=log_id)
        else:
            return JsonResponse({'success': False, 'message': 'Неизвестный тип лога'})

        log.delete()
        return JsonResponse({'success': True, 'message': 'Лог успешно удален'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})

@login_required
def save_user(request):
    if request.method == "POST":
        form = UserForm(request.POST)

        if form.is_valid():
            user = form.save(commit=False)
            user_acesses = request.POST.get('user_acesses')


            if user_acesses:
                user_acesses_data = json.loads(user_acesses)
                user.user_acesses = user_acesses_data
            else:
                user.user_acesses = {}

            user.save()
            return redirect('product_list')

    return render(request, 'myapp/product_form.html', {'form': form})


# views.py
@login_required(login_url='login')
@redirect_if_not_permitted(lambda user: user.groups.filter(name__in=['Администраторы', 'Менеджеры']).exists())
def edit_access(request, user_id):
    user = get_object_or_404(СustomUser, id_user=user_id)
    car_access = Car_access.objects.filter(id_user=user_id).first()

    # Словарь дней недели
    days_choices = {
        'ПН': 'Понедельник',
        'ВТ': 'Вторник',
        'СР': 'Среда',
        'ЧТ': 'Четверг',
        'ПТ': 'Пятница',
        'СБ': 'Суббота',
        'ВС': 'Воскресенье'
    }

    # Если данные уже сохранены, разбиваем их на отдельные части (дни и время)
    if car_access and car_access.time_access:
        parts = car_access.time_access.split(';')
        if len(parts) >= 2:
            selected_days = parts[0].split(',')
            time_parts = parts[1].split(',')
            start_time = time_parts[0] if len(time_parts) > 0 else ''
            end_time = time_parts[1] if len(time_parts) > 1 else ''
        else:
            selected_days = []
            start_time = ''
            end_time = ''
    else:
        selected_days = []
        start_time = '09:00'  # Значения по умолчанию
        end_time = '18:00'

    if request.method == "POST":
        # Получаем данные о времени доступа
        selected_days = request.POST.getlist("days")
        start_time = request.POST.get("start_time")
        end_time = request.POST.get("end_time")

        # Получаем данные об автомобиле
        car_plate_number = request.POST.get("car_plate_number")
        brand_model = request.POST.get("brand_model")
        color = request.POST.get("color")

        # Проверяем, что все необходимые данные заполнены
        if selected_days and start_time and end_time and car_plate_number and brand_model and color:
            formatted_access = f"{','.join(selected_days)};{start_time},{end_time}"

            if car_access:
                # Обновляем существующую запись
                car_access.time_access = formatted_access
                car_access.car_plate_number = car_plate_number
                car_access.brand_model = brand_model
                car_access.color = color
                car_access.save()
            else:
                # Создаем новую запись
                Car_access.objects.create(
                    id_user=user_id,  # Используем id_user вместо user
                    time_access=formatted_access,
                    car_plate_number=car_plate_number,
                    brand_model=brand_model,
                    color=color
                )

            # Добавляем сообщение об успешном сохранении
            messages.success(request, "Информация об автомобиле и доступе успешно сохранена")
            return redirect('user_about', user_id=user_id)
        else:
            messages.error(request, "Пожалуйста, заполните все обязательные поля")

    # Подготавливаем контекст для шаблона
    context = {
        "user": user,
        "car_access": car_access,
        "selected_days": selected_days,
        "start_time": start_time,
        "end_time": end_time,
        "days_choices": days_choices
    }

    return render(request, "myapp/edit_access.html", context)


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
@login_required
@redirect_if_not_permitted(lambda user: user.groups.filter(name__in=['Администраторы', 'Менеджеры']).exists())
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
        if 'device_activated' in post_data:
            post_data['device_status'] = 'normal'
        else:
            post_data['device_status'] = 'timed out'

        # Обработка device_api
        device_api_input = post_data.get('device_api', '').strip()
        if not device_api_input:
            # Шаблон JSON с правильным форматированием
            default_api = {}
            post_data['device_api'] = json.dumps(default_api, indent=2)
        else:
            try:
                # Проверка и форматирование JSON
                if isinstance(device_api_input, dict):
                    post_data['device_api'] = json.dumps(device_api_input, indent=2)
                else:
                    parsed_json = json.loads(device_api_input)
                    post_data['device_api'] = json.dumps(parsed_json, indent=2)
            except json.JSONDecodeError:
                form = DeviceForm(post_data)
                form.add_error('device_api', "Невалидный JSON в API")
                return render(request, 'devices/device_form.html', {'form': form})

        form = DeviceForm(post_data)
        if form.is_valid():
            try:
                # Сохраняем форму, метод save в форме установит правильный id_device
                device = form.save()
                return redirect('device_list')
            except Exception as e:
                # Добавляем логирование ошибки
                print(f"Ошибка при сохранении устройства: {e}")
                form.add_error(None, f"Ошибка при сохранении: {e}")
        else:
            print("Ошибки формы:", form.errors)
    else:
        form = DeviceForm()
        # Предустановка шаблона JSON для нового устройства
        default_api = {
            "open": [
                "rel_0",
                "1",
                "0"
            ],
            "checkabe": "True",
            "commands": ["status"]
        }
        form.initial['device_api'] = json.dumps(default_api, indent=2)

    return render(request, 'devices/device_form.html', {'form': form})



@login_required
@redirect_if_not_permitted(lambda user: user.groups.filter(name__in=['Администраторы', 'Менеджеры']).exists())
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
            # Для JSONField мы можем передать словарь напрямую
            post_data['calendar_regular'] = json.dumps(calendar_regular)

            # calendar_exception
            calendar_exception = {
                "open_day": [day.strip() for day in (post_data.get('exception_open_day') or '').split(',') if day.strip()],
                "close_day": [day.strip() for day in (post_data.get('exception_close_day') or '').split(',') if day.strip()],
            }
            # Для JSONField мы можем передать словарь напрямую
            post_data['calendar_exception'] = json.dumps(calendar_exception)
        else:
            post_data['calendar_regular'] = 'null'
            post_data['calendar_exception'] = 'null'

        # Обработка флага активности
        if 'device_activated' in post_data:
            post_data['device_status'] = 'normal'
        else:
            post_data['device_status'] = 'timed out'

        form = DeviceForm(post_data, instance=device)
        if form.is_valid():
            form.save()
            return redirect('device_list')
        else:
            print("Ошибки формы:", form.errors)

    else:
        # Предзаполнение полей из JSON при GET-запросе
        try:
            # Для JSONField данные уже являются Python объектами
            calendar_regular = device.calendar_regular or {}
            calendar_exception = device.calendar_exception or {}
        except Exception as e:
            print(f"Ошибка при получении данных календаря: {e}")
            calendar_regular = {}
            calendar_exception = {}

        # Заполняем поля формы
        device.open_day = ', '.join(calendar_regular.get('open_day', []))
        device.open_time = calendar_regular.get('open_time', '')
        device.close_day = ', '.join(calendar_regular.get('close_day', []))
        device.close_time = calendar_regular.get('close_time', '')
        device.exception_open_day = ', '.join(calendar_exception.get('open_day', []))
        device.exception_close_day = ', '.join(calendar_exception.get('close_day', []))

        form = DeviceForm(instance=device)

    return render(request, 'devices/device_form.html', {'form': form, 'device': device})

@login_required
@redirect_if_not_permitted(lambda user: user.groups.filter(name__in=['Администраторы', 'Менеджеры']).exists())
def DeviceDeleteView(request, pk):
    device = get_object_or_404(Device, pk=pk)
    if request.method == 'POST':
        device.delete()
        messages.success(request, f"User {device.name} has been deleted.")
        return redirect('device_list')
    return render(request, 'devices/device_confirm_delete.html', {'device': device})

@login_required
@redirect_if_not_permitted(lambda user: user.groups.filter(name__in=['Администраторы', 'Менеджеры']).exists())
def update_device_field(request, device_id):
    """Обновление отдельного поля устройства через AJAX"""
    if request.method == 'POST':
        device = get_object_or_404(Device, id_device=device_id)
        field_name = request.POST.get('field_name')
        field_value = request.POST.get('field_value')

        try:
            # Обработка различных типов полей
            if field_name == 'device_activated':
                device.device_activated = field_value.lower() == 'true'
                # Автоматически обновляем статус при изменении активации
                device.device_status = 'normal' if device.device_activated else 'timed out'
            elif field_name == 'checkable':
                device.checkable = field_value.lower() == 'true'
            elif field_name == 'device_api':
                # Проверяем и сохраняем JSON
                try:
                    parsed_json = json.loads(field_value)
                    device.device_api = parsed_json
                except json.JSONDecodeError:
                    messages.error(request, 'Невалидный JSON в Device API')
                    return redirect('device_detail', pk=device_id)
            elif field_name in ['trying_open', 'trying_close', 'trying_max', 'trying_delay', 'period']:
                # Числовые поля
                setattr(device, field_name, int(field_value))
            else:
                # Обычные текстовые поля
                setattr(device, field_name, field_value)

            device.save()
            messages.success(request, f'Поле "{field_name}" успешно обновлено')

        except Exception as e:
            messages.error(request, f'Ошибка при обновлении поля: {str(e)}')

    return redirect('device_detail', pk=device_id)

@login_required
def device_detail(request, pk):
    """Детальная страница устройства"""
    device = get_object_or_404(Device, pk=pk)

    context = {
        'device': device,
    }

    return render(request, 'devices/device_detail.html', context)

@login_required
def dashboard(request):
    return render(request, "myapp/dashboard.html")


@login_required
def get_dashboard_data(request):
    """API для получения данных дашборда: логи, пользователи, устройства и ключи."""

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

    # Получаем данные об устройствах
    devices_data = []
    devices = Device.objects.all()
    for device in devices:
        devices_data.append({
            'id_device': device.id_device,
            'device_name': device.name,  # Используем поле name вместо device_name
            'device_status': device.device_status or 'normal',  # Устанавливаем 'normal' если None
            'mac': device.mac,
            'ip': device.ip,
            'device_activated': device.device_activated
        })

    # Получаем данные о ключах на руках
    keys_on_hands = []
    total_auditories = 0

    try:
        # Проверяем, существует ли модель Auditory
        try:
            from .models import Auditory

            # Получаем все аудитории, где ключи не в ключнице
            auditories = Auditory.objects.exclude(
                key_holder__isnull=True
            ).exclude(
                key_holder=''
            ).exclude(
                key_holder='home'
            ).exclude(
                key_holder='0'
            )

            total_auditories = Auditory.objects.count()

            for auditory in auditories:
                # Парсим поле key_holder для извлечения ID пользователей
                user_ids = parse_key_holder(auditory.key_holder)

                for user_id in user_ids:
                    try:
                        user = СustomUser.objects.get(id_user=user_id)
                        keys_on_hands.append({
                            'auditory_number': auditory.auditory_number,
                            'user_id': user.id_user,
                            'user_name': user.user_name,
                            'user_department': user.departments or 'Не указан',
                            'user_occupations': user.occupations or 'Не указано',
                            'key_holder_raw': auditory.key_holder
                        })
                    except СustomUser.DoesNotExist:
                        # Пользователь не найден, но ключ числится за ним
                        keys_on_hands.append({
                            'auditory_number': auditory.auditory_number,
                            'user_id': user_id,
                            'user_name': f'Пользователь #{user_id} (не найден)',
                            'user_department': 'Неизвестно',
                            'user_occupations': 'Неизвестно',
                            'key_holder_raw': auditory.key_holder
                        })

        except ImportError:
            print("Модель Auditory не найдена, пропускаем данные о ключах")
            keys_on_hands = []
            total_auditories = 0

    except Exception as e:
        print(f"Ошибка при получении данных о ключах: {e}")
        keys_on_hands = []

    # Статистика
    stats = {
        'total_users': СustomUser.objects.count(),
        'active_devices': Device.objects.filter(device_activated=True).count(),
        'total_devices': Device.objects.count(),
        'keys_on_hands_count': len(keys_on_hands),
        'total_auditories': total_auditories,
        'total_logs': Logg.objects.count(),
    }

    return JsonResponse({
        "logs": logs_data,
        "last_user": last_user_data,
        'devices': devices_data,
        'keys_on_hands': keys_on_hands,
        'stats': stats,
        'status': 'success'
    })


def parse_key_holder(key_holder_value):
    """
    Парсит значение key_holder и возвращает список ID пользователей.

    Обрабатывает форматы:
    - "4" -> [4]
    - "home:4" -> [4]
    - "home" -> []
    - "" -> []
    """
    if not key_holder_value or key_holder_value == 'home':
        return []

    user_ids = []

    # Обрабатываем случай "home:4(id_user)" или "home:4"
    if ':' in key_holder_value:
        parts = key_holder_value.split(':')
        if len(parts) > 1:
            user_part = parts[1]
            # Извлекаем ID пользователя из скобок, если они есть
            if '(' in user_part and ')' in user_part:
                user_id_str = user_part.split('(')[1].split(')')[0]
            else:
                user_id_str = user_part

            try:
                user_id = int(user_id_str)
                user_ids.append(user_id)
            except ValueError:
                pass
    else:
        # Простой случай - только ID пользователя
        try:
            user_id = int(key_holder_value)
            user_ids.append(user_id)
        except ValueError:
            pass

    return user_ids