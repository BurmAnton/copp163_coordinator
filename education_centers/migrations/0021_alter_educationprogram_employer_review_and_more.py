# Generated by Django 4.2.6 on 2024-02-28 16:34

from django.db import migrations, models
import education_centers.models


class Migration(migrations.Migration):

    dependencies = [
        ('education_centers', '0020_educationprogram_employer_review_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='educationprogram',
            name='employer_review',
            field=models.FileField(blank=True, max_length=500, null=True, upload_to=education_centers.models.EducationProgram.irpo_directory_path, verbose_name='Рецензии работодателя (pdf)'),
        ),
        migrations.AlterField(
            model_name='educationprogram',
            name='program_pdf',
            field=models.FileField(blank=True, max_length=500, null=True, upload_to=education_centers.models.EducationProgram.irpo_directory_path, verbose_name='Программа, подписанная работодателем (pdf)'),
        ),
        migrations.AlterField(
            model_name='educationprogram',
            name='program_word',
            field=models.FileField(blank=True, max_length=500, null=True, upload_to=education_centers.models.EducationProgram.irpo_directory_path, verbose_name='Программа по шаблону ИРПО (word)'),
        ),
        migrations.AlterField(
            model_name='educationprogram',
            name='teacher_review',
            field=models.FileField(blank=True, max_length=500, null=True, upload_to=education_centers.models.EducationProgram.irpo_directory_path, verbose_name='Рецензии преподавателя (pdf)'),
        ),
    ]