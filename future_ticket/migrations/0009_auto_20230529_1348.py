# Generated by Django 3.2.8 on 2023-05-29 09:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('future_ticket', '0008_alter_ticketprogram_workshops'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='ticketprogram',
            name='is_federal',
        ),
        migrations.AddField(
            model_name='ticketprofession',
            name='is_federal',
            field=models.BooleanField(default=False, verbose_name='Федеральная?'),
        ),
        migrations.AddField(
            model_name='ticketprogram',
            name='status',
            field=models.CharField(choices=[('NEW', 'Новая'), ('PRWD', 'Подтверждённая')], default='NEW', max_length=5, verbose_name='Статус программы'),
        ),
        migrations.AlterField(
            model_name='ticketprogram',
            name='education_form',
            field=models.CharField(choices=[('FLL', 'Очная'), ('FLLLN', 'Очная с применением ДОТ')], max_length=5, verbose_name='Форма обучения'),
        ),
    ]
