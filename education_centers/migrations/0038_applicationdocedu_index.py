# Generated by Django 4.2.6 on 2024-11-05 03:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('education_centers', '0037_applicationdocedu_signed_file'),
    ]

    operations = [
        migrations.AddField(
            model_name='applicationdocedu',
            name='index',
            field=models.CharField(blank=True, max_length=20, null=True, verbose_name='Почтовый индекс'),
        ),
    ]
