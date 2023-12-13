# Generated by Django 4.2.6 on 2023-12-11 11:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('federal_empl_program', '0012_closingdocument_bill_date'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='closingdocument',
            name='bill_date',
        ),
        migrations.AddField(
            model_name='closingdocument',
            name='bill_id',
            field=models.DateField(blank=True, null=True, verbose_name='Номер счёта'),
        ),
    ]