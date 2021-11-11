from datetime import timedelta, date
from django.db.models import Count
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.db import IntegrityError

from education_centers.models import EducationCenter

from .forms import ImportDataForm
from .imports import bvb_teachers, slots_import

from users.models import User, Group
from citizens.models import Citizen, DisabilityType, School, SchoolClass
from .models import TimeSlot, VocGuidTest, VocGuidGroup, VocGuidAssessment, TestContact, BiletDistribution

# Create your views here.
@login_required(login_url='bilet/login')
def index(request):
    school_group = Group.objects.get(name='Школьник')
    coordinator_group = Group.objects.get(name='Координатор')
    if len(User.objects.filter(groups=school_group, email=request.user.email)) != 0:
        citizen = Citizen.objects.filter(
            email=request.user.email,
        )
        if len(citizen) != 0:
            citizen = citizen[0]
        else:
            return HttpResponseRedirect(reverse('signout'))
        return HttpResponseRedirect(reverse('profile', args=(citizen.id,)))
    elif len(User.objects.filter(groups=coordinator_group, email=request.user.email)) != 0:
        user = User.objects.filter(email=request.user.email)
        school = School.objects.filter(school_coordinators=user[0].id)
        return HttpResponseRedirect(reverse("school_dash", args=(school[0].id,)))
    elif request.user.is_stuff:
        return HttpResponseRedirect(reverse("bilet_dashboard"))
    return HttpResponseRedirect(reverse("index"))
    #school_dash(school.id)
    #ed_center_dash(ed_center.id)
    #region_dash()

@login_required
def students_dashboard(request):
    
    slots = TimeSlot.objects.exclude(report_link=None).order_by('test', 'slot')
    assessments = VocGuidAssessment.objects.filter(attendance=True, slot__in=slots)
    slots_lists = []
    for slot in slots:
        slots_list = []
        slots_list.append(slot.test.education_center.name)
        slots_list.append(slot.test.name)
        slots_list.append(slot.date)
        if slot.slot == "MRN":
            slots_list.append("10:00")
            slots_list.append("11:30")
        elif slot.slot == "MID":
            slots_list.append("15:00")
            slots_list.append("16:30")
        else:
            slots_list.append("16:30")
            slots_list.append("18:00")
        slots_list.append("Онлайн")
        contract = TestContact.objects.filter(test=slot.test)
        if len(contract) != 0:
            slots_list.append(slot.test.contact.full_name)
        else:
            slots_list.append("–")
        slots_list.append(8)
        slots_list.append(slot.test.description)
        if len(contract) != 0:
            slots_list.append(slot.test.contact.full_name)
        else:
            slots_list.append("–")
        slots_list.append("–")
        slots_list.append(slot.test.get_thematic_env_display)
        slots_list.append(90)
        slots_lists.append(slots_list)
    
    return render(request, "vocational_guidance/dashboard_students.html", {
        'assessments': assessments,
        'slots': slots_lists
    })

def bilet_dashboard(request):
    assessments = VocGuidAssessment.objects.filter(attendance=True)
    slots_count = TimeSlot.objects.filter(assessments__in=assessments)
    slots_count_link = TimeSlot.objects.filter(assessments__in=assessments).exclude(report_link=None)
    count_assessments = len(assessments)
    unique_assessments = assessments.values('participant').distinct()

    tests = VocGuidTest.objects.all()
    ed_centers = EducationCenter.objects.filter(voc_guid_sessions__in=tests)
    #Подсчёт квоты по каждому центру и пробе
    tests_dict = {}
    for center in ed_centers:
        tests_dict[center.name] = {}
        tests_dict[center.name]['count'] = 0
    for test in tests:
        tests_dict[test.education_center.name][f"{test.name} ({test.id})"] = [0, 0, 0, 0]
    for assessment in assessments:
        tests_dict[assessment.test.education_center.name][f"{assessment.test.name} ({assessment.test.id})"][0] += 1
        if assessment.slot.slot == 'MRN':
            tests_dict[assessment.test.education_center.name][f"{assessment.test.name} ({assessment.test.id})"][1] += 1
        elif assessment.slot.slot == 'MID':
            tests_dict[assessment.test.education_center.name][f"{assessment.test.name} ({assessment.test.id})"][2] += 1
        else:
            tests_dict[assessment.test.education_center.name][f"{assessment.test.name} ({assessment.test.id})"][3] += 1 
        tests_dict[assessment.test.education_center.name]['count'] += 1
    
    return render(request, "vocational_guidance/dashboard.html", {
        'count_assessments': count_assessments,
        'count_unique_assessments': len(unique_assessments),
        'count_quota': int(count_assessments/2),
        'tests_dict': tests_dict,
        'slots_count': len(slots_count),
        "slots_count_link": len(slots_count_link)
    })

