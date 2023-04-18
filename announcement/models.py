from django.db import models
from course.models import Course


# Create your models here.
class Announcement(models.Model):
    announcement = models.TextField()
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    creation_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Announcement {self.course.code} - {self.course.organization.name}"
