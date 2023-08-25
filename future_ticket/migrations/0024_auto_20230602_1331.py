# Generated by Django 3.2.8 on 2023-06-02 09:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('future_ticket', '0023_auto_20230602_1056'),
    ]

    operations = [
        migrations.AddField(
            model_name='educationcenterticketprojectyear',
            name='is_ndc',
            field=models.BooleanField(default=False, verbose_name='Платит НДС?'),
        ),
        migrations.AddField(
            model_name='educationcenterticketprojectyear',
            name='none_ndc_reason',
            field=models.CharField(blank=True, default='', max_length=500, null=True, verbose_name='Основание работы без НДС'),
        ),
    ]
