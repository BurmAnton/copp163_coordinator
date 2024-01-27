from django.contrib import admin

from .models import City, CityType,\
                    Region, TerAdministration



# Register your models here.
@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    list_display = ['name', ]


@admin.register(TerAdministration)
class TerAdministrationAdmin(admin.ModelAdmin):
    list_display = ['name', 'region']


@admin.register(CityType)
class CityTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'short_name']


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ['name', 'city_type', 'region']

