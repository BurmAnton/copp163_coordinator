# Generated by Django 4.2.6 on 2024-01-27 14:26

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('regions', '0003_alter_organization_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='CityType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='Название')),
                ('short_name', models.CharField(max_length=15, verbose_name='Сокращение')),
            ],
            options={
                'verbose_name': 'Тип населённого пункта',
                'verbose_name_plural': 'Типы населённых пунктов',
            },
        ),
        migrations.CreateModel(
            name='Region',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='Название субъекта')),
            ],
            options={
                'verbose_name': 'Субъект РФ',
                'verbose_name_plural': 'Субъекты РФ',
            },
        ),
        migrations.CreateModel(
            name='TerAdministration',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='Тер. управление')),
                ('region', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ter_administrations', to='regions.region', verbose_name='Субъект Российской Федерации')),
            ],
            options={
                'verbose_name': 'Тер. управление',
                'verbose_name_plural': 'Тер. управления',
            },
        ),
        migrations.CreateModel(
            name='City',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='Название')),
                ('city_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='cities', to='regions.citytype', verbose_name='Тип населённого пункта')),
                ('region', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='cities', to='regions.region', verbose_name='Субъект Российской Федерации')),
            ],
            options={
                'verbose_name': 'Населённый пункт',
                'verbose_name_plural': 'Населённые пункты',
            },
        ),
    ]
