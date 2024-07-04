# Generated by Django 4.2.6 on 2024-07-04 10:41

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('education_centers', '0027_educationprogram_is_atlas'),
    ]

    operations = [
        migrations.AddField(
            model_name='group',
            name='education_center',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='groups', to='education_centers.educationcenter', verbose_name='Центр обучения'),
        ),
    ]
