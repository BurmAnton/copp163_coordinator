# Generated by Django 3.2.5 on 2021-08-16 09:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('organizations', '0003_alter_vacancy_company'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vacancy',
            name='job_title',
            field=models.CharField(default='', max_length=50, verbose_name='Имя'),
        ),
    ]
