# Generated by Django 4.2.6 on 2024-03-03 16:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('federal_empl_program', '0048_alter_fgosstandart_code'),
    ]

    operations = [
        migrations.AlterField(
            model_name='irpoprogram',
            name='status',
            field=models.CharField(blank=True, choices=[('1', 'Шаг 1. Общие сведения о программе'), ('2', 'Шаг 2. Планируемые результаты обучения'), ('3', 'Шаг 3. Учебно-тематический план'), ('4', 'Шаг 4. Календарный учебный график'), ('5', 'Шаг 6. Материально-техническое обеспечение'), ('6', 'Шаг 7. Информационное и учебно-методическое обеспечение')], default='1', max_length=5, null=True, verbose_name='Статус'),
        ),
    ]
