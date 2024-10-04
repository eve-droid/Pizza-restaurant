# Generated by Django 5.1.1 on 2024-10-04 09:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0006_order_has_discount_code'),
    ]

    operations = [
        migrations.CreateModel(
            name='DeliveryPerson',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('postal_code', models.CharField(max_length=20)),
                ('available', models.BooleanField(default=True)),
                ('assigned_orders', models.IntegerField(default=0)),
            ],
        ),
        migrations.AddField(
            model_name='order',
            name='estimated_delivery_time',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
