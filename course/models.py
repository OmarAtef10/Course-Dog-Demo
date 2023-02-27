from django.db import models


# Create your models here.

class Course(models.Model):
    code = models.CharField(max_length=100, unique=True, blank=False, default="")

    def __str__(self):
        return f"course {self.code}"

