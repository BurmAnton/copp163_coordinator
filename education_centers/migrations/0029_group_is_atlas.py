# Generated by Django 4.2.6 on 2024-07-04 11:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('education_centers', '0028_group_education_center'),
    ]

    operations = [
        migrations.AddField(
            model_name='group',
            name='is_atlas',
            field=models.BooleanField(default=False, verbose_name='Атлас?'),
        ),
    ]