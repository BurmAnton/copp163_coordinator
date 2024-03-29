# Generated by Django 4.2.6 on 2024-03-03 12:36

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('federal_empl_program', '0038_irpoprogram_duration'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProfField',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=5, unique=True, verbose_name='Код')),
                ('name', models.CharField(max_length=250, verbose_name='Наименование области профессиональной деятельности')),
            ],
            options={
                'verbose_name': 'Вид проф. деятельности',
                'verbose_name_plural': 'Перечень видов проф. деятельности',
            },
        ),
        migrations.AlterField(
            model_name='irpoprogram',
            name='education_form',
            field=models.CharField(blank=True, choices=[('FLL', 'Очная'), ('PRT', 'Очно-заочная'), ('PRTF', 'Заочная'), ('PRTLN', 'Очно-заочная'), ('FLLLN', 'Очная')], max_length=5, null=True, verbose_name='Форма обучения'),
        ),
        migrations.AlterField(
            model_name='irpoprogram',
            name='status',
            field=models.CharField(blank=True, choices=[('0', 'Ожидает заполнения'), ('1', 'Шаг 1. Общие сведения о программе'), ('2', 'Шаг 2. Планируемые результаты обучения'), ('3', 'Шаг 3. Учебно-тематический план'), ('4', 'Шаг 4. Календарный учебный график'), ('5', 'Шаг 6. Материально-техническое обеспечение'), ('6', 'Шаг 7. Информационное и учебно-методическое обеспечение')], default='0', max_length=5, null=True, verbose_name='Статус'),
        ),
        migrations.AlterField(
            model_name='irpoprogram',
            name='prof_field',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='irpo_programs', to='federal_empl_program.proffield', verbose_name='Область профессиональной деятельности'),
        ),
    ]
