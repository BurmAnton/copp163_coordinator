from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('test', views.test, name='test'),
    path('login', views.signin, name='signin'),
    path('registration', views.signup, name='signup'),
    path('logout', views.signout, name='signout'),
    path('choose_bundle',  views.choose_bundle, name='choose_bundle'),
    path('reject_bundle',  views.reject_bundle, name='reject_bundle'),
    path('change_profile', views.change_profile, name='change_profile'),
    path('change_password', views.change_password, name='change_password')

]
