# myapp/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from .models import СustomUser, Car_access
from .forms import UserForm, CarsForm, CustomAuthenticationForm, AdminUserCreationForm
from .filters import UserFilter
from django.db.models import Q
from django.contrib import messages
from django.contrib.auth import login, authenticate
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User



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
    if form.is_valid():
        form.save()
        return redirect('user_list')
    return render(request, 'myapp/product_form.html', {'form': form, 'access_level_choices': access_level_choices})


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
