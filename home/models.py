from django.db import models
from django.contrib.auth.models import User

class Team(models.Model):
    TEAM_TYPE = (
        ('Main', 'Main'),
        ('Advisor', 'Advisor')
    )
    name = models.CharField(max_length=200, null=True, blank=True)
    name_en = models.CharField(max_length=200, null=True, blank=True)
    specialty = models.CharField(max_length=200, null=True, blank=True)
    specialty_en = models.CharField(max_length=200, null=True, blank=True)
    position = models.CharField(max_length=200, null=True, blank=True)
    position_en = models.CharField(max_length=200, null=True, blank=True)
    image_file = models.ImageField(upload_to='images/team',null=True, blank=True)
    team_type = models.CharField(max_length=50, choices=TEAM_TYPE, default='Advisor', blank=True, null=True)
    desc = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