@login_required(login_url='bilet/login/')
def profile(request, citizen_id):
    citizen = Citizen.objects.get(id=citizen_id)
    school = citizen.school
    bilet_distr = BiletDistribution.objects.filter(school=school)
    if len(bilet_distr) != 0:
        bilet_distr = bilet_distr[0]
        if bilet_distr.test_type == True:
            school_guid_type = "SPO"
        else:
            school_guid_type = "VO"
    else:
        school_guid_type = "VO"
    choosen_bundles = VocGuidTest.objects.filter(participants=citizen).values(
        "id", "name", "description", "img_link", "guid_type"
    )
    slots = TimeSlot.objects.all()
    slots_now = []
    for slot in slots:
        if date.today() < slot.date and slot.date < (date.today() + timedelta(days=7)):
            slots_now.append(slot)
    
    bundles = VocGuidTest.objects.filter(slots__in=slots_now, guid_type=school_guid_type).exclude(participants=citizen).values(
        "id", "name", "description", 
        "img_link", "guid_type", 
        "age_group", 'education_program_link', 
        'education_center__name', 'disability_types',
        "contact__full_name", "contact__email", "contact__phone"
    )

    group = VocGuidGroup.objects.filter(participants=citizen)
    choosen_type_presence = set()
    choosen_tests_dict = {}
    for guid_type in VocGuidTest.TYPE_CHOICES:
        choosen_tests_dict[guid_type[0]] = {}

    for bundle in choosen_bundles:
        if len(group) != 0:
            slot = TimeSlot.objects.filter(group__in=group)
            if len(slot) != 0:
                slot = slot[0]
            else:
                slot = None
        else:
            slot = None
        if slot == None:
            choosen_tests_dict[bundle["guid_type"]][bundle['id']] = {
                'id': bundle['id'],
                'name': bundle['name'],
                'description': bundle['description'],
                'slot': False
            }
        else:
            choosen_tests_dict[bundle["guid_type"]][bundle['id']] = {
                'id': bundle['id'],
                'name': bundle['name'],
                'description': bundle['description'],
                'slot': True,
                'date': slot.date,
                'time': slot.slot,
                'zoom_link': slot.zoom_link
            }
        choosen_type_presence.add(bundle["guid_type"])

    type_presence = set()
    tests_dict = {}
    for guid_type in VocGuidTest.TYPE_CHOICES:
        tests_dict[guid_type[0]] = {}
    if citizen.school_class.grade_number >= 10:
        age_group = '10-11'
    elif citizen.school_class.grade_number <= 7:
        age_group = '6-7'
    else:
        age_group = '8-9'

    citizen = Citizen.objects.get(email=request.user.email)
    for bundle in bundles:
        if school.city != "Самара":
            if bundle["age_group"] == "ALL" or bundle["age_group"] == age_group:
                if citizen.disability_type is None or citizen.disability_type.id == bundle['disability_types']:
                    tests_dict[bundle["guid_type"]][bundle['id']] = {
                        'id': bundle['id'],
                        'name': bundle['name'],
                        'description': bundle['description'],
                        'img_link': bundle['img_link'],
                        'education_program_link': bundle['education_program_link'],
                        'education_center': bundle['education_center__name']
                    }
                    type_presence.add(bundle["guid_type"])
                

    message = ""
    if len(choosen_type_presence) == 0:
        message = "На данные момент Вы не записались не на одно из доступных профориентационных мероприятий. Вы можете просмотреть и выбрать интересующие вас их ниже."
    
    schools = School.objects.exclude(name=citizen.school.name)

    return render(request, "vocational_guidance/index.html",{
        'page_name': 'Личный кабинет',
        'user': citizen,
        'choosen_bundles': choosen_tests_dict,
        'choosen_type_presence': choosen_type_presence,
        'bundles': tests_dict,
        'slot': slot,
        'type_presence': type_presence,
        'message': message,
        "birthday": citizen.birthday.isoformat(),
        'schools': schools,
        "disability_types": DisabilityType.objects.all(),
        "choosed": len(choosen_bundles),
        "guid_type": school_guid_type
    })

