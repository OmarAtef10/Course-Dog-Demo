from django.contrib import admin
from .models import Profile

# Register your models here.


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'organization',
                    'facebook_username', 'whatsapp_number', 'is_admin')
    list_filter = ('is_admin',)
    search_fields = ('user__username', 'user__email',
                     'facebook_username', 'whatsapp_number', 'organization__name')
    readonly_fields = ('id',)
