# Generated by Django 4.2.11 on 2024-04-16 19:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crud', '0005_alter_student_id_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='student',
            name='fullname',
            field=models.CharField(default='No Name Provided', max_length=90),
        ),
    ]
