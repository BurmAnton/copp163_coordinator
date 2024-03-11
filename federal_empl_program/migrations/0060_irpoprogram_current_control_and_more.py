# Generated by Django 4.2.6 on 2024-03-07 04:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('federal_empl_program', '0059_alter_irpoprogram_duration_days'),
    ]

    operations = [
        migrations.AddField(
            model_name='irpoprogram',
            name='current_control',
            field=models.TextField(blank=True, null=True, verbose_name='Описание требований к проведению текущей аттестации'),
        ),
        migrations.AddField(
            model_name='irpoprogram',
            name='final_control',
            field=models.TextField(blank=True, null=True, verbose_name='Описание процедуры проведения итоговой аттестации'),
        ),
        migrations.AddField(
            model_name='irpoprogram',
            name='final_control_criteria',
            field=models.TextField(blank=True, null=True, verbose_name='Критерии оценивания'),
        ),
        migrations.AddField(
            model_name='irpoprogram',
            name='final_control_matereils',
            field=models.TextField(blank=True, null=True, verbose_name='Характеристика материалов итоговой аттестации'),
        ),
        migrations.AddField(
            model_name='irpoprogram',
            name='middle_control',
            field=models.TextField(blank=True, null=True, verbose_name='Описание требований к выполнению заданий промежуточной аттестации'),
        ),
        migrations.AddField(
            model_name='irpoprogram',
            name='min_score',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='Минимальный балл'),
        ),
    ]