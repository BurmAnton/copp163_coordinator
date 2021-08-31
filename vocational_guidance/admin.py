from django.contrib import admin

from django_admin_listfilter_dropdown.filters import RelatedOnlyDropdownFilter

from .models import TimeSlot, VocGuidBundle, VocGuidGroup

@admin.register(TimeSlot)
class TimeSlotAdmin(admin.ModelAdmin):
    pass

@admin.register(VocGuidBundle)
class VocGuidBundleAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "education_center",
        "workshop"
    )
    search_fields = ["name","education_center", "programs"]
    list_filter = (
        ('education_center', RelatedOnlyDropdownFilter),
        ('programs', RelatedOnlyDropdownFilter),
    )

@admin.register(VocGuidGroup)
class VocGuidGroupAdmin(admin.ModelAdmin):
    pass