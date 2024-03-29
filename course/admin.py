from django.contrib import admin
from .models import *

# Register your models here.


@admin.register(Course)
class CourseSiteAdmin(admin.ModelAdmin):
    list_display = ('id', 'code', 'organization', 'name')
    list_filter = ()
    search_fields = ('code', 'name', 'organization__name',
                     'organization__organization_name')
#    readonly_fields = ('id',)


@admin.register(MainCourse)
class MainCourseSiteAdmin(admin.ModelAdmin):
    list_display = ('id', 'code', 'organization', 'name')
    list_filter = ()
    search_fields = ('id', 'code', 'name', 'organization__organization_name',)


@admin.register(UserCourseAdmin)
class UserCourseAdminSiteAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'course')
    list_filter = ()
    search_fields = ('user__username', 'user__email', 'course__code',
                     'course__name', 'course__id', 'course__organization__name')
    fields = ('id', 'user', 'course')
    readonly_fields = ('id',)


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'course')
    list_filter = ()
    search_fields = ('user__username', 'user__email', 'course__code',
                     'course__name', 'course__id', 'course__organization__name')
    fields = ('id', 'user', 'course')
    readonly_fields = ('id',)


class DriveFolderAdmin(admin.ModelAdmin):
    list_display = ('id', 'organization', 'name', 'code')
    list_filter = ()
    search_fields = ('organization__name', 'name', 'code')
    fields = ('id', 'organization', 'name', 'code')
#    readonly_fields = ('id',)


admin.site.register(DriveFolders, DriveFolderAdmin)
