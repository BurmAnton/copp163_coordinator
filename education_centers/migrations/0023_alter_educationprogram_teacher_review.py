# Generated by Django 4.2.6 on 2024-03-05 10:19

from django.db import migrations, models
import education_centers.models


class Migration(migrations.Migration):

    dependencies = [
        ('education_centers', '0022_alter_educationprogram_program_pdf_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='educationprogram',
            name='teacher_review',
            field=models.FileField(blank=True, max_length=1500, null=True, upload_to=education_centers.models.EducationProgram.irpo_directory_path, verbose_name='Рецензии преподавателя (pdf)'),
        ),
    ]
