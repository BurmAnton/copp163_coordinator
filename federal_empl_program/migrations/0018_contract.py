# Generated by Django 4.2.6 on 2023-12-23 08:16

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('federal_empl_program', '0017_alter_citizencategory_official_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='Contract',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.CharField(max_length=100, verbose_name='Номер договора')),
                ('ed_center', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='contracts', to='federal_empl_program.educationcenterprojectyear', verbose_name='ЦО')),
                ('project_year', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='contracts', to='federal_empl_program.projectyear', verbose_name='Год проекта')),
            ],
            options={
                'verbose_name': 'Договор на организацию обучения',
                'verbose_name_plural': 'Договоры на организацию обучения',
            },
        ),
    ]