# Generated by Django 5.0.3 on 2024-09-16 17:24

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('exp_tracker', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='expense',
            name='date',
            field=models.DateField(default=datetime.date(2024, 9, 16)),
        ),
    ]
