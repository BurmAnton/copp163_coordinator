# Generated by Django 3.2.8 on 2023-09-20 15:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('future_ticket', '0012_ticketquota_free_quota'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ticketquota',
            name='free_quota',
            field=models.IntegerField(blank=True, verbose_name='Свободная квота'),
        ),
    ]
