# Generated by Django 3.2.8 on 2021-10-23 16:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vocational_guidance', '0003_rename_disability_type_vocguidtest_disability_types'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vocguidtest',
            name='name',
            field=models.CharField(default='', max_length=300, verbose_name='Название пробы'),
        ),
    ]