from django.db import models


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
    generation = models.IntegerField(default=0, null=True, blank=True)

    def save(self, *args, **kwargs):
        # First save the instance to get an ID
        super().save(*args, **kwargs)

        # Now handle the generation calculation
        if self.parents.exists():
            self.generation = max(p.generation for p in self.parents.all()) + 1
            # Need to save again if generation changed
            super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "FamilyMember"
        verbose_name_plural = "FamilyMembers"