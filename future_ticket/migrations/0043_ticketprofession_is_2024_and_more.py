# Generated by Django 4.2.6 on 2024-08-27 15:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('future_ticket', '0042_educationcenterticketprojectyear_locked_quota_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='ticketprofession',
            name='is_2024',
            field=models.BooleanField(default=False, verbose_name='2024?'),
        ),
        migrations.AlterField(
            model_name='ticketprogram',
            name='education_form',
            field=models.CharField(choices=[('FLL', 'Очный'), ('FLLLN', 'Очный с применением ДОТ')], default='FLL', max_length=5, verbose_name='Формат обучения'),
        ),
    ]