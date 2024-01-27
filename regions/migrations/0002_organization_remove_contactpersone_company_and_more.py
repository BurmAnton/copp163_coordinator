# Generated by Django 4.2.6 on 2024-01-21 13:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('regions', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Organization',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, verbose_name='Название организации')),
            ],
            options={
                'verbose_name': 'Организация',
                'verbose_name_plural': 'Организации',
            },
        ),
        migrations.RemoveField(
            model_name='contactpersone',
            name='company',
        ),
        migrations.RemoveField(
            model_name='vacancy',
            name='company',
        ),
        migrations.DeleteModel(
            name='Company',
        ),
        migrations.DeleteModel(
            name='ContactPersone',
        ),
        migrations.DeleteModel(
            name='Vacancy',
        ),
    ]