def school_dash(request, school_id):
    school = School.objects.get(id=school_id)
    groups = VocGuidGroup.objects.filter(school=school)
    groups_count = len(VocGuidGroup.objects.filter(school=school))
    slots_enroll = TimeSlot.objects.filter(group__in=groups)
    groups_enroll = len(VocGuidGroup.objects.filter(school=school, slots__in=slots_enroll))
    tests = VocGuidTest.objects.all()
    tests_dict = {}
    limit = BiletDistribution.objects.filter(school=school).values("quota")
    if len(limit) != 0:
        limit = limit[0]['quota']
        participants = Citizen.objects.filter(school=school)
        assessments_count = len(VocGuidAssessment.objects.filter(participant__in=participants))
        limit = limit - assessments_count
        if limit >= 8:
            limit = 8
    else:
        limit = 8
    groups_counta = 0
    for test in tests:
        groups = VocGuidGroup.objects.filter(bundle=test, school=school).annotate(participants_count=Count('participants'))
        if len(groups) != 0:
            tests_dict[f'{test.name} (Код пробы – {test.id})'] = {}
            contact = TestContact.objects.filter(test=test)
            if len(contact) != 0:
                contact = contact[0]
                tests_dict[f'{test.name} (Код пробы – {test.id})']['contact_name'] = contact.full_name
                tests_dict[f'{test.name} (Код пробы – {test.id})']['email'] = contact.email
                tests_dict[f'{test.name} (Код пробы – {test.id})']['phone'] = contact.phone
            else:
                tests_dict[f'{test.name} (Код пробы – {test.id})']['contact_name'] = None
            tests_dict[f'{test.name} (Код пробы – {test.id})']['groups'] = []
            for group in groups:
                groups_counta += 1
                group_dict = []
                group_dict.append(group)
                slots = TimeSlot.objects.filter(test=test)
                slots_list = []
                if len(slots) != 0:
                    for slot in slots:
                        slot_groups = VocGuidGroup.objects.filter(slots=slot)
                        if len(groups) != 0:
                            participants = 0
                            for slot_group in slot_groups:
                                participants += slot_group.participants.count()
                                slot.participants_count = participants
                                slot.save()
                        if participants + group.participants_count <= limit:
                            if date.today() < slot.date and slot.date < (date.today() + timedelta(days=7)):
                                slots_list.append(slot)
                else:
                    slots_list = None
                if slots_list == []:
                    slots_list = None
                group_dict.append(slots_list)
                participant = Citizen.objects.filter(voc_guid_groups=group)
                group_dict.append(participant)
                timeslot = TimeSlot.objects.filter(group=group, test=test)
                if len(timeslot) != 0:
                        group_dict.append(timeslot[0])
                        if timeslot[0].date <= date.today():
                            group_dict.append(False)
                        else:
                            group_dict.append(True)
                else:
                    group_dict.append(None)
                tests_dict[f'{test.name} (Код пробы – {test.id})']['groups'].append(group_dict)

    students = Citizen.objects.filter(school=school)
    students_count = len(students)
    six_grade = len(students.filter(school_class__grade_number__in = [6,7]))
    eight_grade = len(students.filter(school_class__grade_number__in = [8,9]))
    ten_grade = len(students.filter(school_class__grade_number__in = [10,11]))

    enroll_count = len(students.filter(voc_guid_tests__isnull=False))
    six_grade_enroll = len(students.filter(school_class__grade_number__in = [6,7], voc_guid_tests__isnull=False))
    eight_grade_enroll = len(students.filter(school_class__grade_number__in = [8,9], voc_guid_tests__isnull=False))
    ten_grade_enroll = len(students.filter(school_class__grade_number__in = [10,11], voc_guid_tests__isnull=False))

    #Проф. пробы
    slots = TimeSlot.objects.all()
    slots_now = []
    for slot in slots:
        if date.today() < slot.date and slot.date < (date.today() + timedelta(days=7)):
            slots_now.append(slot)

    school_guid_type = "VO"
    bilet_distr = BiletDistribution.objects.filter(school=school)
    if len(bilet_distr) != 0:
        bilet_distr = bilet_distr[0]
        if bilet_distr.test_type == True:
            school_guid_type = "SPO"

    bundles = VocGuidTest.objects.filter(slots__in=slots_now, guid_type=school_guid_type)

    return render(request, 'vocational_guidance/school_dash.html', {
        'school': school,
        'tests': tests_dict,
        'bundles': bundles,
        'bundle_len': len(bundles),

        'groups_count': groups_count,
        'groups_enroll': groups_enroll,
        'students_count': students_count,
        'six_grade': six_grade,
        'eight_grade': eight_grade,
        'ten_grade': ten_grade,
        'enroll_count': enroll_count,
        'six_grade_enroll': six_grade_enroll,
        'eight_grade_enroll': eight_grade_enroll,
        'ten_grade_enroll': ten_grade_enroll
    })

