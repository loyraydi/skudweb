# Generated by Django 5.1.2 on 2025-01-23 09:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0011_rename_user_сustomuser'),
    ]

    operations = [
        migrations.AlterField(
            model_name='сustomuser',
            name='reg',
            field=models.IntegerField(choices=[(0, 'Не завершил регистрацию'), (1, 'Зарегистрировался'), (2, 'Ожидает активации через Telegram')], default=0),
        ),
    ]
