# Generated by Django 3.2.8 on 2021-10-23 14:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('citizens', '0002_auto_20211023_1739'),
    ]

    operations = [
        migrations.AlterField(
            model_name='citizen',
            name='res_city',
            field=models.CharField(blank=True, max_length=150, null=True, verbose_name='Населённый пункт'),
        ),
        migrations.AlterField(
            model_name='citizen',
            name='res_region',
            field=models.CharField(blank=True, max_length=150, null=True, verbose_name='Регион проживания'),
        ),
    ]