def ed_center_dash(request, ed_center_id):
    pass

def region_dash(request):
    pass

@csrf_exempt
def choose_bundle(request):
    if request.method == "POST":
        bundle_id = request.POST["bundle_id"]
        citizen_id = request.POST["citizen"]
        test = VocGuidTest.objects.get(id=bundle_id)
        citizen = Citizen.objects.get(id=citizen_id)
        if citizen.school_class.grade_number >= 10:
            age_group = '10-11'
        elif citizen.school_class.grade_number <= 7:
            age_group = '6-7'
        else:
            age_group = '8-9'
        previous_bundles = VocGuidTest.objects.filter(
            participants=citizen_id,
            guid_type=test.guid_type
        )
        if len(previous_bundles) != 0:
            citizen.voc_guid_tests.remove(previous_bundles[0])
        test.participants.add(citizen_id)
        test.save()
        school = citizen.school
        
        groups = VocGuidGroup.objects.filter(bundle=test, school=school, age_group=age_group).annotate(participants_count=Count('participants'))
        
        if len(groups) == 0:
            create_group(citizen, test)
        else:
            add = False
            for group in groups:
                if group.participants_count < group.attendance_limit:
                    cheak_slot = TimeSlot.objects.filter(group=group)
                    if len(cheak_slot) == 0:
                        group.participants.add(citizen)
                        add = True
                        break
            if not add:
                create_group(citizen, test)
    return HttpResponseRedirect(reverse("index"))

def create_group(citizen, bundle):
    if citizen.school_class.grade_number >= 10:
        age_group = '10-11'
    elif citizen.school_class.grade_number <= 7:
        age_group = '6-7'
    else:
        age_group = '8-9'
    group = VocGuidGroup(
        school=citizen.school,
        bundle=bundle,
        attendance_limit=8,
        age_group=age_group 
    )
    group.save()
    group.participants.add(citizen)

@csrf_exempt
def reject_bundle(request):
    if request.method == "POST":
        bundle_id = request.POST["bundle_id"]
        citizen_id = request.POST["citizen"]
        bundle = VocGuidTest.objects.get(id=bundle_id)
        citizen = Citizen.objects.get(id=citizen_id)
        if citizen.school_class.grade_number >= 10:
            age_group = '10-11'
        elif citizen.school_class.grade_number <= 7:
            age_group = '6-7'
        else:
            age_group = '8-9'
        group = VocGuidGroup.objects.get(bundle=bundle,participants=citizen, age_group=age_group)

        citizen.voc_guid_tests.remove(bundle)
        citizen.voc_guid_groups.remove(group)
        citizen.save()
        if group.participants.count() == 0:
            group.delete()
    return HttpResponseRedirect(reverse("index"))

@csrf_exempt
def signin(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse("index"))
    elif request.method == "POST":
        email = request.POST["email"]
        password = request.POST["password"]
        citizen = Citizen.objects.filter(
            email=email,
        )
        user = authenticate(email=email, password=password)
        sch_group = Group.objects.filter(name='Школьник')
        if len(sch_group) != 0:
            sch_group = sch_group[0]
            if User.objects.filter(email=email, groups=sch_group):
                if user is not None:
                    if len(citizen) == 0:
                        return render(request, "vocational_guidance/login.html", {
                            "message": "Ошибка авторизации, аккаунт не активирован. Обратитесь в поддержку – support@copp63.ru"
                        })
            if user is not None:
                login(request, user)
                return HttpResponseRedirect(reverse("index"))
            else:
                return render(request, "vocational_guidance/login.html", {
                    "message": "Неверный логин и/или пароль."
                })
    else:
        return render(request, "vocational_guidance/login.html") 

