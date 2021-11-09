from django.contrib import admin

from easy_select2 import select2_modelform
from django_admin_listfilter_dropdown.filters import DropdownFilter, RelatedOnlyDropdownFilter, ChoiceDropdownFilter

from citizens.models import Citizen

from .models import TimeSlot, VocGuidTest, VocGuidGroup, VocGuidAssessment, TestContact
from users.models import Group, User
from education_centers.models import EducationCenter


VocGuidAssessmentForm = select2_modelform(VocGuidAssessment, attrs={'width': '400px'})

@admin.register(VocGuidAssessment)
class VocGuidAssessmentAdmin(admin.ModelAdmin):
    search_fields = ["slot__id", 'test__name', 'slot__date', 'slot__slot', 'participant__first_name', 'participant__last_name']
    list_filter = (
        ('test', RelatedOnlyDropdownFilter),
    )

    list_display = (
        "id",
        "participant",
        "test",
        "slot",
    )


class VocGuidAssessmentInline(admin.TabularInline):
    form = VocGuidAssessmentForm
    model = VocGuidAssessment
    fields = ['participant', 'attendance']
    readonly_fields = ['participant',]
    def get_extra(self, request, obj=None, **kwargs):
        extra = 0
        if obj:
            return extra
        return extra

TimeSlotForm = select2_modelform(TimeSlot, attrs={'width': '600px'})

@admin.register(TimeSlot)
class TimeSlotAdmin(admin.ModelAdmin):
    form = TimeSlotForm
    inlines = [VocGuidAssessmentInline,]
    list_display = (
        "test", "date",
        "get_time", "get_participants",
        "get_ed_center", "participants_count"
    )
    search_fields = ["test__name","date", "group__id"]
    list_filter = (
        ('date', DropdownFilter),
        ('slot', DropdownFilter),
        ('test', RelatedOnlyDropdownFilter)
    )

    readonly_fields = ['get_ed_center', 'get_participants']
    fieldsets = (
        (None, {
            'fields': (
                'get_ed_center', 'test', 
                'date', 'slot', 'group',
                'zoom_link', 'report_link'
            )
        }),
    )

    def get_ed_center(self, slot):
        education_center = slot.test.education_center
        return education_center
    get_ed_center.short_description='Центр обучения'
    get_ed_center.admin_order_field = 'test__education_center__name'

    def get_participants(self, slot):
        groups = VocGuidGroup.objects.filter(slots=slot)
        participants = 0
        if len(groups) != 0:
            for group in groups:
                participants += len(group.participants.all())
        return participants
    get_participants.admin_order_field = 'group__participants'
    get_participants.short_description='Кол-во участников'

    def get_time(self, slot):
        SLOT_CHOICES = [
            ("MRN", "10:00–11:30"),
            ("MID", "с 15:00 до 16:30"),
            ("EVN", "с 16:30 до 18:00"),
        ]
        time = slot.slot
        if time == 'MRN':
            time = "10:00–11:30"
        elif time == "MID":
            time = "15:00-16:30"
        else:
            time = "16:30-18:00"
        return time
    get_time.short_description='Время'
    get_time.admin_order_field = 'slot'

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        cl_group = Group.objects.filter(name='Представитель ЦО')

        if len(cl_group) != 0:
            if len(User.objects.filter(groups=cl_group[0], email=request.user.email)) != 0:
                education_center = EducationCenter.objects.filter(contact_person=request.user)
                if len(education_center) != 0:
                    education_center = education_center[0]
                    tests = VocGuidTest.objects.filter(education_center=education_center)
                    if len(tests) != 0:
                        return queryset.filter(test__in=tests)
        return queryset

    def get_readonly_fields(self, request, obj=None):
        cl_group = Group.objects.filter(name='Представитель ЦО')

        if len(cl_group) != 0:
            if len(User.objects.filter(groups=cl_group[0], email=request.user.email)) != 0:
                return self.readonly_fields + [
                    'test','group',
                    'slot', 'date', 
                ]
        return self.readonly_fields

TestContactForm = select2_modelform(TestContact, attrs={'width': '400px'})

class QuestionnaireInline(admin.StackedInline):
    form = TestContactForm
    model = TestContact

VocGuidTestForm = select2_modelform(VocGuidTest, attrs={'width': '400px'})

@admin.register(VocGuidTest)
class VocGuidTestAdmin(admin.ModelAdmin):
    form = VocGuidTestForm
    inlines = [QuestionnaireInline,]
    list_display = (
        "name",
        "id",
        "guid_type",
        "attendance_limit",
        "workshop"
    )
    search_fields = ["name","education_center__name", "id"]

    fieldsets = (
        (None, {
            'fields': 
            (
                'name', 'education_center', 'thematic_env', 'profession',
                'education_program_link', 'img_link', 'description',
                'attendance_limit', 'age_group', 'disability_types', 'guid_type'
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

VocGuidGroupForm = select2_modelform(VocGuidGroup, attrs={'width': '400px'})

@admin.register(VocGuidGroup)
class VocGuidGroupAdmin(admin.ModelAdmin):
    form = VocGuidGroupForm

    search_fields = ["id", 'school__name', 'bundle__name', 'city', 'participants__email']
    list_filter = (
        ('age_group', DropdownFilter),
        ('school', RelatedOnlyDropdownFilter)
    )
    list_display = (
        "id",
        "school",
        "bundle",
        "age_group",
        "get_participants"
    )

    def get_participants(self, group):
        return group.participants.count()
            
    get_participants.admin_order_field='participants'
    get_participants.short_description='Кол-во участников'