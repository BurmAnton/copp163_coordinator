from django.urls import path

from . import views

urlpatterns = [
    path('partners/', views.contacts_list, name='contacts_list'),
    path('add/organization/', views.add_organization, name='add_organization')
    #,path('addressbooks/', views.addressbooks, name='addressbooks')
]
