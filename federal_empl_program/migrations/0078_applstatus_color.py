# Generated by Django 4.2.6 on 2024-07-08 12:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('federal_empl_program', '0077_applstatus_order_alter_application_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='applstatus',
            name='color',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]
