# Generated by Django 4.2.6 on 2024-03-28 10:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('federal_empl_program', '0070_remove_irpoprogram_exam_consultations_duration_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='citizenapplication',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default="2024-01-01 00:00"),
            preserve_default=False,
        ),
    ]