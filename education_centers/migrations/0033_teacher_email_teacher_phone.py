# Generated by Django 4.2.6 on 2024-08-13 11:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('education_centers', '0032_teacher_is_certified_teacher_is_experienced'),
    ]

    operations = [
        migrations.AddField(
            model_name='teacher',
            name='email',
            field=models.EmailField(blank=True, max_length=254, null=True, verbose_name='email address'),
        ),
        migrations.AddField(
            model_name='teacher',
            name='phone',
            field=models.CharField(blank=True, max_length=120, null=True, verbose_name='Телефон(-ы)'),
        ),
    ]