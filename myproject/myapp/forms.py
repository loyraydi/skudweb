# myapp/forms.py
from django import forms
from .models import СustomUser, Car_access
from django.contrib.auth.forms import AuthenticationForm
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User


class UserForm(forms.ModelForm):
    access_level_choices = [
        ('user', 'User'),
        ('admin', 'Admin'),
        ('kent', 'Kent'),
        ('alien', 'Alien'),
    ]

    # Добавляем поле с чекбоксами для уровней доступа
    access_level = forms.MultipleChoiceField(
        choices=access_level_choices,
        widget=forms.CheckboxSelectMultiple,
        label="Access Level"
    )

    class Meta:
        model = СustomUser
        fields = '__all__'
        widgets = {
            'reg': forms.RadioSelect,  # Указываем, что это будет radio button
        }
    def clean_access_level(self):
        # Получаем выбранные значения чекбоксов
        selected_levels = self.cleaned_data['access_level']
        # Преобразуем список в строку, разделяя значения точкой с запятой
        return ';'.join(selected_levels)


class CarsForm(forms.ModelForm):

    class Mete:
        model = Car_access
        fields = '__all__'


class CustomAuthenticationForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.error_messages['invalid_login'] = _('Неверный логин или пароль.')
        self.error_messages['inactive'] = _('Этот аккаунт отключён.')


class AdminUserCreationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, label="Пароль")
    password_confirm = forms.CharField(widget=forms.PasswordInput, label="Подтвердите пароль")

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']

    def clean_password_confirm(self):
        password = self.cleaned_data.get('password')
        password_confirm = self.cleaned_data.get('password_confirm')
        if password != password_confirm:
            raise forms.ValidationError("Пароли не совпадают")
        return password_confirm
