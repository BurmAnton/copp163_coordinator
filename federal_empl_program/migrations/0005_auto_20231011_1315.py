# Generated by Django 3.2.8 on 2023-10-11 09:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('federal_empl_program', '0004_auto_20231009_1437'),
    ]

    operations = [
        migrations.AddField(
            model_name='educationcenterprojectyear',
            name='quota_144',
            field=models.IntegerField(default=0, verbose_name='Квота 144'),
        ),
        migrations.AddField(
            model_name='educationcenterprojectyear',
            name='quota_256',
            field=models.IntegerField(default=0, verbose_name='Квота 256'),
        ),
        migrations.AddField(
            model_name='educationcenterprojectyear',
            name='quota_72',
            field=models.IntegerField(default=0, verbose_name='Квота 72'),
        ),
    ]