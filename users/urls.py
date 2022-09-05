from django.urls import path

from . import views

urlpatterns = [
    path('partners/', views.contacts_list, name='contacts_list'),
    path('add/organization', views.add_organization, name='add_organization'),
    path('mailing_list/send', views.send_mailing_list, name='send_mailing_list')
]
