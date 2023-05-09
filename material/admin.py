from django.contrib import admin
from .models import *


# Register your models here.


@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    list_display = ('id', 'parent_course', 'file_name')
    list_filter = ('parent_course__name',)
    search_fields = ('file_name', 'id', 'parent_course__id',
                     'parent_course__name', 'parent_course__organization__name')
    readonly_fields = ('id',)
