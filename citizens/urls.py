from django.urls import path

from . import views

urlpatterns = [
    path('schools/import/', views.import_schools, name='import_schools')
]