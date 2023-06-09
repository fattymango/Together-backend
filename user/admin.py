from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin 

from .models import BaseUser,SpecialNeed,Volunteer

class BaseUserAdmin(UserAdmin):
    fieldsets = (
	    (None, {'fields': ('email', 'justID', 'password')}),
	    ('Personal info', {'fields': ('full_name', 'gender', "phone_number")}),
	    ('PermissionsMixin', {'fields': ('is_active', 'is_admin', 'is_just_admin', 'is_online')}),

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
	    (None, {'fields': ('email', 'justID', 'password')}),
	    ('Personal info', {'fields': ('full_name', 'gender', 'disability_type', "phone_number")}),
	    ('PermissionsMixin', {'fields': ('is_active',)}),
    )

class VolunteerAdmin(BaseUserAdmin):
    fieldsets = (
	    (None, {'fields': ('email', 'justID', 'password')}),
	    ('Personal info', {'fields': ('full_name', 'gender', 'is_validated', "phone_number")}),
	    ('PermissionsMixin', {'fields': ('is_active',)}),
    )



admin.site.register(BaseUser, BaseUserAdmin)
admin.site.register(SpecialNeed, SpecialNeedAdmin)
admin.site.register(Volunteer, VolunteerAdmin)


admin.site.unregister(Group)