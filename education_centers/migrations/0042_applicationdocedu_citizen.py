# Generated by Django 4.2.6 on 2024-11-05 05:32

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('citizens', '0001_squashed_0006_remove_citizen_aplication_stages'),
        ('education_centers', '0041_alter_applicationdocedu_passport_issued_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='applicationdocedu',
            name='citizen',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='application_docs', to='citizens.citizen', verbose_name='Гражданин'),
        ),
    ]
