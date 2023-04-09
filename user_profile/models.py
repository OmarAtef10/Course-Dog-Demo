from django.contrib.auth import get_user_model
from django.db import models
from organization.models import Organization
User = get_user_model()

# Create your models here.
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, null=True, blank=True)
    facebook_username = models.CharField(max_length=100, blank=True, null=True)
    whatsapp_number = models.CharField(max_length=100, blank=True, null=True)
    is_admin = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.user.username} Profile'
