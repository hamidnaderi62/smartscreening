from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
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
    code = models.CharField(max_length=10)
    phone_number = models.CharField(
        max_length=20,
        blank=True,
        help_text='Mobile number used for follow-up SMS notifications.',
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
