# myapp/forms.py
from django import forms
from .models import СustomUser, Car_access, Device
from django.contrib.auth.forms import AuthenticationForm
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User
import json
import uuid

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


class DeviceForm(forms.ModelForm):
    class Meta:
        model = Device
        fields = [
            "name", "mac", "device_activated", "device_api",
            "calendar_regular", "calendar_exception", "trying_max"
        ]
        widgets = {
            'device_api': forms.Textarea(attrs={"rows": 6}),
            'calendar_regular': forms.HiddenInput(),
            'calendar_exception': forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Устанавливаем значение по умолчанию только если форма создаётся, а не редактируется
        if not self.instance.pk:
            self.fields['device_api'].initial = json.dumps({
                "open": [""],
                "checkabe": "",
                "commands": [""]
            }, indent=4)

    def clean_mac(self):
        mac = self.cleaned_data.get("mac")
        if Device.objects.filter(mac=mac).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("Устройство с таким MAC-адресом уже существует.")
        return mac

    def clean_calendar_regular(self):
        data = self.cleaned_data.get("calendar_regular")
        try:
            return json.loads(data) if data else {}
        except json.JSONDecodeError:
            raise forms.ValidationError("Ошибка в формате JSON")

    def clean_calendar_exception(self):
        data = self.cleaned_data.get("calendar_exception")
        try:
            return json.loads(data) if data else {}
        except json.JSONDecodeError:
            raise forms.ValidationError("Ошибка в формате JSON")

    def save(self, commit=True):
        instance = super().save(commit=False)
        if not instance.token:
            instance.token = uuid.uuid4().hex
        if commit:
            instance.save()
        return instance