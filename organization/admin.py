from django.contrib import admin
from .models import *
# Register your models here.
admin.site.register(Organization)
admin.site.register(UserOrganizationAdmin)
admin.site.register(OrganizationSubdomain)
