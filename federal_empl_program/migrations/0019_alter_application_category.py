# Generated by Django 3.2.5 on 2021-09-23 06:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('federal_empl_program', '0018_alter_application_category'),
    ]

    operations = [
        migrations.AlterField(
            model_name='application',
            name='category',
            field=models.CharField(choices=[('EMPS', 'Граждане, ищущие работу и обратившиеся в органы службы занятости, включая безработных граждан'), ('JOBS', 'Ищущий работу'), ('UEMP', 'Безработный'), ('VACK', 'Женщины, находящиеся в отпуске по уходу за ребенком в возрасте до трех лет'), ('SCHK', 'Женщины, имеющие детей дошкольного возраста и не состоящие в трудовых отношениях'), ('50+', 'Граждане в возрасте 50-ти лет и старше'), ('SC', 'Граждане предпенсионного возраста')], default='EMPS', max_length=50, verbose_name='Категория слушателя'),
        ),
    ]
