# Generated by Django 4.2.11 on 2024-04-18 00:08

import django.contrib.auth.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crud', '0007_supportmessage'),
    ]

    operations = [
        migrations.AlterField(
            model_name='student',
            name='fullname',
            field=models.CharField(default='No Name Provided', max_length=90, verbose_name=django.contrib.auth.models.User),
        ),
        migrations.AlterField(
            model_name='student',
            name='id_user',
            field=models.IntegerField(editable=False, null=True, verbose_name=django.contrib.auth.models.User),
        ),
    ]
