# Generated by Django 5.0.4 on 2024-04-15 19:55

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('crud', '0003_student_name'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='student',
            name='name',
        ),
    ]
