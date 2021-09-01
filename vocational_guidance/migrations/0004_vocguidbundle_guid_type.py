# Generated by Django 3.2.5 on 2021-08-30 13:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vocational_guidance', '0003_auto_20210830_1755'),
    ]

    operations = [
        migrations.AddField(
            model_name='vocguidbundle',
            name='guid_type',
            field=models.CharField(blank=True, choices=[('SPO', 'Моя Россия'), ('VO', 'Онлайн')], max_length=4, null=True, verbose_name='Тип проб'),
        ),
    ]