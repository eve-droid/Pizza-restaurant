# Generated by Django 5.1.1 on 2024-10-08 19:24

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Customer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('gender', models.CharField(choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')], max_length=10)),
                ('birthday', models.DateField()),
                ('phone', models.CharField(max_length=100)),
                ('address_number_street', models.CharField(max_length=100)),
                ('address_city', models.CharField(max_length=100)),
                ('address_postal_code', models.CharField(default='', max_length=100)),
                ('count_pizza', models.IntegerField(default=0)),
                ('had_BD_gift', models.BooleanField(default=False)),
                ('user', models.OneToOneField(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
