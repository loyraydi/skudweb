# Generated by Django 5.1.2 on 2024-11-07 07:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("myapp", "0005_alter_user_access_level_alter_user_table"),
    ]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="phone_number",
            field=models.DecimalField(decimal_places=3, max_digits=11),
        ),
        migrations.AlterField(
            model_name="user",
            name="uid_card",
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]
