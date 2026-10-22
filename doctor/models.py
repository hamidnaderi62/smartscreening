from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models


class DoctorSpecialization(models.Model):
    code = models.SlugField(max_length=80, unique=True)
    title = models.CharField(max_length=160)
    title_fa = models.CharField(max_length=160, blank=True)
    title_ar = models.CharField(max_length=160, blank=True)
    assessment_ids = models.JSONField(default=list, blank=True)
    is_active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('title',)

    def __str__(self):
        return self.title

    @property
    def assessment_id_set(self):
        values = self.assessment_ids if isinstance(self.assessment_ids, list) else []
        return {int(value) for value in values if str(value).isdigit()}


class DoctorProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='doctor_profile',
    )
    display_name = models.CharField(max_length=180)
    license_number = models.CharField(max_length=100, unique=True)
    phone_number = models.CharField(max_length=40, blank=True)
    clinic_name = models.CharField(max_length=180, blank=True)
    clinic_address = models.TextField(blank=True)
    bio = models.TextField(blank=True)
    image = models.ImageField(upload_to='doctors/', blank=True, null=True)
    specializations = models.ManyToManyField(
        DoctorSpecialization,
        related_name='doctors',
        blank=True,
    )
    is_active = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('display_name',)

    def __str__(self):
        return self.display_name

    @property
    def covered_assessment_ids(self):
        return {
            assessment_id
            for specialization in self.specializations.all()
            if specialization.is_active
            for assessment_id in specialization.assessment_id_set
        }

    @property
    def is_available(self):
        return self.is_active and self.is_verified and self.user.is_active


class DoctorReferral(models.Model):
    STATUS_PENDING = 'pending'
    STATUS_REVIEWED = 'reviewed'
    STATUS_CLOSED = 'closed'
    STATUS_CANCELLED = 'cancelled'
    STATUS_CHOICES = (
        (STATUS_PENDING, 'Pending review'),
        (STATUS_REVIEWED, 'Reviewed'),
        (STATUS_CLOSED, 'Closed'),
        (STATUS_CANCELLED, 'Cancelled'),
    )

    patient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='doctor_referrals',
    )
    screening = models.ForeignKey(
        'my_model.MyModel',
        on_delete=models.CASCADE,
        related_name='doctor_referrals',
    )
    doctor = models.ForeignKey(
        DoctorProfile,
        on_delete=models.PROTECT,
        related_name='referrals',
    )
    assessment_id = models.PositiveSmallIntegerField(validators=[MinValueValidator(1)])
    result_status = models.CharField(max_length=500, blank=True)
    patient_message = models.TextField(blank=True)
    doctor_comment = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('-created',)
        constraints = [
            models.UniqueConstraint(
                fields=('screening', 'doctor', 'assessment_id'),
                name='unique_screening_doctor_assessment_referral',
            ),
        ]
        indexes = [
            models.Index(fields=('doctor', 'status', '-created')),
            models.Index(fields=('patient', '-created')),
        ]

    def __str__(self):
        return f'{self.screening.code} → {self.doctor.display_name}'
