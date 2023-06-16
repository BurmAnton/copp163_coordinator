from django.urls import path, re_path

from . import views

urlpatterns = [
    path('',views.index, name='index'),
    #Import
    path('import/express/', views.import_express, name='import_express'),
    #Auth
    re_path(r'^login/$', views.login, name="login"),
    path('logout/', views.logout, name="logout"),
    #Quotes
    path('quota/dashboard/', views.quota_dashboard, name="quota_dashboard")
]
