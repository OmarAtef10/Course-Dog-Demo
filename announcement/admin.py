from django.contrib import admin
from .models import Announcement

# Register your models here.


@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ('id', 'course', 'creation_date')
    list_filter = ()
    search_fields = ('id', 'course__id', 'course__name',)
    fields = ('id', 'announcement', 'course', 'creation_date')
    readonly_fields = ('id', 'creation_date')
