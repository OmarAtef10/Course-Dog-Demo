from django.contrib.auth import get_user_model
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from organization.models import Organization
from django.contrib.auth.models import User
from . import pickle_helper


# Create your models here.
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, null=True, blank=True)
    facebook_username = models.CharField(max_length=100, blank=True, null=True)
    whatsapp_number = models.CharField(max_length=100, blank=True, null=True)
    is_admin = models.BooleanField(default=False)
    oAuth_file = models.FileField(upload_to='OAuth_files/', default=None, null=True, blank=True)

    def __str__(self):
        return f'{self.user.username} Profile'


# Creates a profile on user creation
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        service = pickle_helper.create_service(instance.username)
        file = f"OAuth_files/token_{instance.username}.pickle"
        Profile.objects.create(user=instance, oAuth_file=file)
