# Generated by Django 3.2.8 on 2023-05-04 09:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('education_centers', '0036_alter_workshop_programs'),
    ]

    operations = [
        migrations.AlterField(
            model_name='workshop',
            name='adress',
            field=models.CharField(blank=True, max_length=200, null=True, verbose_name='Адрес'),
        ),
    ]
