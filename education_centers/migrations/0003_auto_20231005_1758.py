# Generated by Django 3.2.8 on 2023-10-05 13:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('education_centers', '0002_auto_20230826_1638'),
    ]

    operations = [
        migrations.AddField(
            model_name='educationprogram',
            name='flow_id',
            field=models.IntegerField(blank=True, null=True, verbose_name='Идентификатор flow'),
        ),
        migrations.AddField(
            model_name='group',
            name='flow_id',
            field=models.IntegerField(blank=True, null=True, verbose_name='Идентификатор flow'),
        ),
    ]