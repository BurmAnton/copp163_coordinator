from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt

from .models import PartnerContact, Project, PartnerOrganization, PartnerContactEmail, PartnerContactPhone, PartnerOrganization

# Create your views here.
@csrf_exempt
def contacts_list(request):
    if request.method == 'POST':
        last_name = request.POST["last_name"]
        first_name = request.POST["first_name"]
        middle_name = request.POST["middle_name"]
        job_title = request.POST["job_title"]
        organization_id = request.POST["organization"]
        commentary = request.POST["commentary"]
        organization = PartnerOrganization.objects.get(id=organization_id)
        contact = PartnerContact(
            last_name=last_name,
            first_name=first_name,
            middle_name=middle_name,
            job_title=job_title,
            organization=organization,
            commentary=commentary
        )
        contact.save()

        email = request.POST["email"]
        email = PartnerContactEmail(email=email, contact=contact)
        email.save()

        phone = request.POST["phone"]
        phone = PartnerContactPhone(phone=phone, contact=contact)
        phone.save()

        projects_id = request.POST.getlist("project")
        contact.projects.add(*projects_id)
        contact.save()
    contacts = PartnerContact.objects.all()
    projects = Project.objects.all()
    organizations = PartnerOrganization.objects.all()

    return render(request, "users/contacts_list.html",{
        'contacts': contacts,
        'organizations': organizations,
        'projects': projects,
        'contacts_count': len(contacts)
    })

@csrf_exempt
def add_organization(request):
    if request.method == 'POST':
        name = request.POST["name"]
        organization_type = request.POST["organization_type"]
        organization = PartnerOrganization(
            name=name,
            organization_type=organization_type
        )
        organization.save()
    
    return HttpResponseRedirect(reverse("contacts_list"))

def send_mailing_list(request):
    pass