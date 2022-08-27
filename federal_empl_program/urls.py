from django.urls import path, re_path

from . import views

urlpatterns = [
    path('',views.index, name='index'),
    #Import
    path('import/express/', views.import_express, name='import_express'),
    path('import/gd/', views.import_gd, name='import_gd'),
    path('import/statuses/', views.import_st, name='import_st'),
    path('import/schools/',views.import_sch, name='import_sch'),

    #Auth
    re_path(r'^login/$', views.login, name="login"),
    path('logout/', views.logout, name="logout"),
    #registration
    path('registration/', views.registration, name='registration'),
    path('registration/<int:stage>', views.reg_stage, name='reg_stage'),
    path('registration/<int:stage>/?c=<ed_cenret_id>/', views.reg_stage, name='reg_stage'),
    #pass_recovery
    path('password/recovery/<int:step>/', views.password_recovery, name="password_recovery"),
    
    #applicants
    path('applicant/profile/<int:user_id>/', views.applicant_profile, name="applicant_profile"),

    #Groups
    re_path(r'^groups/$', views.group_list, name='group_list'),
    path('groups/?c=<ed_cenret_id>/', views.group_list, name='group_list'),
    path('groups/select/', views.group_select, name='group_select')
]
