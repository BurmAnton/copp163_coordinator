# Generated by Django 3.2.8 on 2021-10-23 18:21

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('vocational_guidance', '0004_alter_vocguidtest_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='timeslot',
            name='test',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='vocational_guidance.vocguidtest', verbose_name='Пробы'),
        ),
    ]