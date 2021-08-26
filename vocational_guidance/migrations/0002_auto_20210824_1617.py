# Generated by Django 3.2.5 on 2021-08-24 12:17

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('citizens', '0006_auto_20210824_1248'),
        ('education_centers', '0015_auto_20210824_1249'),
        ('vocational_guidance', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='vocguidbundle',
            options={'verbose_name': 'Бандл', 'verbose_name_plural': 'Бандлы'},
        ),
        migrations.AddField(
            model_name='vocguidbundle',
            name='education_center',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='education_centers.educationcenter', verbose_name='Организатор'),
        ),
        migrations.AddField(
            model_name='vocguidbundle',
            name='workshop',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='education_centers.workshop', verbose_name='Место проведения'),
        ),
        migrations.AlterField(
            model_name='vocguidgroup',
            name='participants',
            field=models.ManyToManyField(related_name='voc_guid_group', to='citizens.Citizen', verbose_name='Участники'),
        ),
    ]
