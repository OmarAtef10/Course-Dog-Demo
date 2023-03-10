from django.db import models
from django.contrib.auth.models import User
# Create your models here.


class Organization(models.Model):
    faculty_name = models.CharField(max_length=128)
    organization_name = models.CharField(max_length=128)
    name = models.CharField(max_length=356, primary_key=True)


class UserOrganization(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)

    class Meta:
        unique_together = (('user', 'organization'),)


class UserOrganizationAdmin(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)

    class Meta:
        unique_together = (('user', 'organization'),)


class OrganizationSubdomain(models.Model):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    subdomain = models.CharField(
        max_length=128, null=False, blank=False, primary_key=True)
