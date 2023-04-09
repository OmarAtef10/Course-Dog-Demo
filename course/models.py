from django.db import models
from organization.models import Organization
from django.contrib.auth.models import User
# Create your models here.


class Course(models.Model):
    code = models.CharField(max_length=100,
                            unique=True, blank=False, default="")
    organization = models.ForeignKey(
        Organization, on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(max_length=256, unique=True, blank=True, null=True)

    class Meta:
        indexes = [
            models.Index(fields=['code',]),
        ]

    def __str__(self):
        return f"course {self.code}"


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
