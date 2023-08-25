# Generated by Django 3.2.8 on 2023-08-25 09:38

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import education_centers.models


class Migration(migrations.Migration):

    replaces = [('education_centers', '0001_initial'), ('education_centers', '0002_alter_educationcentergroup_education_center'), ('education_centers', '0003_auto_20230330_1206'), ('education_centers', '0004_alter_educationcenter_contact_person'), ('education_centers', '0005_contractorsdocument'), ('education_centers', '0006_contractorsdocument_group'), ('education_centers', '0007_auto_20230403_1113'), ('education_centers', '0008_contractorsdocument_doc_stage'), ('education_centers', '0009_auto_20230403_1615'), ('education_centers', '0010_contractorsdocument_doc_type'), ('education_centers', '0011_auto_20230404_1226'), ('education_centers', '0012_bankdetails_educationcenterhead'), ('education_centers', '0013_auto_20230404_1448'), ('education_centers', '0014_alter_educationcenter_ed_license'), ('education_centers', '0015_auto_20230406_1213'), ('education_centers', '0016_auto_20230406_1326'), ('education_centers', '0017_alter_contractorsdocument_parent_doc'), ('education_centers', '0018_contractorsdocument_creation_date'), ('education_centers', '0019_auto_20230412_0938'), ('education_centers', '0020_auto_20230414_1253'), ('education_centers', '0021_auto_20230503_1136'), ('education_centers', '0022_auto_20230503_1254'), ('education_centers', '0023_employee_is_head'), ('education_centers', '0024_educationprogram_ed_center'), ('education_centers', '0025_auto_20230503_2136'), ('education_centers', '0026_auto_20230504_1015'), ('education_centers', '0027_auto_20230504_1032'), ('education_centers', '0028_workshop_equipment'), ('education_centers', '0029_auto_20230504_1114'), ('education_centers', '0030_auto_20230504_1116'), ('education_centers', '0031_auto_20230504_1116'), ('education_centers', '0032_remove_educationcenter_home_city'), ('education_centers', '0033_educationcenter_home_city'), ('education_centers', '0034_auto_20230504_1118'), ('education_centers', '0035_auto_20230504_1145'), ('education_centers', '0036_alter_workshop_programs'), ('education_centers', '0037_alter_workshop_adress'), ('education_centers', '0038_auto_20230505_1212'), ('education_centers', '0039_auto_20230510_1014'), ('education_centers', '0040_auto_20230515_1344'), ('education_centers', '0041_auto_20230515_1637'), ('education_centers', '0042_teacher_education_major'), ('education_centers', '0043_alter_teacher_position'), ('education_centers', '0044_auto_20230518_1017'), ('education_centers', '0045_educationprogram_is_bvb'), ('education_centers', '0046_auto_20230527_1845'), ('education_centers', '0047_teacher_bvb_experience'), ('education_centers', '0048_remove_group_education_project'), ('education_centers', '0049_auto_20230616_1519')]

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        #('citizens', '0005_auto_20230616_1519'),
    ]

    operations = [
        migrations.CreateModel(
            name='Competence',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=500, verbose_name='Название компетенции')),
                ('is_irpo', models.BooleanField(default=True, verbose_name='ИРПО?')),
                ('is_worldskills', models.BooleanField(default=True, verbose_name='ВС?')),
            ],
            options={
                'verbose_name': 'Компетенция',
                'verbose_name_plural': 'Компетенции',
            },
        ),
        migrations.CreateModel(
            name='EducationCenter',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=500, verbose_name='Название организации')),
                ('quota_1_72', models.IntegerField(default=0, verbose_name='Квота 72ч (Грант 1)')),
                ('quota_1_144', models.IntegerField(default=0, verbose_name='Квота 144ч (Грант 1)')),
                ('quota_1_256', models.IntegerField(default=0, verbose_name='Квота 256ч (Грант 1)')),
                ('quota_2_72', models.IntegerField(default=0, verbose_name='Квота 72ч (Грант 2)')),
                ('quota_2_144', models.IntegerField(default=0, verbose_name='Квота 144ч (Грант 2)')),
                ('quota_2_256', models.IntegerField(default=0, verbose_name='Квота 256ч (Грант 2)')),
                ('competences', models.ManyToManyField(blank=True, related_name='educationCenters', to='education_centers.Competence', verbose_name='Компетенции')),
                ('ed_license', models.TextField(blank=True, default='', null=True, verbose_name='Образовательная лизенция (серия, номер, дата, срок действия)')),
                ('legal_address', models.TextField(blank=True, null=True, verbose_name='Адрес места нахождения')),
                ('org_document', models.TextField(blank=True, null=True, verbose_name='Действует на основаннии:')),
                ('is_license', models.BooleanField(default=False, verbose_name='Есть обр. лизенция?')),
                ('entity_sex', models.CharField(blank=True, choices=[('ML', 'Мужской'), ('M', 'Женский'), ('N', 'Средний')], max_length=4, null=True, verbose_name='Род для юр. лица')),
                ('is_ndc', models.BooleanField(default=False, verbose_name='Платит НДС?')),
                ('license_issued_by', models.TextField(blank=True, default='', null=True, verbose_name='Кем выдана обр. лизенция (творический падеж)')),
                ('contact_person', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='education_centers', to=settings.AUTH_USER_MODEL, verbose_name='Контактное лицо')),
                ('none_ndc_reason', models.CharField(blank=True, default='', max_length=500, null=True, verbose_name='Основание работы без НДС')),
                ('short_name', models.CharField(blank=True, default='', max_length=500, null=True, verbose_name='Краткое название организации')),
                ('short_name_r', models.CharField(blank=True, default='', max_length=500, null=True, verbose_name='Краткое название организации (род.)')),
                ('home_city', models.CharField(blank=True, default='', max_length=150, null=True, verbose_name='Город')),
            ],
            options={
                'verbose_name': 'Центр обучения',
                'verbose_name_plural': 'Центры обучения',
            },
        ),
        migrations.CreateModel(
            name='EducationProgram',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('program_name', models.CharField(max_length=500, verbose_name='Название программы')),
                ('program_type', models.CharField(blank=True, choices=[('DPOPK', 'ДПО ПК'), ('DPOPP', 'ДПО ПП'), ('POP', 'ПО П'), ('POPP', 'ПО ПП'), ('POPK', 'ПО ПК')], max_length=5, null=True, verbose_name='Тип программы')),
                ('duration', models.IntegerField(blank=True, verbose_name='Длительность (ак. часов)')),
                ('program_link', models.CharField(blank=True, max_length=200, null=True, verbose_name='Ссылка на программу')),
                ('competence', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='programs', to='education_centers.competence', verbose_name='Компетенция')),
                ('description', models.TextField(blank=True, null=True, verbose_name='Описание программы')),
                ('education_form', models.CharField(blank=True, choices=[('PRTLN', 'Очно-заочная с применением ДОТ'), ('FLLLN', 'Очная с применением ДОТ '), ('PRT', 'Очно-заочная'), ('FLL', 'Очная')], max_length=5, null=True, verbose_name='Форма обучения')),
                ('entry_requirements', models.CharField(blank=True, choices=[('NDC', 'Без образования'), ('SPO', 'Среднее профессиональное образование')], max_length=4, null=True, verbose_name='Входные требования')),
                ('notes', models.TextField(blank=True, null=True, verbose_name='Примечания')),
                ('profession', models.CharField(blank=True, max_length=200, null=True, verbose_name='Профессия')),
                ('ed_center', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='programs', to='education_centers.educationcenter', verbose_name='Центр обучения')),
            ],
            options={
                'verbose_name': 'Программа',
                'verbose_name_plural': 'Программы',
            },
        ),
        migrations.CreateModel(
            name='Workshop',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('adress', models.CharField(blank=True, max_length=200, null=True, verbose_name='Адрес')),
                ('competence', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='workshops', to='education_centers.competence', verbose_name='Компетенция')),
                ('education_center', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='workshops', to='education_centers.educationcenter', verbose_name='Центр обучения')),
                ('classes_type', models.CharField(blank=True, choices=[('T', 'Теоретические занятия'), ('P', 'Практические занятия'), ('TP', 'Практические и теоретические занятия')], max_length=4, null=True, verbose_name='Вид занятий')),
                ('name', models.CharField(blank=True, max_length=500, null=True, verbose_name='Название мастерской')),
                ('equipment', models.TextField(blank=True, null=True, verbose_name='Оборудование')),
                ('programs', models.ManyToManyField(blank=True, related_name='workshops', to='education_centers.EducationProgram', verbose_name='программы')),
            ],
            options={
                'verbose_name': 'Мастерская',
                'verbose_name_plural': 'Мастерские',
            },
        ),
        migrations.CreateModel(
            name='Group',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, verbose_name='Номер группы')),
                ('start_date', models.DateField(blank=True, null=True, verbose_name='Дата начала обучения')),
                ('end_date', models.DateField(blank=True, null=True, verbose_name='Дата окончания обучения')),
                ('distance_education', models.BooleanField(default=False, verbose_name='Дистанционное обучение')),
                ('mixed_education', models.BooleanField(default=False, verbose_name='Смешанное обучение')),
                ('is_new_price', models.BooleanField(default=False, verbose_name='Новая цена')),
                ('education_program', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='groups', to='education_centers.educationprogram', verbose_name='Программа обучения')),
                ('workshop', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='groups', to='education_centers.workshop', verbose_name='мастерская')),
                ('group_status', models.CharField(choices=[('NEW', 'Создана'), ('SED', 'В процессе обучения'), ('COMP', 'Завершила обучение'), ('NCOM', 'Отменена')], default='NEW', max_length=4, verbose_name='Статус заявки')),
            ],
            options={
                'verbose_name': 'Группа',
                'verbose_name_plural': 'Группы',
            },
        ),
        migrations.CreateModel(
            name='DocumentType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=150, null=True, verbose_name='Тип документа')),
                ('stage', models.CharField(choices=[('GRMNT', 'Договорные'), ('CLS', 'Закрывающие'), ('PRV', 'Подтверждающие')], max_length=6, verbose_name='Этап')),
                ('template', models.FileField(upload_to=education_centers.models.DocumentType.template_directory_path, verbose_name='Документ')),
            ],
            options={
                'verbose_name': 'Шаблон документов',
                'verbose_name_plural': 'Шаблоны документов',
            },
        ),
        migrations.CreateModel(
            name='ContractorsDocument',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('doc_file', models.FileField(upload_to=education_centers.models.ContractorsDocument.doc_directory_path, verbose_name='Документ')),
                ('contractor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ed_center_documents', to='education_centers.educationcenter', verbose_name='подрядчик')),
                ('groups', models.ManyToManyField(related_name='group_documents', to='education_centers.Group', verbose_name='группы')),
                ('doc_stage', models.CharField(choices=[('CRTD', 'Создан'), ('CHCKD', 'Проверен'), ('SGND', 'Подписан'), ('SGNDAP', 'Подписан и проверен')], default='CRTD', max_length=6, verbose_name='Стадия')),
                ('doc_type', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='education_centers.documenttype', verbose_name='Тип документа')),
                ('parent_doc', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='children_docs', to='education_centers.contractorsdocument', verbose_name='Родительский документ')),
                ('register_number', models.IntegerField(default=1, verbose_name='Номер в реестре')),
                ('creation_date', models.DateTimeField(blank=True, default=django.utils.timezone.now, null=True, verbose_name='Дата создания')),
            ],
            options={
                'verbose_name': 'Документ с подрядчиком',
                'verbose_name_plural': 'Документы с подрядчиками',
            },
        ),
        migrations.CreateModel(
            name='BankDetails',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ogrn', models.CharField(max_length=25, verbose_name='ОГРН')),
                ('account_number', models.CharField(max_length=25, verbose_name='Расчётный счёт')),
                ('biс', models.CharField(max_length=25, verbose_name='БИК')),
                ('corr_account', models.CharField(max_length=25, verbose_name='К/сч')),
                ('phone', models.CharField(max_length=120, verbose_name='Телефон(-ы)')),
                ('email', models.EmailField(max_length=254, unique=True, verbose_name='email address')),
                ('organization', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='bank_details', to='education_centers.educationcenter', verbose_name='Организация')),
                ('inn', models.CharField(default=123, max_length=25, verbose_name='ИНН')),
                ('kpp', models.CharField(default=123, max_length=25, verbose_name='КПП')),
                ('accountant', models.CharField(blank=True, max_length=250, null=True, verbose_name='Главный бухгалтер')),
                ('bank', models.CharField(default='Банк', max_length=250, verbose_name='Банк')),
                ('legal_address', models.CharField(default='445007, Самарская область, г. Тольятти , улица Победы, влд. 7', max_length=500, verbose_name='Юридический адрес')),
                ('mail_address', models.CharField(default='445007, Самарская область, г. Тольятти , улица Победы, влд. 7', max_length=500, verbose_name='Почтовый адрес')),
                ('okpo', models.CharField(default=43504248, max_length=25, verbose_name='ОКПО')),
                ('oktmo', models.CharField(default=63.11, max_length=25, verbose_name='ОКТМО')),
                ('okved', models.CharField(max_length=250, verbose_name='ОКВЭД')),
                ('other', models.TextField(blank=True, null=True, verbose_name='Другие реквизиты')),
                ('bank_inn', models.CharField(blank=True, max_length=25, null=True, verbose_name='Банк ИНН')),
                ('bank_kpp', models.CharField(blank=True, max_length=25, null=True, verbose_name='Банк КПП')),
                ('personal_account_number', models.CharField(blank=True, max_length=25, null=True, verbose_name='Лицевой счёт')),
            ],
            options={
                'verbose_name': 'Реквизиты организации',
                'verbose_name_plural': 'Реквизиты организаций',
            },
        ),
        migrations.CreateModel(
            name='Employee',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=30, verbose_name='Имя')),
                ('middle_name', models.CharField(blank=True, max_length=30, null=True, verbose_name='Отчество')),
                ('last_name', models.CharField(max_length=30, verbose_name='Фамилия')),
                ('position', models.CharField(max_length=150, verbose_name='Должность')),
                ('first_name_r', models.CharField(max_length=30, verbose_name='Имя (род)')),
                ('middle_name_r', models.CharField(blank=True, max_length=30, null=True, verbose_name='Отчество (род)')),
                ('last_name_r', models.CharField(max_length=30, verbose_name='Фамилия (род)')),
                ('position_r', models.CharField(max_length=150, verbose_name='Должность (род)')),
                ('phone', models.CharField(max_length=120, verbose_name='Телефон(-ы)')),
                ('email', models.EmailField(max_length=254, verbose_name='email address')),
                ('organization', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='employees', to='education_centers.educationcenter', verbose_name='Организация')),
                ('is_head', models.BooleanField(default=False, verbose_name='Руководитель организации?')),
            ],
            options={
                'verbose_name': 'Сотрудник (контрагента)',
                'verbose_name_plural': 'Сотрудники (контрагента)',
            },
        ),
        migrations.CreateModel(
            name='Teacher',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=30, verbose_name='Имя')),
                ('middle_name', models.CharField(blank=True, max_length=30, null=True, verbose_name='Отчество')),
                ('last_name', models.CharField(max_length=30, verbose_name='Фамилия')),
                ('employment_type', models.CharField(blank=True, choices=[('STFF', 'Штатный педагогический сотрудник'), ('TTRC', 'Привлеченный педагогический работник')], max_length=4, null=True, verbose_name='Тип трудоустройства')),
                ('education_level', models.CharField(blank=True, choices=[('VO', 'Высшее образование'), ('SPO', 'Среднее профессиональное образование')], max_length=4, null=True, verbose_name='Уровень образования')),
                ('experience', models.TextField(blank=True, null=True, verbose_name='Наличие опыта')),
                ('organization', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='teachers', to='education_centers.educationcenter', verbose_name='Организация')),
                ('additional_education', models.TextField(blank=True, null=True, verbose_name='Наличие доп. проф. образования по профилю программы за последние 3 года')),
                ('programs', models.ManyToManyField(related_name='teachers', to='education_centers.EducationProgram', verbose_name='программы')),
                ('position', models.CharField(blank=True, max_length=150, null=True, verbose_name='Ученая степень/должность')),
                ('education_major', models.CharField(blank=True, max_length=150, null=True, verbose_name='Специальность')),
                ('bvb_experience', models.TextField(blank=True, null=True, verbose_name='Наличие профессиональных сертификаций')),
            ],
            options={
                'verbose_name': 'Педагог',
                'verbose_name_plural': 'Педагоги',
            },
        ),
    ]
