# Generated by Django 3.2.8 on 2021-10-25 18:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('citizens', '0004_alter_citizen_middle_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='citizen',
            name='phone_number',
            field=models.CharField(blank=True, max_length=35, null=True, verbose_name='Номер телефона'),
        ),
    ]
