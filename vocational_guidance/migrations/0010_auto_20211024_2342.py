# Generated by Django 3.2.8 on 2021-10-24 19:42

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vocational_guidance', '0009_vocguidassessment'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='vocguidassessment',
            options={'verbose_name': 'Ассесмент', 'verbose_name_plural': 'Ассесмент'},
        ),
        migrations.AddField(
            model_name='timeslot',
            name='participants_count',
            field=models.IntegerField(default=0, validators=[django.core.validators.MaxValueValidator(8), django.core.validators.MinValueValidator(0)], verbose_name='Колво участников'),
        ),
        migrations.RemoveField(
            model_name='timeslot',
            name='group',
        ),
        migrations.AddField(
            model_name='timeslot',
            name='group',
            field=models.ManyToManyField(blank=True, related_name='slots', to='vocational_guidance.VocGuidGroup', verbose_name='Группы'),
        ),
    ]
