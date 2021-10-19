# Generated by Django 3.2.5 on 2021-09-23 06:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('federal_empl_program', '0016_alter_application_contract_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='application',
            name='contract_type',
            field=models.CharField(choices=[('OLD', 'Трехсторонний договор со старым работодателем'), ('NEW', 'Трехсторонний договор с новым работодателем'), ('SELF', 'Двухсторонный договор'), ('NOT', 'Без договора'), ('–', '-')], default='–', max_length=4, verbose_name='Тип контракта'),
        ),
    ]