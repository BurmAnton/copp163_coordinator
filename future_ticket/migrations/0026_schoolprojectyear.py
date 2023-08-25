# Generated by Django 3.2.8 on 2023-06-28 07:55

from django.db import migrations, models
import django.db.models.deletion
import future_ticket.models


class Migration(migrations.Migration):

    dependencies = [
        ('citizens', '0006_remove_citizen_aplication_stages'),
        ('future_ticket', '0025_auto_20230613_1734'),
    ]

    operations = [
        migrations.CreateModel(
            name='SchoolProjectYear',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('resp_full_name', models.CharField(max_length=250, verbose_name='ФИО ответственного')),
                ('resp_position', models.CharField(max_length=100, verbose_name='Должность')),
                ('phone', models.CharField(max_length=120, verbose_name='Телефон')),
                ('email', models.EmailField(max_length=254, verbose_name='email address')),
                ('resp_order', models.FileField(upload_to=future_ticket.models.SchoolProjectYear.template_directory_path, verbose_name='Приказ')),
                ('project_year', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='schools', to='future_ticket.ticketprojectyear', verbose_name='Год проекта (БВБ)')),
                ('school', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ticket_project_years', to='citizens.school', verbose_name='Школа')),
            ],
            options={
                'verbose_name': 'Школа (год проекта)',
                'verbose_name_plural': 'Школы (годы проекта)',
            },
        ),
    ]
