# Generated by Django 4.2.6 on 2024-03-03 13:48

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('federal_empl_program', '0041_remove_irpoprogram_profstandarts_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='profstandart',
            options={'verbose_name': 'Профстандарт', 'verbose_name_plural': 'Профстандарты'},
        ),
        migrations.RemoveField(
            model_name='irpoprogram',
            name='prof_activity_type',
        ),
        migrations.RemoveField(
            model_name='irpoprogram',
            name='prof_field',
        ),
        migrations.AddField(
            model_name='profstandart',
            name='prof_activity_type',
            field=models.CharField(blank=True, max_length=250, null=True, verbose_name='Вид профессиональной деятельности'),
        ),
        migrations.AddField(
            model_name='profstandart',
            name='prof_field',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='irpo_programs', to='federal_empl_program.proffield', verbose_name='Область профессиональной деятельности'),
        ),
    ]
