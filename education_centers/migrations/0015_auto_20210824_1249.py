# Generated by Django 3.2.5 on 2021-08-24 08:49

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('education_centers', '0014_remove_schoolclass_students'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='schoolclass',
            name='school',
        ),
        migrations.DeleteModel(
            name='School',
        ),
        migrations.DeleteModel(
            name='SchoolClass',
        ),
    ]
