# Generated by Django 4.2.6 on 2024-03-28 10:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('federal_empl_program', '0071_citizenapplication_created_at'),
    ]

    operations = [
        migrations.AlterField(
            model_name='citizenapplication',
            name='created_at',
            field=models.DateField(auto_now_add=True),
        ),
    ]
