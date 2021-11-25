from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('profile/<int:citizen_id>/', views.profile, name='profile'),
    path('school/dashboard/<int:school_id>/', views.school_dash, name='school_dash'),
    path('school/dashboard/<int:school_id>/students/', views.students_list, name='students_list'),
    path('ed_center/dashboard/<int:ed_center_id>/', views.ed_center_dash, name='ed_center_dash'),
    path('tests/', views.tests_list, name='tests_list'),

    path('dashboard/region/', views.region_dash, name='region_dash'),
    path('dashboard/bilet/', views.bilet_dashboard, name="bilet_dashboard"),
    path('dashboard/students/', views.students_dashboard, name="students_dashboard"),
    path('dashboard/quotas/', views.quotas_dashboard, name="quotas_dashboard"),

#Auth
    path('login/', views.signin, name='signin'),
    path('registration/', views.signup, name='signup'),
    path('registration/parent/', views.signup_parent, name='signup_parent'),
    path('registration/child/', views.signup_child, name='signup_child'),
    path('logout/', views.signout, name='signout'),

#Служебные
    path('choose_bundle/', views.choose_bundle, name='choose_bundle'),
    path('reject_bundle/', views.reject_bundle, name='reject_bundle'),
    path('change_profile/', views.change_profile, name='change_profile'),
    path('choose_slot/', views.choose_slot, name='choose_slot'),
    path('cancel_slot/', views.cancel_slot, name='cancel_slot'),
    path('cancel_participant/', views.cancel_participant, name='cancel_participant'),
    path('change_profile/teacher/', views.change_profile_teacher, name='change_profile_teacher'),
    path('change_profile/student/', views.change_profile_student, name='change_profile_student'),
    path('change_password/', views.change_password, name='change_password'),

#Импорт
    path('import/teachers/', views.import_teachers, name="import_teachers"),
    path('import/slots/', views.import_slots, name="import_slots"),
    path('import/slots/external/', views.import_external_slots, name="import_external_slots"),
    path('import/slots/bvb/matching/', views.import_bvb_matching, name="import_bvb_matching"),

#Экспорт
    path('export/bvb/report/students', views.bvb_students_report, name="bvb_students_report"),

#Временные
    path('add_assessment_all/', views.add_assessment_all, name='add_assessment_all'),
    path('combine_groups/', views.combine_groups, name='combine_groups'),
    path('regulate_groups/', views.regulate_groups, name='regulate_groups'),
    path('balance_quotas/', views.balance_quotas, name='balance_quotas')
]
