# Generated by Django 3.2.8 on 2023-09-20 15:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('future_ticket', '0009_auto_20230920_1913'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ticketquota',
            name='free_quota',
            field=models.IntegerField(verbose_name='Свободная квота'),
        ),
    ]