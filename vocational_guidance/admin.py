from django.contrib import admin

from easy_select2 import select2_modelform
from django_admin_listfilter_dropdown.filters import DropdownFilter, RelatedOnlyDropdownFilter, ChoiceDropdownFilter

from .models import TimeSlot, VocGuidTest, VocGuidGroup

TimeSlotForm = select2_modelform(TimeSlot, attrs={'width': '400px'})

@admin.register(TimeSlot)
class TimeSlotAdmin(admin.ModelAdmin):
    list_display = (
        "test",
        "date",
        "get_time",
        "get_ed_center"
    )
    search_fields = ["test__name","date"]

    def get_ed_center(self, slot):
        education_center = slot.test.education_center
        return education_center
    get_ed_center.short_description='Центр обучения'

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
