# Generated by Django 4.2.6 on 2024-01-27 15:07

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0013_delete_mailattachfile'),
    ]

    operations = [
        migrations.DeleteModel(
            name='DistributionEmail',
        ),
    ]
