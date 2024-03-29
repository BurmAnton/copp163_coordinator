# Generated by Django 4.2.6 on 2024-03-05 11:58

from django.db import migrations, models
import education_centers.models


class Migration(migrations.Migration):

    dependencies = [
        ('education_centers', '0023_alter_educationprogram_teacher_review'),
    ]

    operations = [
        migrations.AlterField(
            model_name='educationprogram',
            name='employer_review',
            field=models.FileField(blank=True, max_length=1500, null=True, upload_to=education_centers.models.EducationProgram.irpo_directory_path, verbose_name='Рецензии работодателя (pdf)'),
        ),
    ]
