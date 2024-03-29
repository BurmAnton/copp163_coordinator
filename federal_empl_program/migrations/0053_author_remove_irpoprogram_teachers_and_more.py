# Generated by Django 4.2.6 on 2024-03-04 00:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('federal_empl_program', '0052_activitycompetence_function_code_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Author',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=600, verbose_name='ФИО')),
                ('degree', models.CharField(blank=True, max_length=250, null=True, verbose_name='Учёная степень')),
                ('position', models.CharField(max_length=250, verbose_name='Должность')),
                ('place_of_work', models.CharField(max_length=600, verbose_name='Место работы')),
            ],
            options={
                'verbose_name': 'Разработчик программы',
                'verbose_name_plural': 'Разработчики программы',
            },
        ),
        migrations.RemoveField(
            model_name='irpoprogram',
            name='teachers',
        ),
        migrations.AddField(
            model_name='irpoprogram',
            name='authors',
            field=models.ManyToManyField(blank=True, related_name='irpo_programs', to='federal_empl_program.author', verbose_name='Разработчики'),
        ),
    ]
