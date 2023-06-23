from django.db import models
from course.models import Course


# Create your models here.
class Announcement(models.Model):
    id = models.BigIntegerField(primary_key=True, db_index=True, unique=True)
    title = models.CharField(max_length=1000, default="New Announcement")
    content = models.TextField()
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    creation_date = models.DateTimeField(auto_now=True)
    similar_to = models.ForeignKey(
        "self", on_delete=models.SET_NULL, blank=True, null=True)

    def __str__(self):
        return f"Announcement {self.course.code} - {self.course.organization.name}"
