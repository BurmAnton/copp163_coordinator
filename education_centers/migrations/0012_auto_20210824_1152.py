# Generated by Django 3.2.5 on 2021-08-24 07:52

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('education_centers', '0011_school_schoolclass_schoolstudent'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='school',
            options={'verbose_name': 'Школа', 'verbose_name_plural': 'Школы'},
        ),
        migrations.AlterField(
            model_name='schoolclass',
            name='grade_number',
            field=models.IntegerField(validators=[django.core.validators.MaxValueValidator(11), django.core.validators.MinValueValidator(1)], verbose_name='Номер класса'),
        ),
        migrations.AlterField(
            model_name='schoolclass',
            name='specialty',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='Уклон класса'),
        ),
        migrations.AlterField(
            model_name='schoolstudent',
            name='school_class',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='student', to='education_centers.schoolclass', verbose_name='Класс'),
        ),
    ]
