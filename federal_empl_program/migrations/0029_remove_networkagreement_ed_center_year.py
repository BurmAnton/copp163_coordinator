# Generated by Django 4.2.6 on 2024-02-14 08:26

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('federal_empl_program', '0028_remove_networkagreement_project_year_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='networkagreement',
            name='ed_center_year',
        ),
    ]
