from django.contrib import admin
from django.contrib.auth.admin import GroupAdmin, UserAdmin
from django_admin_listfilter_dropdown.filters import RelatedOnlyDropdownFilter
from easy_select2 import select2_modelform

from .forms import CustomUserChangeForm, CustomUserCreationForm
from .models import (DisabilityType, Group, Organization, User)


@admin.register(User)
class UserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    list_display = ('email', 'last_name', 'first_name', 'get_group', 'is_staff')
    list_filter = (
        ('groups', RelatedOnlyDropdownFilter), 
        'is_staff', 
        'is_active',
        'is_superuser'
    )
    fieldsets = (
        (None,
            {'fields': ('email', 'password', 'first_name', 'last_name', 'middle_name', 'phone_number')}),
        ('Права доступа',
            {'fields': ('role','is_superuser', 'is_staff', 'is_active', 'groups', 'user_permissions')}),
        ('Важные даты', 
            {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'is_staff', 'is_active')}
        ),
    )
    search_fields = ('email','last_name', 'first_name')
    ordering = ('email',)
    actions = ['remove_staff_status', 'remove_superuser_status']

    def remove_staff_status(self, request, queryset):
        queryset.update(is_staff=False)
    remove_staff_status.short_description='Убрать доступ к админке'

    def remove_superuser_status(self, request, queryset):
        queryset.update(is_superuser=False)
    remove_superuser_status.short_description='Убрать админ права'

    def get_group(self, user):
        specialist = Group.objects.filter(name='Специалист по работе с клиентами')
        coordinator_bvb = Group.objects.filter(name='Координатор')
        student = Group.objects.filter(name='Школьник')
        college_rep = Group.objects.filter(name='Представитель ЦО')

        if user.is_superuser:
            return "Админ"

        if len(User.objects.filter(groups__in=specialist, email=user.email)) != 0:
            return "Спец. по работе с клиентами"
        
        if len(User.objects.filter(groups__in=coordinator_bvb, email=user.email)) != 0:
            return "Кординатор БВБ"
                
        if len(User.objects.filter(groups__in=student, email=user.email)) != 0:
            return "Школьник"
                
        if len(User.objects.filter(groups__in=college_rep, email=user.email)) != 0:
            return "Представитель колледжа"

        return "–"
    get_group.short_description = 'Тип пользователя'


@admin.register(Group)
class GroupAdmin(GroupAdmin):
    pass


@admin.register(DisabilityType)
class DisabilityTypeAdmin(admin.ModelAdmin):
    pass


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ['name', ]
