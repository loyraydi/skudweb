from django.db import models


class СustomUser(models.Model):

    id_user = models.AutoField(primary_key=True)
    code_activation = models.CharField(max_length=100, blank=True, null=True, verbose_name='Код активации')
    uid_card = models.CharField(max_length=50, blank=True, null=True, verbose_name='Код пропуска')

    REG_CHOICES  = [
        (0, 'Не завершил регистрацию'),
        (1, 'Зарегистрировался'),
        (2, 'Ожидает активации через Telegram'),
    ]
    reg = models.IntegerField(choices=REG_CHOICES, default=0)
    access_level = models.CharField(max_length=100, verbose_name='Уровень доступа')
    user_name = models.CharField(max_length=100,verbose_name='Фио')
    departments = models.CharField(max_length=100, blank=True, null=True,verbose_name='Департамент')
    occupations = models.CharField(max_length=100, blank=True, null=True,verbose_name='Должность')
    phone_number = models.CharField(max_length=100, blank=True, null=True,verbose_name='Номер телефона')
    email = models.EmailField(blank=True, null=True,verbose_name='Эл.почта')
    telegram = models.BigIntegerField(blank=True, null=True,verbose_name='Telegram ID')
    user_acesses = models.JSONField(blank=True,null=True,default=dict, verbose_name='Доступы')

    class Meta:
        db_table = 'users'

    def __str__(self):
        return self.user_name


class Car_access(models.Model):
    id_user = models.AutoField(primary_key=True)
    car_plate_number = models.CharField(max_length=100)
    brand_model = models.CharField(max_length=100)
    color = models.CharField(max_length=100)
    time_access = models.CharField(max_length=100)

    class Meta:
        db_table = 'car_access'

    def __str__(self):
        return self.id_user


class Logg(models.Model):
    datetime = models.CharField(max_length=26)
    message = models.TextField(max_length=100)
    auditory_number = models.CharField(max_length=15)

    class Meta:

        db_table = "logg"

    def __str__(self):
        return f"[{self.datetime}] {self.message}: {self.auditory_number}"
