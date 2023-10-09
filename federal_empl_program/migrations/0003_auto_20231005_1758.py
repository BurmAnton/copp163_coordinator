# Generated by Django 3.2.8 on 2023-10-05 13:58

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('federal_empl_program', '0002_delete_edcenterquota'),
    ]

    operations = [
        migrations.AddField(
            model_name='application',
            name='csn_prv_date',
            field=models.DateField(blank=True, null=True, verbose_name='Дата одобрения ЦЗН'),
        ),
        migrations.AddField(
            model_name='application',
            name='flow_id',
            field=models.IntegerField(blank=True, null=True, verbose_name='Номер заявки'),
        ),
        migrations.CreateModel(
            name='FlowStatus',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('off_name', models.CharField(max_length=100, verbose_name='Название с flow')),
                ('name', models.CharField(max_length=100, verbose_name='Название')),
                ('action', models.TextField(verbose_name='Что делать?')),
                ('is_parent', models.BooleanField(default=False, verbose_name='Верхнеуровневый статус')),
                ('is_rejected', models.BooleanField(default=False, verbose_name='Отказной статус')),
                ('parent_status', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='children_statuses', to='federal_empl_program.flowstatus', verbose_name='Родительский статус')),
            ],
            options={
                'verbose_name': 'Статус flow',
                'verbose_name_plural': 'Статусы flow',
            },
        ),
        migrations.AddField(
            model_name='application',
            name='flow_status',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='applications', to='federal_empl_program.flowstatus', verbose_name='Статус (2023)'),
        ),
    ]
