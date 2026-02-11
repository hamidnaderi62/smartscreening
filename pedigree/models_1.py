from django.db import models
from django.contrib.auth.models import User

class FamilyMember(models.Model):
    GENDER_CHOICES = [
        ('M', 'مرد'),
        ('F', 'زن'),
    ]

    STATUS_CHOICES = [
        ('A', 'زنده'),
        ('D', 'فوت شده'),
    ]

    AFFECTED_CHOICES = [
        ('H', 'سالم'),
        ('C', 'مبتلا به سرطان'),
    ]

    name = models.CharField(max_length=100, verbose_name="نام")
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, verbose_name="جنسیت")
    affected = models.CharField(max_length=1, choices=AFFECTED_CHOICES, verbose_name="وضعیت بیماری")
    cancer_type = models.CharField(max_length=100, blank=True, verbose_name="نوع سرطان")
    age_diagnosis = models.PositiveIntegerField(null=True, blank=True, verbose_name="سن تشخیص سرطان")
    genes = models.CharField(max_length=200, blank=True, verbose_name="ژن‌های جهش‌یافته")
    age = models.PositiveIntegerField(verbose_name="سن فعلی یا سن فوت")
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, verbose_name="وضعیت زنده یا فوت شده")
    parents = models.ManyToManyField('self', symmetrical=False, blank=True, verbose_name="والدین")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "عضو خانواده"
        verbose_name_plural = "اعضای خانواده"


######################

class Family(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Individual(models.Model):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('U', 'Unknown'),
    ]

    family = models.ForeignKey(Family, on_delete=models.CASCADE, related_name='individuals')
    name = models.CharField(max_length=100)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    date_of_birth = models.DateField(null=True, blank=True)
    date_of_death = models.DateField(null=True, blank=True)
    affected = models.BooleanField(default=False)  # For genetic conditions
    notes = models.TextField(blank=True)

    # Relationships
    mother = models.ForeignKey('self', on_delete=models.SET_NULL,
                               null=True, blank=True, related_name='children_mother')
    father = models.ForeignKey('self', on_delete=models.SET_NULL,
                               null=True, blank=True, related_name='children_father')

    def __str__(self):
        return f"{self.name} ({self.get_gender_display()})"