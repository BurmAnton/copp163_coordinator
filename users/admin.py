from django.contrib import admin
from django.contrib.auth.admin import UserAdmin, GroupAdmin

from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import User, Group

@admin.register(User)
class UserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    list_display = ('email', 'is_staff', 'is_active',)
    list_filter = ('email', 'is_staff', 'is_active',)
    fieldsets = (
        (None,
            {'fields': ('email', 'password', 'first_name', 'last_name', 'middle_name', 'phone_number')}),
        ('Права доступа',
            {'fields': ('is_superuser', 'is_staff', 'is_active', 'groups', 'user_permissions')}),
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

@admin.register(Group)
class GroupAdmin(GroupAdmin):
    pass
