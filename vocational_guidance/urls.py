from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('profile/<int:id>', views.profile, name='profile'),
    path('school/dashboard/<int:id>', views.school_dash, name='school_dash'),
    path('ed_center/dashboard/<int:id>', views.ed_center_dash, name='ed_center_dash'),
    path('dashboard', views.region_dash, name='region_dash'),

#Auth
    path('login/', views.signin, name='signin'),
    path('registration/', views.signup, name='signup'),
    path('logout/', views.signout, name='signout'),

#Служебные
    path('choose_bundle',  views.choose_bundle, name='choose_bundle'),
    path('reject_bundle',  views.reject_bundle, name='reject_bundle'),
    path('change_profile', views.change_profile, name='change_profile'),
    path('change_password', views.change_password, name='change_password')
]
