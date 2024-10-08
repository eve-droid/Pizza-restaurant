# Generated by Django 5.1.1 on 2024-10-08 08:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0011_all_ingredients_vegetarian_alter_order_status'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='all_ingredients',
            name='vegetarian',
        ),
        migrations.RemoveField(
            model_name='deliveryperson',
            name='postal_code',
        ),
        migrations.AddField(
            model_name='deliveryperson',
            name='address_city',
            field=models.CharField(default='lyon', max_length=100),
        ),
        migrations.AddField(
            model_name='deliveryperson',
            name='last_assigned_time',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('Processing', 'Processing'), ('Making', 'Making'), ('Out for Delivery', 'Out for Delivery'), ('Delivered', 'Delivered'), ('Cancelled', 'Cancelled')], default='Processing', max_length=100),
        ),
    ]
