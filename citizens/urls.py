from django.urls import path

from . import views

urlpatterns = [
    path('schools/import/', views.import_schools, name='import_schools'),
    path('export/schools/', views.export_schools, name='export_schools'),
]