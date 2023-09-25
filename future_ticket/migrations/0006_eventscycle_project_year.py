# Generated by Django 3.2.8 on 2023-09-19 09:52

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('future_ticket', '0005_auto_20230919_1320'),
    ]

    operations = [
        migrations.AddField(
            model_name='eventscycle',
            name='project_year',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='events_cycles', to='future_ticket.ticketprojectyear', verbose_name='Год проекта (БВБ)'),
            preserve_default=False,
        ),
    ]