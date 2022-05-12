from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('import/express/', views.import_express, name='import_express'),
    path('import/gd/', views.import_gd, name='import_gd'),
    path('import/statuses/', views.import_st, name='import_st'),
    path('import/schools/',views.import_sch, name='import_sch'),
    #auth
    path('login/', views.login, name="login"),
    path('logout/', views.logout, name="logout"),
    #registration
    path('registration/', views.registration, name='registration'),
    path('registration/<int:stage>', views.reg_stage, name='reg_stage'),
    #pass_recovery
    path('password/recovery/<int:step>/', views.password_recovery, name="password_recovery"),
]
