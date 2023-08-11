from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from .exports import schools
from . import imports
from education_centers.forms import ImportDataForm

# Create your views here.
@csrf_exempt
def import_schools(request):
    form = ImportDataForm()
    message = None
    if request.method == 'POST':
        form = ImportDataForm(request.POST, request.FILES)
        if form.is_valid():
            data = imports.schools(form)
            message = data
    
    return render(request, "citizens/import_schools.html", {
        'message': message,
        'form' : ImportDataForm(),
    })

def export_schools(request):
    return schools()