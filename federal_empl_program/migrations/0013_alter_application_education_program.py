# Generated by Django 3.2.5 on 2021-08-21 13:22

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('education_centers', '0010_auto_20210820_1104'),
        ('federal_empl_program', '0012_alter_application_education_program'),
    ]

    operations = [
        migrations.AlterField(
            model_name='application',
            name='education_program',
            field=models.ForeignKey(blank=True, limit_choices_to={'competence': models.Q('competence')}, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='programm_applicants', to='education_centers.educationprogram', verbose_name='Програма обучения'),
        ),
    ]