# Generated by Django 3.2.8 on 2023-07-05 08:05

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('citizens', '0006_remove_citizen_aplication_stages'),
        ('education_centers', '0049_auto_20230616_1519'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProjectYear',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('year', models.IntegerField(verbose_name='year')),
                ('programs', models.ManyToManyField(blank=True, related_name='project_years', to='education_centers.EducationProgram', verbose_name='Программы')),
            ],
            options={
                'verbose_name': 'Год проекта',
                'verbose_name_plural': 'Годы проекта',
            },
        ),
        migrations.CreateModel(
            name='ProjectPosition',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('position', models.CharField(max_length=50, verbose_name='Название позиции')),
                ('is_basis_needed', models.BooleanField(default=False, verbose_name='Нужно основание?')),
                ('project_year', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='positions', to='federal_empl_program.projectyear', verbose_name='Год проекта')),
            ],
            options={
                'verbose_name': 'Позиция в проекте',
                'verbose_name_plural': 'Позиции в проекте',
            },
        ),
        migrations.CreateModel(
            name='Indicator',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=500, verbose_name='Показатель эффективности')),
                ('is_free_form', models.BooleanField(default=False, verbose_name='Свободная форма?')),
                ('project_year', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='indicators', to='federal_empl_program.projectyear', verbose_name='Год проекта')),
            ],
            options={
                'verbose_name': 'Показатель эффективности',
                'verbose_name_plural': 'Показатели эффективности',
            },
        ),
        migrations.CreateModel(
            name='Grant',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('grant_name', models.CharField(max_length=100, verbose_name='Название')),
                ('qouta_72', models.IntegerField(default=0, verbose_name='Квота 72')),
                ('qouta_144', models.IntegerField(default=0, verbose_name='Квота 144')),
                ('qouta_256', models.IntegerField(default=0, verbose_name='Квота 256')),
                ('project_year', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='federal_empl_program.projectyear', verbose_name='Год проекта')),
            ],
            options={
                'verbose_name': 'Грант',
                'verbose_name_plural': 'Гранты',
            },
        ),
        migrations.CreateModel(
            name='EducationCenterProjectYear',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('appl_docs_link', models.TextField(default='', verbose_name='Ссылка на комп. документов')),
                ('stage', models.CharField(choices=[('FLLNG', 'заполнение'), ('FLLD', 'на проверке'), ('RWRK', 'отправлена на доработку'), ('VRFD', 'проверена'), ('FRMD', 'сформирована'), ('DWNLD', 'подгружена'), ('PRVD', 'принята')], default='FLLNG', max_length=5, verbose_name='Работа с заявкой')),
                ('step_1_check', models.BooleanField(default=False, verbose_name='Шаг 1. Проверка')),
                ('step_1_commentary', models.TextField(blank=True, default='', null=True, verbose_name='Шаг 1. Комментарий')),
                ('step_2_check', models.BooleanField(default=False, verbose_name='Шаг 2. Проверка')),
                ('step_2_commentary', models.TextField(blank=True, default='', null=True, verbose_name='Шаг 2. Комментарий')),
                ('step_3_check', models.BooleanField(default=False, verbose_name='Шаг 3. Проверка')),
                ('step_3_commentary', models.TextField(blank=True, default='', null=True, verbose_name='Шаг 3. Комментарий')),
                ('step_4_check', models.BooleanField(default=False, verbose_name='Шаг 4. Проверка')),
                ('step_4_commentary', models.TextField(blank=True, default='', null=True, verbose_name='Шаг 4. Комментарий')),
                ('step_5_check', models.BooleanField(default=False, verbose_name='Шаг 5. Проверка')),
                ('step_5_commentary', models.TextField(blank=True, default='', null=True, verbose_name='Шаг 5. Комментарий')),
                ('step_6_check', models.BooleanField(default=False, verbose_name='Шаг 6. Проверка')),
                ('step_6_commentary', models.TextField(blank=True, default='', null=True, verbose_name='Шаг 6. Комментарий')),
                ('is_federal', models.BooleanField(default=False, verbose_name='Федеральный центр')),
                ('ed_center', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='project_years', to='education_centers.educationcenter', verbose_name='Центр обучения')),
                ('project_year', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ed_centers', to='federal_empl_program.projectyear', verbose_name='Год проекта')),
            ],
            options={
                'verbose_name': 'Данные колледжа на год',
                'verbose_name_plural': 'Данные колледжей на годы',
            },
        ),
        migrations.CreateModel(
            name='EdCenterQuota',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quota_72', models.IntegerField(default=0, verbose_name='Квота 72ч')),
                ('quota_144', models.IntegerField(default=0, verbose_name='Квота 144ч')),
                ('quota_256', models.IntegerField(default=0, verbose_name='Квота 256ч')),
                ('ed_center_year', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='quota', to='federal_empl_program.educationcenterprojectyear', verbose_name='Центр обучения')),
            ],
            options={
                'verbose_name': 'Квота ЦО на год',
                'verbose_name_plural': 'Квота ЦО на годы',
            },
        ),
        migrations.CreateModel(
            name='EdCenterIndicator',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value_2021', models.CharField(max_length=25, verbose_name='Значение показателя (2021)')),
                ('value_2022', models.CharField(max_length=25, verbose_name='Значение показателя (2022)')),
                ('free_form_value', models.TextField(blank=True, default='', null=True, verbose_name='Значение (свободная форма)')),
                ('ed_center', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='indicators', to='education_centers.educationcenter', verbose_name='Центр обучения')),
                ('indicator', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ed_centers', to='federal_empl_program.indicator', verbose_name='Показатель')),
            ],
            options={
                'verbose_name': 'Показатель эффективности (ЦО)',
                'verbose_name_plural': 'Показатели эффективности (ЦО)',
            },
        ),
        migrations.CreateModel(
            name='EdCenterEmployeePosition',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('acts_basis', models.CharField(blank=True, max_length=500, null=True, verbose_name='Действует на основании')),
                ('ed_center', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='positions_employees', to='education_centers.educationcenter', verbose_name='Центр обучения')),
                ('employee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='positions', to='education_centers.employee', verbose_name='Сотрудник')),
                ('position', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='positions_employees', to='federal_empl_program.projectposition', verbose_name='Позиция')),
            ],
            options={
                'verbose_name': 'Роль сотрудника',
                'verbose_name_plural': 'Роли сотрудников',
            },
        ),
        migrations.CreateModel(
            name='CitizenCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('short_name', models.CharField(max_length=100, verbose_name='Название')),
                ('official_name', models.CharField(blank=True, max_length=500, verbose_name='Офицальное наименованние')),
                ('project_year', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='categories', to='federal_empl_program.projectyear', verbose_name='Год проекта')),
            ],
            options={
                'verbose_name': 'Категория граждан',
                'verbose_name_plural': 'Категории граждан',
            },
        ),
        migrations.CreateModel(
            name='Application',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('creation_date', models.DateTimeField(blank=True, default=django.utils.timezone.now, null=True, verbose_name='Дата создания')),
                ('appl_status', models.CharField(choices=[('NEW', 'Новая заявка'), ('ADM', 'Допущен'), ('SED', 'Начал обучение'), ('COMP', 'Завершил обучение'), ('NCOM', 'Заявка отменена'), ('DUPL', 'Дубликат')], default='NEW', max_length=4, verbose_name='Статус заявки')),
                ('change_status_date', models.DateTimeField(null=True, verbose_name='Дата последней смены статуса')),
                ('contract_type', models.CharField(choices=[('OLD', 'Трехсторонний договор со старым работодателем'), ('NEW', 'Трехсторонний договор с новым работодателем'), ('SELF', 'Двухсторонный договор'), ('NOT', 'Без договора'), ('–', '-')], default='–', max_length=4, verbose_name='Тип контракта')),
                ('is_working', models.BooleanField(default=False, verbose_name='Трудоустроен')),
                ('payment', models.CharField(blank=True, choices=[('DP', 'Не оплачен'), ('PF', 'Оплачен (100%)'), ('PP', 'Оплачен (70%)'), ('PFN', 'Оплачен (100%), НЦ'), ('PPN', 'Оплачен (70%), НЦ')], default='DP', max_length=3, null=True, verbose_name='Статус оплаты')),
                ('payment_amount', models.IntegerField(default=0, verbose_name='Оплата')),
                ('grant', models.CharField(blank=True, choices=[('1', 'Грант 1'), ('2', 'Грант 2')], default='1', max_length=2, null=True, verbose_name='Грант')),
                ('find_work', models.CharField(blank=True, choices=[('CONT', 'Заключил договор'), ('CERT', 'Предоставил справку о самозанятости'), ('VACS', 'Подобраны вакансии'), ('DFI', 'Направлен на собеседование'), ('INTD', 'Прошел собеседование'), ('GAJ', 'Трудоустроился'), ('SWRK', 'Сохранил работу'), ('CRIP', 'Предоставил справку ИП')], max_length=4, null=True, verbose_name='Трудоустройство')),
                ('applicant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='POE_applications', to='citizens.citizen', verbose_name='Заявитель')),
                ('citizen_category', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='application', to='federal_empl_program.citizencategory', verbose_name='категория')),
                ('competence', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='competence_applicants', to='education_centers.competence', verbose_name='Компетенция')),
                ('education_center', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='edcenter_applicants', to='education_centers.educationcenter', verbose_name='Центр обучения')),
                ('education_program', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='programm_applicants', to='education_centers.educationprogram', verbose_name='Програма обучения')),
                ('group', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='students', to='education_centers.group', verbose_name='Группа')),
                ('project_year', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='applications', to='federal_empl_program.projectyear', verbose_name='Год проекта')),
            ],
            options={
                'verbose_name': 'Заявка (Содействие занятости)',
                'verbose_name_plural': 'Заявки (Содействие занятости)',
            },
        ),
    ]