# Generated by Django 4.2.6 on 2024-03-03 14:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('federal_empl_program', '0043_alter_proffield_options_alter_profstandart_code'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profstandart',
            name='prof_activity_type',
            field=models.CharField(blank=True, max_length=350, null=True, verbose_name='Вид профессиональной деятельности'),
        ),
    ]