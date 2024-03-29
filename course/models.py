from django.db import models
from organization.models import Organization
from django.contrib.auth.models import User
from django.db.models.signals import pre_delete
from django.dispatch import receiver
# Create your models here.


class DriveFolders(models.Model):
    id = models.CharField(max_length=256, primary_key=True,
                          db_index=True, unique=True)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    name = models.CharField(max_length=256)
    code = models.CharField(max_length=100)

    class Meta:
        verbose_name_plural = "Drive Folders"


class MainCourse(models.Model):
    code = models.CharField(max_length=50)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    name = models.CharField(max_length=256)
    materials_clusterd = models.BooleanField(default=False)
    announcements_clusterd = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.name} - {self.organization.name}'

    class Meta:
        unique_together = (('code', 'organization'),)


class Course(models.Model):
    id = models.BigIntegerField(primary_key=True, db_index=True, unique=True)
    code = models.CharField(max_length=100, blank=True, null=True)
    organization = models.ForeignKey(
        Organization, on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(max_length=256, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    linked_drive_folder = models.ForeignKey(
        DriveFolders, on_delete=models.SET_NULL, null=True, blank=True, unique=True)
    main_course = models.ForeignKey(
        MainCourse, on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=['code', ]),
        ]

    def __str__(self):
        return f"{self.name} - {self.organization.name}"


class UserCourseAdmin(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(MainCourse, on_delete=models.CASCADE)

    class Meta:
        unique_together = (('user', 'course'),)


class Subscription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(MainCourse, on_delete=models.CASCADE)

    class Meta:
        unique_together = (('user', 'course'),)



@receiver(pre_delete, sender=Course)
def delete_linked_drive_folder(sender, instance, **kwargs):
    if instance.linked_drive_folder:
        instance.linked_drive_folder.delete()
        