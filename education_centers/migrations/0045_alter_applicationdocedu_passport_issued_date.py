# Generated by Django 4.2.6 on 2024-11-05 05:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('education_centers', '0044_applicationdocedu_status_doc'),
    ]

    operations = [
        migrations.AlterField(
            model_name='applicationdocedu',
            name='passport_issued_date',
            field=models.DateTimeField(null=True, verbose_name='Дата выдачи паспорта'),
        ),
    ]
