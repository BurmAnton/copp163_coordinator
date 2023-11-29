# Generated by Django 4.2 on 2023-11-27 10:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_alter_user_role'),
        ('education_centers', '0005_abilimpicswinner'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='abilimpicswinner',
            options={'verbose_name': 'Участник Абилимпикс', 'verbose_name_plural': 'Участники Абилимпикс'},
        ),
        migrations.AddField(
            model_name='educationprogram',
            name='disability_types',
            field=models.ManyToManyField(blank=True, to='users.disabilitytype', verbose_name='ОВЗ'),
        ),
    ]