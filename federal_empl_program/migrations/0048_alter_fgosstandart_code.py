# Generated by Django 4.2.6 on 2024-03-03 14:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('federal_empl_program', '0047_remove_fgosstandart_prof_field'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fgosstandart',
            name='code',
            field=models.CharField(max_length=20, verbose_name='Код ПС'),
        ),
    ]
