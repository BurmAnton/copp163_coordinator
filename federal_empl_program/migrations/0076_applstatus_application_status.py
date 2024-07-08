# Generated by Django 4.2.6 on 2024-07-08 10:50

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('federal_empl_program', '0075_application_atlas_id'),
    ]

    operations = [
        migrations.CreateModel(
            name='ApplStatus',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('short_name', models.CharField(max_length=50)),
                ('name', models.CharField(max_length=250, verbose_name='Название')),
            ],
            options={
                'verbose_name': 'Статус заявки',
                'verbose_name_plural': 'Статусы заявки',
            },
        ),
        migrations.AddField(
            model_name='application',
            name='status',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='application', to='federal_empl_program.applstatus', verbose_name='категория'),
        ),
    ]
