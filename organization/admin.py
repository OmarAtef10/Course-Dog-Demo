from django.contrib import admin
from .models import *
# Register your models here.


@admin.register(Organization)
class OrganizationSiteAdmin(admin.ModelAdmin):
    list_display = ('name', 'faculty_name', 'organization_name',)
    list_filter = ()
    search_fields = ('name', 'faculty_name', 'organization_name',)
    fields = ('faculty_name', 'organization_name', 'name')
    readonly_fields = ()


@admin.register(UserOrganizationAdmin)
class UserOrganizationAdminSiteAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'organization')
    list_filter = ()
    search_fields = ('user__id', 'organization__name')
    fields = ('id', 'user', 'organization')
    readonly_fields = ('id',)


@admin.register(OrganizationSubdomain)
class OrganizationSubdomainAdmin(admin.ModelAdmin):
    list_display = ('organization', 'subdomain')
    list_filter = ()
    search_fields = ('organization__name', 'subdomain')
    fields = ('organization', 'subdomain')
    readonly_fields = ()
