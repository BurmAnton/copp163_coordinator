# Generated by Django 4.2.6 on 2024-01-27 14:40

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0008_delete_partnercontact'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='distributionemail',
            options={},
        ),
        migrations.AlterModelOptions(
            name='partnercontactemail',
            options={},
        ),
        migrations.AlterModelOptions(
            name='partnercontactphone',
            options={},
        ),
        migrations.RemoveField(
            model_name='distributionemail',
            name='email',
        ),
        migrations.RemoveField(
            model_name='partnercontactemail',
            name='email',
        ),
        migrations.RemoveField(
            model_name='partnercontactphone',
            name='phone',
        ),
    ]