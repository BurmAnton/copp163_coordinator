# Generated by Django 4.2 on 2023-11-30 06:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('federal_empl_program', '0008_application_price'),
    ]

    operations = [
        migrations.AddField(
            model_name='application',
            name='added_to_act',
            field=models.BooleanField(default=False, verbose_name='Трудоустроен'),
        ),
    ]