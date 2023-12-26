# Generated by Django 4.2.6 on 2023-12-24 17:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('federal_empl_program', '0023_alter_application_contract_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='employmentinvoice',
            name='stage',
            field=models.CharField(blank=True, choices=[('GNRT', 'Сгенерирован'), ('NVC', 'Подгружен счёт'), ('SPD', 'На оплату'), ('PD', 'Оплачен')], default='GNRT', max_length=4, null=True, verbose_name='Стадии'),
        ),
    ]