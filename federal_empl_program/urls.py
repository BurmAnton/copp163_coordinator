from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('import/express', views.import_express, name='import_express'),
    path('import/gd', views.import_gd, name='import_gd'),
    path('import/statuses', views.import_st, name='import_st'),
    path('import/schools',views.import_sch, name='import_sch')
]
