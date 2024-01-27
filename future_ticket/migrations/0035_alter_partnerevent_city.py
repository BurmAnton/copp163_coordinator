# Generated by Django 4.2.6 on 2024-01-27 17:56

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('regions', '0005_delete_organization'),
        ('future_ticket', '0034_partnerevent_partner'),
    ]

    operations = [
        migrations.AlterField(
            model_name='partnerevent',
            name='city',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='events', to='regions.city', verbose_name='Населённый пункт'),
        ),
    ]