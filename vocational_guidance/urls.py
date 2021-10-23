from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('profile/<int:citizen_id>', views.profile, name='profile'),
    path('school/dashboard/<int:school_id>', views.school_dash, name='school_dash'),
    path('ed_center/dashboard/<int:ed_center_id>', views.ed_center_dash, name='ed_center_dash'),
    path('dashboard', views.region_dash, name='region_dash'),
    path('import_teachers', views.import_teachers, name="import_teachers"),
    path('import_slots', views.import_slots, name="import_slots"),

#Auth
    path('login/', views.signin, name='signin'),
    path('registration/', views.signup, name='signup'),
    path('registration/parent', views.signup_parent, name='signup_parent'),
    path('registration/child', views.signup_child, name='signup_child'),
    path('logout/', views.signout, name='signout'),

#Служебные
    path('choose_bundle',  views.choose_bundle, name='choose_bundle'),
    path('reject_bundle',  views.reject_bundle, name='reject_bundle'),
    path('change_profile', views.change_profile, name='change_profile'),
    path('change_profile_teacher', views.change_profile_teacher, name='change_profile_teacher'),
    path('change_password', views.change_password, name='change_password')
]
