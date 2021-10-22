from django.contrib import admin

from easy_select2 import select2_modelform
from django_admin_listfilter_dropdown.filters import DropdownFilter, RelatedOnlyDropdownFilter, ChoiceDropdownFilter

from .models import TimeSlot, VocGuidTest, VocGuidGroup

TimeSlotForm = select2_modelform(TimeSlot, attrs={'width': '400px'})

@admin.register(TimeSlot)
class TimeSlotAdmin(admin.ModelAdmin):
    form = TimeSlotForm


VocGuidTestForm = select2_modelform(VocGuidTest, attrs={'width': '400px'})

@admin.register(VocGuidTest)
class VocGuidTestAdmin(admin.ModelAdmin):
    form = VocGuidTestForm
    list_display = (
        "name",
        "guid_type",
        "attendance_limit",
        "workshop"
    )
    search_fields = ["name","education_center__name"]

VocGuidGroupForm = select2_modelform(VocGuidGroup, attrs={'width': '400px'})

@admin.register(VocGuidGroup)
class VocGuidGroupAdmin(admin.ModelAdmin):
    form = VocGuidGroupForm
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
