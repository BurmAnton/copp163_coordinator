# Generated by Django 4.2 on 2023-10-27 08:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('future_ticket', '0020_ticketevent_photo_link'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ticketevent',
            name='status',
            field=models.CharField(choices=[('CRTD', 'Создана'), ('LOAD', 'Фото и видеоматериалы загружены')], default='CRTD', max_length=6, verbose_name='Статус'),
        ),
    ]
