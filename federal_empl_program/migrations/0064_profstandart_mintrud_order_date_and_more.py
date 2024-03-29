# Generated by Django 4.2.6 on 2024-03-11 17:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('federal_empl_program', '0063_alter_activitycompetenceequipment_competencies'),
    ]

    operations = [
        migrations.AddField(
            model_name='profstandart',
            name='mintrud_order_date',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='Приказ Минтруда России (дата)'),
        ),
        migrations.AddField(
            model_name='profstandart',
            name='mintrud_order_number',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='Приказ Минтруда России\t(номер)'),
        ),
        migrations.AddField(
            model_name='profstandart',
            name='minust_order_date',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='Приказ Минюста России (дата)'),
        ),
        migrations.AddField(
            model_name='profstandart',
            name='minust_order_number',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='Приказ Минюста России\t(номер)'),
        ),
        migrations.AlterField(
            model_name='irpoprogram',
            name='education_form',
            field=models.CharField(blank=True, choices=[('FLL', 'очная'), ('PRT', 'очно-заочная'), ('PRTF', 'Заочная'), ('PRTLN', 'очно-заочная'), ('FLLLN', 'очная')], max_length=5, null=True, verbose_name='Форма обучения'),
        ),
    ]
