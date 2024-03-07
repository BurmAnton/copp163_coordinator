# Generated by Django 4.2.6 on 2024-03-03 14:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('federal_empl_program', '0042_alter_profstandart_options_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='proffield',
            options={'verbose_name': 'область проф. деятельности', 'verbose_name_plural': 'Области проф. деятельности'},
        ),
        migrations.AlterField(
            model_name='profstandart',
            name='code',
            field=models.CharField(max_length=20, verbose_name='Код ПС'),
        ),
    ]
