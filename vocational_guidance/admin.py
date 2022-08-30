from django.contrib import admin

from easy_select2 import select2_modelform
from django_admin_listfilter_dropdown.filters import DropdownFilter, RelatedOnlyDropdownFilter, ChoiceDropdownFilter

from citizens.models import Citizen

from .models import VocGuidTest, TestContact
from users.models import Group, User
from education_centers.models import EducationCenter


VocGuidTestForm = select2_modelform(VocGuidTest, attrs={'width': '400px'})

@admin.register(VocGuidTest)
class VocGuidTestAdmin(admin.ModelAdmin):
    form = VocGuidTestForm
    list_display = (
        "name",
        "competence",
        "start_datetime",
        "attendance_limit",
        "participants_count",
        "is_online",
        "address"
    )
    search_fields = ["name","education_center__name", "id"]

    fieldsets = (
        (None, {
            'fields': 
            (
                'name', 'education_center', 'competence','is_online', 
                'conference_data', 'address', 'short_description', 'description',
                'attendance_limit', 'participants_count', 'start_datetime'
            )
        }),
        ('Участники', {
            'fields':
            (
                'participants',
            )
        })
    )

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        cl_group = Group.objects.filter(name='Представитель ЦО')

        if len(cl_group) != 0:
            if len(User.objects.filter(groups=cl_group[0], email=request.user.email)) != 0:
                education_center = EducationCenter.objects.filter(contact_person=request.user)
                if len(education_center) != 0:
                    education_center = education_center[0]
                    return queryset.filter(education_center=education_center)
        return queryset

    def get_readonly_fields(self, request, obj=None):
        cl_group = Group.objects.filter(name='Представитель ЦО')

        if len(cl_group) != 0:
            if len(User.objects.filter(groups=cl_group[0], email=request.user.email)) != 0:
                return [
                    'disability_types','guid_type',
                    'workshop', 'attendance_limit', 
                    'participants', 'age_group',
                    'education_center', 'name', 'disability_types'
                ]
        return self.readonly_fields