@login_required(login_url='bilet/login')
@csrf_exempt
def change_password(request):
    if request.method == "POST":
        email = request.user.email
        current_password = request.POST["current_password"]
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        user = authenticate(email=email, password=current_password)
        if user is not None:
            if password == confirmation:
                user.set_password(password)
                user.save()
                login(request, user)
    return HttpResponseRedirect(reverse("index"))

def signup(request):
    return render(request, "vocational_guidance/registration_select.html")

@csrf_exempt
def signup_child(request):
    if request.method == "POST":
        email = request.POST["email"]
        phone = request.POST["phone"]
        if len(phone) > 19:
            phone = phone[0:19]
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        first_name = request.POST['name']
        last_name = request.POST['last_name']
        middle_name = request.POST['middle_name']
        birthday = request.POST['birthday']
        grade_number = request.POST['school_class']
        grade_letter = request.POST['school_class_latter']
        school_id = request.POST['school']
        school = School.objects.get(id=school_id)
        try:
            disability_check = request.POST['disability-check']
        except:
            disability_check = False
        if disability_check != False:
            disability_type = request.POST['disability_type']
            disability_type = DisabilityType.objects.filter(id=disability_type)
            if len(disability_type) != 0:
                disability_type = disability_type[0]
        else:
            disability_type = None
        if password != confirmation:
            return render(request, "vocational_guidance/registration.html", {
                "message": "Введённые пароли не совпадают"
            })
        try:
            user = User.objects.create_user(email, password)
            user.first_name = first_name
            user.last_name = last_name
            school_group = Group.objects.get(name='Школьник')
            user.groups.add(school_group)
            school_class = SchoolClass.objects.filter(
                school=school,
                grade_number=grade_number,
                grade_letter=grade_letter
            )
            if len(school_class) != 0:
                school_class = school_class[0]
            else:
                school_class = SchoolClass(
                    school=school,
                    grade_number=int(grade_number),
                    grade_letter=grade_letter.upper()
                )
                school_class.save()
            citizen = Citizen(
                first_name=first_name,
                last_name=last_name,
                middle_name=middle_name,
                birthday=birthday,
                email=email,
                social_status='SCHS',
                school=school,
                school_class=school_class,
                phone_number = phone,
                disability_type = disability_type
            )
            citizen.save()
            user.save()
        except IntegrityError:
            schools = School.objects.all()
            cities = set()
            for school in schools:
                cities.add(school.city) 
            return render(request, "vocational_guidance/registration.html", {
                "message": "Email уже использован",
                'schools': schools,
                'cities': cities,
                "disability_types": DisabilityType.objects.all()
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        schools = School.objects.all()
        cities = set()
        for school in schools:
            cities.add(school.city) 
    
        return render(request, "vocational_guidance/registration.html", {
            'schools': schools,
            'cities': cities,
            "disability_types": DisabilityType.objects.all()
        })

@csrf_exempt
def signup_parent(request):
    if request.method == "POST":
        email = request.POST["email"]
        phone = request.POST["phone"]
        if len(phone) > 30:
            phone = phone[0:30]
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        first_name = request.POST['name']
        last_name = request.POST['last_name']
        middle_name = request.POST['middle_name']
        birthday = request.POST['birthday']
        grade_number = request.POST['school_class']
        grade_letter = request.POST['school_class_latter']
        school_id = request.POST['school']
        school = School.objects.get(id=school_id)
        try:
            disability_check = request.POST['disability-check']
        except:
            disability_check = False
        if disability_check != False:
            disability_type = request.POST['disability_type']
            disability_type = DisabilityType.objects.filter(id=disability_type)
            if len(disability_type) != 0:
                disability_type = disability_type[0]
        else:
            disability_type = None
        if password != confirmation:
            return render(request, "vocational_guidance/registration.html", {
                "message": "Введённые пароли не совпадают"
            })
        try:
            user = User.objects.create_user(email, password)
            user.first_name = first_name
            user.last_name = last_name
            school_group = Group.objects.get(name='Школьник')
            user.groups.add(school_group)
            school_class = SchoolClass.objects.filter(
                school=school,
                grade_number=grade_number,
                grade_letter=grade_letter
            )
            if len(school_class) != 0:
                school_class = school_class[0]
            else:
                school_class = SchoolClass(
                    school=school,
                    grade_number=int(grade_number),
                    grade_letter=grade_letter.upper()
                )
                school_class.save()
            citizen = Citizen(
                first_name=first_name,
                last_name=last_name,
                middle_name=middle_name,
                birthday=birthday,
                email=email,
                social_status='SCHS',
                school=school,
                school_class=school_class,
                phone_number = phone,
                disability_type = disability_type
            )
            citizen.save()
            user.save()
        except IntegrityError:
            schools = School.objects.all()
            cities = set()
            for school in schools:
                cities.add(school.city) 
            return render(request, "vocational_guidance/registration_parent.html", {
                "message": "Email уже использован",
                'schools': schools,
                'cities': cities,
                "disability_types": DisabilityType.objects.all()
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        schools = School.objects.all()
        cities = set()
        for school in schools:
            cities.add(school.city) 
    
        return render(request, "vocational_guidance/registration_parent.html", {
            'schools': schools,
            'cities': cities,
            "disability_types": DisabilityType.objects.all()
        })

@login_required(login_url='bilet/login')
@csrf_exempt
def change_profile(request):
    if request.method == "POST":
        citizen_id = request.POST["id"]
        citizen = Citizen.objects.get(id=citizen_id)
        citizen.email = request.POST["email"]
        request.user.email = request.POST["email"]
        citizen.phone_number = request.POST["phone"]
        citizen.first_name = request.POST['name']
        request.user.first_name = request.POST["name"]
        citizen.last_name = request.POST['last_name']
        request.user.last_name = request.POST["last_name"]
        citizen.middle_name = request.POST['middle_name']
        citizen.birthday = request.POST['birthday']
        school_id = request.POST['school']
        school = School.objects.get(id=school_id)
        citizen.school = school
        grade_number = request.POST['school_class']
        grade_letter = request.POST['school_class_latter']
        try:
            disability_check = request.POST['disability-check']
        except:
            disability_check = False
        if disability_check != False:
            disability_type = request.POST['disability_type']
            citizen.disability_type = DisabilityType.objects.get(id=disability_type)
        else:
            citizen.disability_type = None
        
        school_class = SchoolClass.objects.filter(
                school=school,
                grade_number=grade_number,
                grade_letter=grade_letter
        )
        if len(school_class) != 0:
            school_class = school_class[0]
        else:
            school_class = SchoolClass(
                school=school,
                grade_number=int(grade_number),
                grade_letter=grade_letter.upper()
            )
            school_class.save()
        citizen.school_class = school_class
        request.user.save()
        citizen.save()
        return HttpResponseRedirect(reverse("index"))
    return HttpResponseRedirect(reverse("index"))

@login_required(login_url='bilet/login')
@csrf_exempt
def change_profile_teacher(request):
    if request.method == "POST":
        request.user.email = request.POST["email"]
        request.user.phone_number = request.POST["phone"]
        request.user.first_name = request.POST["name"]
        request.user.last_name = request.POST["last_name"]
        request.user.middle_name = request.POST['middle_name']
        request.user.save()
        school = School.objects.get(id=request.POST["school_id"])
        school.adress = request.POST['adress']
        school.save()
        return HttpResponseRedirect(reverse("index"))
    return HttpResponseRedirect(reverse("index"))



@login_required(login_url='bilet/login')
def signout(request):
    if request.user.is_authenticated:
        logout(request)
    return HttpResponseRedirect(reverse("signin"))


@login_required
@csrf_exempt
def import_teachers(request):
    if request.method == "POST":
        form = ImportDataForm(request.POST, request.FILES)
        if form.is_valid():
            message = bvb_teachers(form)
        else:
            data = form.errors
        form = ImportDataForm()
        return render(request, "vocational_guidance/import_teachers.html",{
            'form': form,
            'message': message
        })
    else:
        form = ImportDataForm()
        return render(request, "vocational_guidance/import_teachers.html",{
            'form': form
        })

@login_required
@csrf_exempt
def import_slots(request):
    if request.method == "POST":
        form = ImportDataForm(request.POST, request.FILES)
        if form.is_valid():
            message = slots_import(form)
        else:
            data = form.errors
        form = ImportDataForm()
        return render(request, "vocational_guidance/import_slots.html",{
            'form': form,
            'message': message
        })
    else:
        form = ImportDataForm()
        return render(request, "vocational_guidance/import_slots.html",{
            'form': form
        })

@csrf_exempt
def choose_slot(request):
    if request.method == "POST":
        slot_id = request.POST["slot_id"]
        group_id = request.POST["group_id"]
        slot = TimeSlot.objects.get(id=slot_id)
        group = VocGuidGroup.objects.get(id=group_id)
        group.slots.clear()
        group.slots.add(slot)
        participants = Citizen.objects.filter(voc_guid_groups=group)
        for participant in participants:
            assessments = VocGuidAssessment.objects.filter(participant=participant, slot=slot)
            assessments.delete()
            assessment = VocGuidAssessment(
                participant=participant,
                test=slot.test,
                slot=slot
            )
            assessment.save()
    return HttpResponseRedirect(reverse("index"))

@csrf_exempt
def cancel_slot(request):
    if request.method == "POST":
        group_id = request.POST["group_id"]
        group = VocGuidGroup.objects.get(id=group_id)
        group.slots.clear()
        participants = Citizen.objects.filter(voc_guid_groups=group)
        for participant in participants:
            assessment = VocGuidAssessment.objects.filter(participant=participant)
            assessment.delete()
    return HttpResponseRedirect(reverse("index"))

def add_assessment_all(request):
    slots = TimeSlot.objects.all()
    for slot in slots:
        groups = VocGuidGroup.objects.filter(slots=slot)
        if len(groups) != 0:
            for group in groups:
                for participant in group.participants.all():
                    assessment = VocGuidAssessment.objects.filter(participant=participant, slot=slot)
                    if len(assessment) == 0:
                        assessment = VocGuidAssessment(
                            participant=participant,
                            test=slot.test,
                            slot=slot
                        )
                        assessment.save()
    return HttpResponseRedirect(reverse("index"))

def combine_groups(request):
    groups = VocGuidGroup.objects.filter(slots=None)
    for group in groups:
        duplicate_groups = VocGuidGroup.objects.filter(
            age_group=group.age_group, 
            bundle=group.bundle, 
            school=group.school
        )
        if len(duplicate_groups) != 0:
            participants = []
            for duplicate in duplicate_groups:
                for participant in duplicate.participants.all():
                    participants.append(participant)
                duplicate.delete()
            new_group = VocGuidGroup(
                age_group=group.age_group, 
                bundle=group.bundle, 
                school=group.school,
            )
            new_group.save()
            new_group.participants.set(participants)
            new_group.save()
            
    return HttpResponseRedirect(reverse("index"))

def regulate_groups(request):
    groups = VocGuidGroup.objects.filter(slots=None)
    for group in groups:
        group_count = len(group.participants.all())
        while group_count > 8:
            extra_participants_count = group_count - 8
            if extra_participants_count > 8:
                extra_participants_count = 8
            new_group = VocGuidGroup(
                age_group=group.age_group, 
                bundle=group.bundle, 
                school=group.school,
            )
            new_group.save()
            participant_count = 0
            for participant in group.participants.all():
                if participant_count < extra_participants_count:
                    participant.voc_guid_groups.clear()
                    participant.voc_guid_groups.add(new_group)
                    participant_count += 1
            group_count -= participant_count

    return HttpResponseRedirect(reverse("index"))

#Добавляем 0 квоту всем школам
def add_quotas_all(request):
    schools = School.objects.all()
    for school in schools:
        distribution = BiletDistribution.objects.filter(school=school)
        if len(distribution) == 0:
            distribution = BiletDistribution(
                school=school,
                test_type=False,
                quota=0
            )
        else:
            distribution = distribution[0]
            distribution.quota = 0
        distribution.save()
    return HttpResponseRedirect(reverse("index"))