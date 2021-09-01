# Generated by Django 3.2.5 on 2021-08-30 15:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('citizens', '0007_citizen_birthday'),
        ('vocational_guidance', '0004_vocguidbundle_guid_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='vocguidbundle',
            name='participants',
            field=models.ManyToManyField(related_name='voc_guid_bundles', to='citizens.Citizen', verbose_name='Участники'),
        ),
        migrations.AlterField(
            model_name='vocguidgroup',
            name='participants',
            field=models.ManyToManyField(related_name='voc_guid_groups', to='citizens.Citizen', verbose_name='Участники'),
        ),
    ]