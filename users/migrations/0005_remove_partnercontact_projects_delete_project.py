# Generated by Django 4.2.6 on 2024-01-27 14:36

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_alter_user_role'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='partnercontact',
            name='projects',
        ),
        migrations.DeleteModel(
            name='Project',
        ),
    ]
