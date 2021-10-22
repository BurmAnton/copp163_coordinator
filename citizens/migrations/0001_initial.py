# Generated by Django 3.2.8 on 2021-10-22 06:48

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('organizations', '__first__'),
    ]

    operations = [
        migrations.CreateModel(
            name='Citizen',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=30, null=True, verbose_name='Имя')),
                ('last_name', models.CharField(max_length=50, null=True, verbose_name='Фамилия')),
                ('middle_name', models.CharField(blank=True, max_length=30, null=True, verbose_name='Отчество')),
                ('sex', models.CharField(blank=True, choices=[('M', 'Мужской'), ('F', 'Женский')], max_length=1, null=True, verbose_name='Пол')),
                ('birthday', models.DateField(blank=True, null=True, verbose_name='Дата рождения')),
                ('email', models.EmailField(blank=True, max_length=320, null=True, verbose_name='Email')),
                ('phone_number', models.CharField(blank=True, max_length=16, null=True, verbose_name='Номер телефона')),
                ('snils_number', models.CharField(blank=True, max_length=11, null=True, verbose_name='Номер СНИЛС')),
                ('inn_number', models.CharField(blank=True, max_length=30, null=True, verbose_name='ИНН')),
                ('res_region', models.CharField(blank=True, max_length=50, null=True, verbose_name='Регион проживания')),
                ('res_city', models.CharField(blank=True, max_length=50, null=True, verbose_name='Населённый пункт')),
                ('res_disctrict', models.CharField(blank=True, max_length=50, null=True, verbose_name='Населённый пункт')),
                ('social_status', models.CharField(blank=True, choices=[('SCHT', 'Учитель в школе'), ('SCHS', 'Обучающиеся общеообразовательных организаций'), ('SSPO', 'студент СПО'), ('SVO', 'студент ВО'), ('EMP', 'Cотрудник предприятия'), ('SC', 'Гражданин предпенсионного возраста'), ('50+', 'Гражданин старше 50-ти лет'), ('UEMP', 'Безработный гражданин (статус ЦЗН)'), ('EMPS', 'Гражданин, ищущий работу (статус ЦЗН)'), ('OTHR', 'Другой')], max_length=4, null=True, verbose_name='Социальный статус')),
                ('education_type', models.CharField(blank=True, choices=[('SPO', 'СПО'), ('VO', 'ВО'), ('SSPO', 'Cтудент ВО'), ('SVO', 'Cтудент СПО'), ('11', '11 классов'), ('9', '9 классов'), ('OTHR', 'Другой')], max_length=4, null=True, verbose_name='Образование')),
                ('self_employed', models.BooleanField(default=False, verbose_name='Самозанятый')),
                ('is_employed', models.BooleanField(default=False, verbose_name='Трудоустроен')),
                ('is_verified', models.BooleanField(default=False, verbose_name='Верифицирован')),
                ('copp_registration', models.BooleanField(default=False, verbose_name='Зарегистрирован на copp63.ru')),
                ('disability_type', models.CharField(blank=True, choices=[('SPO', 'СПО'), ('VO', 'ВО'), ('SSPO', 'Cтудент ВО'), ('SVO', 'Cтудент СПО'), ('11', '11 классов'), ('9', '9 классов'), ('OTHR', 'Другой')], default=None, max_length=4, null=True, verbose_name='Инвалидность')),
            ],
            options={
                'verbose_name': 'Гражданин',
                'verbose_name_plural': 'Граждане',
            },
        ),
        migrations.CreateModel(
            name='School',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='Название школы')),
                ('specialty', models.CharField(blank=True, max_length=50, null=True, verbose_name='Уклон школы')),
                ('territorial_administration', models.CharField(blank=True, max_length=150, null=True, verbose_name='Тер. управление')),
                ('municipality', models.CharField(blank=True, max_length=200, null=True, verbose_name='Муниципалитет')),
                ('city', models.CharField(blank=True, max_length=100, null=True, verbose_name='Населённый пункт')),
                ('adress', models.CharField(blank=True, max_length=250, null=True, verbose_name='Адрес')),
                ('is_bilet', models.BooleanField(default=False, verbose_name='Есть педагог-навигатор')),
                ('inn', models.CharField(blank=True, max_length=20, null=True, verbose_name='ИНН')),
                ('school_coordinators', models.ManyToManyField(blank=True, related_name='coordinated_schools', to=settings.AUTH_USER_MODEL, verbose_name='Педагоги-навигаторы')),
            ],
            options={
                'verbose_name': 'Школа',
                'verbose_name_plural': 'Школы',
            },
        ),
        migrations.CreateModel(
            name='SchoolClass',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('grade_number', models.IntegerField(validators=[django.core.validators.MaxValueValidator(11), django.core.validators.MinValueValidator(1)], verbose_name='Номер класса')),
                ('grade_letter', models.CharField(max_length=4, verbose_name='Буква класса')),
                ('specialty', models.CharField(blank=True, max_length=50, null=True, verbose_name='Уклон класса')),
                ('school', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='classes', to='citizens.school', verbose_name='Школа')),
            ],
            options={
                'verbose_name': 'Класс',
                'verbose_name_plural': 'Классы',
            },
        ),
        migrations.CreateModel(
            name='Job',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('position', models.CharField(max_length=50, verbose_name='Должность')),
                ('start_date', models.DateField(verbose_name='Дата начала работы')),
                ('end_date', models.DateField(verbose_name='Дата окончания работы')),
                ('place_of_work', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='employees', to='organizations.company', verbose_name='Место работы')),
                ('worker', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='jobs', to='citizens.citizen')),
            ],
            options={
                'verbose_name': 'Работа',
                'verbose_name_plural': 'Работы',
            },
        ),
        migrations.AddField(
            model_name='citizen',
            name='school',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='students', to='citizens.school', verbose_name='Школа'),
        ),
        migrations.AddField(
            model_name='citizen',
            name='school_class',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='students', to='citizens.schoolclass', verbose_name='Школный класс'),
        ),
    ]
