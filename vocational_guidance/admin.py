from django.contrib import admin

from .models import TimeSlot, VocGuidBundle, VocGuidGroup

@admin.register(TimeSlot)
class TimeSlotAdmin(admin.ModelAdmin):
    pass

@admin.register(VocGuidBundle)
class VocGuidBundleAdmin(admin.ModelAdmin):
    pass

@admin.register(VocGuidGroup)
class VocGuidGroupAdmin(admin.ModelAdmin):
    pass