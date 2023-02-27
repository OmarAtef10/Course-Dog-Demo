from django.db import models
from course.models import Course


# Create your models here.
class Announcement(models.Model):
    announcement = models.TextField()
    course = models.ForeignKey(Course, on_delete=models.CASCADE)

    def __str__(self):
        return f"Announcement for {self.course.code}"
