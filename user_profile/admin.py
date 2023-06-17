from django.contrib import admin
from .models import Profile, AdminRequests


# Register your models here.


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'organization',
                    'facebook_id', 'whatsapp_number', 'is_admin')
    list_filter = ('is_admin',)
    search_fields = ('user__username', 'user__email',
                     'facebook_id', 'whatsapp_number', 'organization__name')
    readonly_fields = ('id',)


class AdminRequestsAdmin(admin.ModelAdmin):
    list_display = ('id', 'profile', 'status')
    list_filter = ('status', 'profile__user__username',)
    search_fields = ('profile__user__username', 'profile__user__email',)
    readonly_fields = ('id',)


admin.site.register(AdminRequests, AdminRequestsAdmin)
