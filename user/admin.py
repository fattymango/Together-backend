from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin 

from .models import BaseUser,SpecialNeed,Volunteer,Admin

class BaseUserAdmin(UserAdmin):
    fieldsets = (
        (None, {'fields': ('email','justID', 'password')}),
        ('Personal info', {'fields': ('full_name','gender')}),
        ('Permissions', {'fields': ( 'is_active','is_admin',)}),
        ('Important dates', {'fields': ()})
    )
    # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
    # overrides get_fieldsets to use this attribute when creating a user.
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields' : ('justID', 'password1', 'password2'),
        }),
    )
    list_display = ('email', 'justID')
    search_fields=('email','justID')
    ordering = None
    filter_horizontal=()
    list_filter=()


class SpecialNeedAdmin(BaseUserAdmin):
    fieldsets = (
        (None, {'fields': ('email','justID', 'password')}),
        ('Personal info', {'fields': ('full_name','gender','disability_type')}),
        ('Permissions', {'fields': ( 'is_active','is_admin',)}),
    )

class VolunteerAdmin(BaseUserAdmin):
    fieldsets = (
        (None, {'fields': ('email','justID', 'password')}),
        ('Personal info', {'fields': ('full_name','gender','is_validated')}),
        ('Permissions', {'fields': ( 'is_active','is_admin',)}),
    )

class AdminUserAdmin(BaseUserAdmin):
    pass

admin.site.register(BaseUser, BaseUserAdmin)
admin.site.register(SpecialNeed, SpecialNeedAdmin)
admin.site.register(Volunteer, VolunteerAdmin)
admin.site.register(Admin, AdminUserAdmin)

admin.site.unregister(Group)