from django.contrib import admin

from django_admin_listfilter_dropdown.filters import DropdownFilter, RelatedOnlyDropdownFilter, ChoiceDropdownFilter

from .models import TimeSlot, VocGuidBundle, VocGuidGroup, VocGuidSession

@admin.register(TimeSlot)
class TimeSlotAdmin(admin.ModelAdmin):
    pass

@admin.register(VocGuidSession)
class VocGuidSessionAdmin(admin.ModelAdmin):
    list_display = (
        "get_program_name",
        "education_center",
        "session_type",
        "attendance_limit",
        "duration",
        "get_adress",
    )
    search_fields = ["workshop", "education_center", "education_program", "attendance_limit"]
    
    list_filter = (
        ('education_center', RelatedOnlyDropdownFilter),
        ('education_program', RelatedOnlyDropdownFilter),
        ('session_type', ChoiceDropdownFilter),
        ('duration', DropdownFilter)
    )

    def get_program_name(self, session):
        program_name = session.education_program.program_name
        return program_name
    get_program_name.short_description='Название программы'

    def get_adress(self, session):
        adress = session.workshop.adress
        return adress
    get_adress.short_description='Адрес'

@admin.register(VocGuidBundle)
class VocGuidBundleAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "guid_type",
        "attendance_limit",
        "workshop"
    )
    search_fields = ["name","education_center", "programs"]

@admin.register(VocGuidGroup)
class VocGuidGroupAdmin(admin.ModelAdmin):
    list_display = (
        "get_id",
        "school",
        "age_group",
        "attendance_limit"
    )
    def get_id(self, session):
        id_group = f'Группа №{session.__str__()}'
        return id_group
    get_id.short_description='Номер группы'

