from django.contrib.auth import get_user_model
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from organization.models import Organization
from django.contrib.auth.models import User
from . import OAuth_helpers
from organization.models import Organization, OrganizationSubdomain
from django.contrib.auth.models import User, Group


# Create your models here.


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, null=True, blank=True)
    facebook_id = models.CharField(max_length=100, blank=True, null=True)
    whatsapp_number = models.CharField(max_length=100, blank=True, null=True)
    is_admin = models.BooleanField(default=False)
    oAuth_file = models.FileField(
        upload_to='OAuth_files/', default=None, null=True, blank=True)

    def __str__(self):
        return f'{self.user.username} Profile'


status_choices = (
    ('pending', 'pending'),
    ('accepted', 'accepted'),
    ('rejected', 'rejected'),
)


class AdminRequests(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    status = models.CharField(max_length=100, choices=status_choices, default='pending')

    def __str__(self):
        return f'{self.profile.user.username} Request'

    class Meta:
        verbose_name_plural = "Admin Requests"
        verbose_name = "Admin Request"



@receiver(post_save, sender=AdminRequests)
def handle_post_save_logic(sender, instance, created, *args, **kwargs):
    if instance.status == 'accepted':
        instance.profile.is_admin = True
        instance.profile.save()
    elif instance.status == 'rejected':
        instance.profile.is_admin = False
        instance.profile.save()


def get_domain(email):
    return email.split('@')[-1]


# Creates a profile on user creation


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        user = instance
        user_domain = get_domain(user.email)
        student_group = Group.objects.get(name='Student')
        user.groups.add(student_group)
        user_profile = Profile(user=user)
        try:
            organization = OrganizationSubdomain.objects.get(
                subdomain=user_domain).organization
            user_profile.organization = organization
        except OrganizationSubdomain.DoesNotExist:
            pass
        user_profile.save()
