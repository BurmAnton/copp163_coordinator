# Generated by Django 4.2.6 on 2024-01-27 14:41

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0009_alter_distributionemail_options_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='mailattachfile',
            name='attached_file',
        ),
        migrations.RemoveField(
            model_name='mailattachfile',
            name='name',
        ),
        migrations.RemoveField(
            model_name='mailattachfile',
            name='upload_date_time',
        ),
    ]
