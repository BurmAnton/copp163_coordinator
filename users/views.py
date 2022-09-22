from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required

from federal_empl_program.forms import ImportDataForm
from .models import PartnerContact, Project, PartnerOrganization, PartnerContactEmail, PartnerContactPhone, PartnerOrganization
from . import imports
from . import sendpulse
# Create your views here.
@csrf_exempt
def contacts_list(request):
    message = None
    data = None
    if request.method == 'POST':
        if 'add_contact' in request.POST:
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

            emails = request.POST["email"].split(',')
            for email in emails:
                email = email.strip()
                email = PartnerContactEmail(contact=contact, email=email)
                email.save()

            phones = request.POST["phone"].split(',')
            for phone in phones:
                phone = phone.strip()
                phone = PartnerContactPhone(contact=contact, phone=phone)
                phone.save()

            projects_id = request.POST.getlist("project")
            contact.projects.add(*projects_id)
            contact.save()
            message = "AddContact"
            data = contact
        elif 'edit_contact' in request.POST:
            contact_id = request.POST['id']
            contact = PartnerContact.objects.get(id=contact_id)
            contact.last_name = request.POST["last_name"]
            contact.first_name = request.POST["first_name"]
            contact.middle_name = request.POST["middle_name"]
            contact.job_title = request.POST["job_title"]
            contact.commentary = request.POST["commentary"]
            organization_id = request.POST["organization"]
            contact.organization = PartnerOrganization.objects.get(id=organization_id)
            contact.save()
            
            old_emails = PartnerContactEmail.objects.filter(contact=contact).delete()
            emails = request.POST["email"].split(',')
            for email in emails:
                email = email.strip()
                email = PartnerContactEmail(contact=contact, email=email)
                email.save()

            old_phones = PartnerContactPhone.objects.filter(contact=contact).delete()
            phones = request.POST["phone"].split(',')
            for phone in phones:
                phone = phone.strip()
                phone = PartnerContactPhone(contact=contact, phone=phone)
                phone.save()

            projects_id = request.POST.getlist("project")
            contact.projects.remove(*Project.objects.all())
            contact.projects.add(*projects_id)
            contact.save()
            message = "Change Contact"
            data = contact
        elif 'delete_contact' in request.POST:
            contact_id = request.POST['id']
            contact = PartnerContact.objects.get(id=contact_id)
            data = f'{contact.last_name} {contact.first_name} {contact.middle_name}'
            contact.delete()
            message = "Delete Contact"
        elif 'import_contacts' in request.POST:
            form = ImportDataForm(request.POST, request.FILES)
            if form.is_valid():
                data = imports.contacts(form)
                message = data[0]
            else:
                data = form.errors
                message = "IndexError"
        elif 'send_emails' in request.POST:
            from_email = request.POST["from_email"]
            name = request.POST["name"]
            subject = request.POST["subject"]
            text = request.POST["text"]

            organizationtype = request.POST.getlist("organizationtype")
            projects = request.POST.getlist("projects")
            organizations = request.POST.getlist("organizations")
            emails = request.POST.getlist("emails")
            mailing_list = emails
            partners = PartnerContact.objects.all()
            projects = Project.objects.filter(project_name__in=projects)
            if len(projects) != 0:
                partners = partners.filter(projects__in=projects)
            if len(organizationtype) != 0 and len(organizations) != 0:
                organizations = PartnerOrganization.objects.filter(name__in=organizations, organization_type__in=organizationtype)
                partners = partners.filter(organization__in=organizations)
            elif len(organizations) != 0:
                organizations = PartnerOrganization.objects.filter(name__in=organizations)
                partners = partners.filter(organization__in=organizations)
            elif len(organizationtype) != 0:
                organizations = PartnerOrganization.objects.filter(organization_type__in=organizationtype)
                partners = partners.filter(organization__in=organizations)
            mailing_list += list(PartnerContactEmail.objects.filter(contact__in=partners).values_list('email', flat=True))
            message = sendpulse.send_campaign(from_email, name, subject, text, mailing_list)
            if message == "BisyError":
                data = ""
            else:
                data = message
                message = "SendMails"
    contacts = PartnerContact.objects.all()
    projects = Project.objects.all()
    organizations = PartnerOrganization.objects.all()
    
    return render(request, "users/contacts_list.html",{
        'contacts': contacts,
        'organizations': organizations,
        'projects': projects,
        'contacts_count': len(contacts),
        'from_emails': sendpulse.get_emails(),
        'form': ImportDataForm(request.POST, request.FILES),
        'message': message,
        'data': data
    })

@csrf_exempt
def add_organization(request):
    if request.method == 'POST':
        name = request.POST["name"]
        organization_inn = request.POST["organization_inn"]
        organization_type = request.POST["organization_type"]
        organization = PartnerOrganization(
            name=name,
            organization_inn=organization_inn,
            organization_type=organization_type
        )
        organization.save()
    return HttpResponseRedirect(reverse("contacts_list"))