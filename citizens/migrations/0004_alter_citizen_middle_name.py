# Generated by Django 3.2.8 on 2021-10-23 15:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('citizens', '0003_auto_20211023_1843'),
    ]

    operations = [
        migrations.AlterField(
            model_name='citizen',
            name='middle_name',
            field=models.CharField(blank=True, max_length=60, null=True, verbose_name='Отчество'),
        ),
    ]
