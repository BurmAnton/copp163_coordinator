# Generated by Django 3.2.5 on 2021-08-16 09:39

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('federal_empl_program', '0005_application_test'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='application',
            name='for_inline',
        ),
        migrations.RemoveField(
            model_name='application',
            name='test',
        ),
    ]