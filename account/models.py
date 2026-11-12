from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.utils import timezone
from .validators import validate_image_upload


HEX_COLOR_VALIDATOR = RegexValidator(
    regex=r'^#[0-9A-Fa-f]{6}$',
    message='Use a six-digit hexadecimal color such as #066AC9.',
)

class Organization(models.Model):
    LANGUAGE_CHOICES = (
        ('fa', 'Persian'),
        ('en', 'English'),
        ('ar', 'Arabic'),
    )

    title = models.CharField(max_length=200)
    title_en = models.CharField(max_length=200, blank=True, null=True)
    title_ar = models.CharField(max_length=200, blank=True, null=True)
    code = models.CharField(max_length=10, unique=True)
    image = models.ImageField(upload_to="organization/images", blank=True, null=True, validators=[validate_image_upload])
    logo = models.ImageField(upload_to="organization/logo", blank=True, null=True, validators=[validate_image_upload])
    brand_primary_color = models.CharField(
        max_length=7,
        default='#066ac9',
        validators=[HEX_COLOR_VALIDATOR],
        help_text='Primary color used on organization login and registration pages.',
    )
    brand_accent_color = models.CharField(
        max_length=7,
        default='#0cbc87',
        validators=[HEX_COLOR_VALIDATOR],
        help_text='Accent color used for highlights and secondary actions.',
    )
    brand_surface_color = models.CharField(
        max_length=7,
        default='#f5f8fb',
        validators=[HEX_COLOR_VALIDATOR],
        help_text='Soft background color used by organization authentication pages.',
    )
    slug = models.SlugField(max_length=50, unique=True)  # For URL routing
    website = models.CharField(max_length=2000, blank=True, null=True)
    sentence = models.CharField(max_length=2000, blank=True, null=True)
    sentence_en = models.CharField(max_length=2000, blank=True, null=True)
    sentence_ar = models.CharField(max_length=2000, blank=True, null=True)
    default_language = models.CharField(
        max_length=5,
        choices=LANGUAGE_CHOICES,
        default='fa',
    )
    followup_sms_enabled = models.BooleanField(
        default=True,
        verbose_name='Enable follow-up SMS',
        help_text='Allow scheduled follow-up reminder SMS messages for this organization.',
    )
    pdf_report_sms_enabled = models.BooleanField(
        default=True,
        verbose_name='Send PDF report link by SMS',
        help_text='Allow sending the screening PDF report link by SMS for this organization.',
    )
    admin_user = models.OneToOneField(
        User,
        on_delete=models.SET_NULL,
        related_name='managed_organization',
        blank=True,
        null=True,
    )
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title  # Fixed: was self.user.title


class OrganizationMembership(models.Model):
    ROLE_CHOICES = (
        ('member', 'Member'),
        ('admin', 'Admin'),
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='organization_memberships',
    )
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='memberships',
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='member')
    is_active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'organization'),
                name='unique_organization_membership',
            ),
        ]
        indexes = [
            models.Index(fields=('organization', 'role', 'is_active')),
            models.Index(fields=('user', 'is_active')),
        ]

    def __str__(self):
        return f'{self.user} - {self.organization} ({self.role})'


class Profile(models.Model):
    LANGUAGE_CHOICES = Organization.LANGUAGE_CHOICES

    USER_TYPE = (
        ('Person', 'Person'),
        ('Organization', 'Organization')
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to="profiles/images", blank=True, null=True, validators=[validate_image_upload])
    code = models.CharField(max_length=20)
    phone_number = models.CharField(
        max_length=20,
        blank=True,
        help_text='Mobile number used for follow-up SMS notifications.',
    )
    GENDER_CHOICES = (
        ('Male', 'Male'),
        ('Female', 'Female'),
    )
    birth_date = models.DateField(
        null=True,
        blank=True,
        help_text='Used to calculate the screening age automatically.',
    )
    gender = models.CharField(
        max_length=10,
        choices=GENDER_CHOICES,
        default='Male',
        help_text='Used to show the relevant screening assessments.',
    )
    organization = models.ForeignKey(Organization, on_delete=models.SET_NULL, null=True, blank=True)
    user_type = models.CharField(max_length=50, choices=USER_TYPE, default='Person', blank=True, null=True)
    is_org_admin = models.BooleanField(default=False)
    language = models.CharField(
        max_length=5,
        choices=LANGUAGE_CHOICES,
        default='fa',
    )

    def __str__(self):
        return self.user.username

    @property
    def calculated_age(self):
        """Return the user's completed years from the saved birth date."""
        if not self.birth_date:
            return None
        today = timezone.localdate()
        return today.year - self.birth_date.year - (
            (today.month, today.day) < (self.birth_date.month, self.birth_date.day)
        )
