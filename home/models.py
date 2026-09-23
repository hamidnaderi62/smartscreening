from django.db import models
from django.contrib.auth.models import User
from account.validators import validate_image_upload

class Team(models.Model):
    TEAM_TYPE = (
        ('Main', 'Main'),
        ('Advisor', 'Advisor')
    )
    name = models.CharField(max_length=200, null=True, blank=True)
    name_en = models.CharField(max_length=200, null=True, blank=True)
    name_ar = models.CharField(max_length=200, null=True, blank=True)
    specialty = models.CharField(max_length=200, null=True, blank=True)
    specialty_en = models.CharField(max_length=200, null=True, blank=True)
    specialty_ar = models.CharField(max_length=200, null=True, blank=True)
    position = models.CharField(max_length=200, null=True, blank=True)
    position_en = models.CharField(max_length=200, null=True, blank=True)
    position_ar = models.CharField(max_length=200, null=True, blank=True)
    image_file = models.ImageField(upload_to='images/team',null=True, blank=True, validators=[validate_image_upload])
    team_type = models.CharField(max_length=50, choices=TEAM_TYPE, default='Advisor', blank=True, null=True)
    desc = models.TextField(null=True, blank=True)
    image_center1 = models.ImageField(upload_to='images/center', null=True, blank=True, validators=[validate_image_upload])
    image_center2 = models.ImageField(upload_to='images/center', null=True, blank=True, validators=[validate_image_upload])
    image_center3 = models.ImageField(upload_to='images/center', null=True, blank=True, validators=[validate_image_upload])
    is_active = models.BooleanField(null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Blog(models.Model):
    user = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    title = models.CharField(max_length=200, null=True, blank=True)
    title_en = models.CharField(max_length=200, null=True, blank=True)
    title_ar = models.CharField(max_length=200, null=True, blank=True)
    desc = models.TextField(null=True, blank=True)
    desc_en = models.TextField(null=True, blank=True)
    desc_ar = models.TextField(null=True, blank=True)
    image_file = models.ImageField(upload_to='images/blog',null=True, blank=True, validators=[validate_image_upload])
    media_file = models.FileField(upload_to='medias/blog',null=True, blank=True)
    read_time = models.IntegerField(null=True, blank=True)
    is_active = models.BooleanField(null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
