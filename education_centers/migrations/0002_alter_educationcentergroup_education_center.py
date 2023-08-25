# Generated by Django 3.2.8 on 2023-03-30 07:57

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('education_centers', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='educationcentergroup',
            name='education_center',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='ed_center_groups', to='education_centers.educationcenter', verbose_name='Центр обучения'),
        ),
    ]
