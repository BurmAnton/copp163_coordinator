# Generated by Django 4.2.6 on 2024-03-03 22:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('federal_empl_program', '0051_remove_irpoprogram_activities_activitytype_program'),
    ]

    operations = [
        migrations.AddField(
            model_name='activitycompetence',
            name='function_code',
            field=models.CharField(default=1, max_length=20, verbose_name='Код'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='activitycompetence',
            name='function_name',
            field=models.CharField(default=1, max_length=350, verbose_name='Наименование'),
            preserve_default=False,
        ),
    ]