from django.db import models
from organization.models import Organization
from django.contrib.auth.models import User


# Create your models here.


class Course(models.Model):
    id = models.BigIntegerField(primary_key=True, db_index=True, unique=True)
    code = models.CharField(max_length=100, blank=True, null=True)
    organization = models.ForeignKey(Organization, on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(max_length=256, blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        indexes = [
            models.Index(fields=['code', ]),
        ]

    def __str__(self):
        return f"{self.name} - {self.organization.name}"


class UserCourseAdmin(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)

    class Meta:
        unique_together = (('user', 'course'),)


class Subscription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)

    class Meta:
        unique_together = (('user', 'course'),)


class DriveFolders(models.Model):
    id = models.CharField(max_length=255, primary_key=True, db_index=True, unique=True)
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=255)
    organization = models.ForeignKey(Organization, on_delete=models.SET_NULL, null=True, blank=True, default=None)

    def __str__(self):
        return f"{self.name} - {self.code}"

    class Meta:
        verbose_name_plural = "Drive Folders"
