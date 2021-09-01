# Generated by Django 3.2.5 on 2021-08-24 08:36

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('education_centers', '0014_remove_schoolclass_students'),
        ('citizens', '0004_auto_20210824_1235'),
    ]

    operations = [
        migrations.AlterField(
            model_name='citizen',
            name='school',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='students', to='education_centers.school', verbose_name='Школа'),
        ),
        migrations.AlterField(
            model_name='citizen',
            name='school_class',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='students', to='education_centers.schoolclass', verbose_name='Школный класс'),
        ),
    ]