from django.db import models
from django.contrib.auth.models import User

class Organization(models.Model):
    title = models.CharField(max_length=200)
    code = models.CharField(max_length=10, unique=True)
    image = models.ImageField(upload_to="organization/images", blank=True, null=True)
    logo = models.ImageField(upload_to="organization/logo", blank=True, null=True)
    slug = models.SlugField(max_length=50, unique=True)  # For URL routing
    website = models.CharField(max_length=2000, blank=True, null=True)
    sentence = models.CharField(max_length=2000, blank=True, null=True)

    def __str__(self):
        return self.title  # Fixed: was self.user.title


class Profile(models.Model):
    USER_TYPE = (
        ('Person', 'Person'),
        ('Organization', 'Organization')
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to="profiles/images", blank=True, null=True)
    code = models.CharField(max_length=10)
    organization = models.ForeignKey(Organization, on_delete=models.SET_NULL, null=True, blank=True)
    user_type = models.CharField(max_length=50, choices=USER_TYPE, default='Person', blank=True, null=True)

    def __str__(self):
        return self.user.username