from django.shortcuts import get_object_or_404, render
from django.views.decorators.csrf import csrf_exempt

from future_ticket.models import EducationCenterTicketProjectYear,\
                                 TicketFullQuota, TicketProjectYear

from .forms import ImportDataForm
from . import imports

@csrf_exempt
def quotas(request):
    project_year = get_object_or_404(TicketProjectYear, year=project_year)
    centers_project_year = EducationCenterTicketProjectYear.objects.filter(
        project_year=project_year
    )
    full_quota = get_object_or_404(TicketFullQuota, project_year=project_year)
    

    return render(request, "future_ticket/import_professions.html", {
        'project_year': project_year,
        'centers_project_year': centers_project_year,
        'full_quota': full_quota
    })

@csrf_exempt
def import_ticket_professions(request):
    form = ImportDataForm()
    message = None
    if request.method == 'POST':
        form = ImportDataForm(request.POST, request.FILES)
        if form.is_valid():
            data = imports.professions(form)
            message = data
    
    return render(request, "future_ticket/import_professions.html", {
        'message': message,
        'form' : ImportDataForm(),
    })

@csrf_exempt
def import_ticket_programs(request):
    form = ImportDataForm()
    message = None
    if request.method == 'POST':
        form = ImportDataForm(request.POST, request.FILES)
        if form.is_valid():
            data = imports.programs(form)
            message = data
    
    return render(request, "future_ticket/import_programs.html", {
        'message': message,
        'form' : ImportDataForm(),
    })