# Generated by Django 3.2.8 on 2023-05-27 14:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('education_centers', '0045_educationprogram_is_bvb'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='educationprogram',
            name='is_bvb',
        ),
        migrations.AlterField(
            model_name='educationprogram',
            name='description',
            field=models.TextField(blank=True, null=True, verbose_name='Описание программы'),
        ),
    ]
