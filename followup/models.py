from django.conf import settings
from django.db import models

from my_model.assessment_catalog import ASSESSMENTS
from my_model.models import MyModel


ASSESSMENT_CHOICES = tuple(
    (item['id'], item.get('title_en') or item.get('title', '').replace('_', ' '))
    for item in ASSESSMENTS
)


class FollowUpProgram(models.Model):
    """Admin-defined follow-up rules for one screening assessment."""

    assessment_id = models.PositiveSmallIntegerField(
        unique=True,
        choices=ASSESSMENT_CHOICES,
        help_text='The disease/assessment this follow-up program belongs to.',
    )
    title = models.CharField(max_length=200, help_text='Default/Farsi title.')
    title_en = models.CharField(max_length=200, blank=True)
    title_ar = models.CharField(max_length=200, blank=True)
    description = models.TextField(blank=True, help_text='Default/Farsi description.')
    description_en = models.TextField(blank=True)
    description_ar = models.TextField(blank=True)
    trigger_statuses = models.CharField(
        max_length=500,
        blank=True,
        help_text='Comma-separated English result statuses. Leave blank to apply to every result.',
    )
    send_pdf_sms = models.BooleanField(
        default=False,
        verbose_name='Send PDF report by SMS',
    )
    pdf_sms_delay_days = models.PositiveIntegerField(
        default=0,
        verbose_name='PDF SMS delay (days)',
    )
    is_active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('assessment_id',)

    def __str__(self):
        return self.display_title('en')

    def display_title(self, language='fa'):
        language = (language or 'fa').split('-', 1)[0]
        return (
            getattr(self, f'title_{language}', '')
            or self.title_en
            or self.title
            or dict(ASSESSMENT_CHOICES).get(self.assessment_id, 'Follow-up')
        )

    def display_description(self, language='fa'):
        language = (language or 'fa').split('-', 1)[0]
        return getattr(self, f'description_{language}', '') or self.description_en or self.description

    def matches_status(self, status):
        configured = {
            value.strip().casefold()
            for value in self.trigger_statuses.split(',')
            if value.strip()
        }
        return not configured or (status or '').strip().casefold() in configured


class FollowUpStep(models.Model):
    program = models.ForeignKey(
        FollowUpProgram,
        on_delete=models.CASCADE,
        related_name='steps',
    )
    order = models.PositiveIntegerField(default=1)
    delay_days = models.PositiveIntegerField(
        default=30,
        help_text='Days after the screening date when this reminder becomes due.',
    )
    title = models.CharField(max_length=200, help_text='Default/Farsi title.')
    title_en = models.CharField(max_length=200, blank=True)
    title_ar = models.CharField(max_length=200, blank=True)
    message = models.TextField(help_text='Default/Farsi SMS message.')
    message_en = models.TextField(blank=True)
    message_ar = models.TextField(blank=True)
    send_sms = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ('program', 'order')
        constraints = [
            models.UniqueConstraint(
                fields=('program', 'order'),
                name='unique_follow_up_step_order',
            ),
        ]

    def __str__(self):
        return f'{self.program} / {self.order} / {self.title_en or self.title}'

    def display_title(self, language='fa'):
        language = (language or 'fa').split('-', 1)[0]
        return getattr(self, f'title_{language}', '') or self.title_en or self.title

    def display_message(self, language='fa'):
        language = (language or 'fa').split('-', 1)[0]
        return getattr(self, f'message_{language}', '') or self.message_en or self.message


class FollowUpPlan(models.Model):
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )

    screening = models.ForeignKey(
        MyModel,
        on_delete=models.CASCADE,
        related_name='follow_up_plans',
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='follow_up_plans',
    )
    program = models.ForeignKey(
        FollowUpProgram,
        on_delete=models.PROTECT,
        related_name='plans',
    )
    result_status = models.CharField(max_length=120, blank=True)
    language = models.CharField(max_length=5, default='fa')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    started_at = models.DateTimeField(auto_now_add=True)
    next_reminder_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ('status', 'next_reminder_at', '-started_at')
        constraints = [
            models.UniqueConstraint(
                fields=('screening', 'program'),
                name='unique_follow_up_plan_per_screening_program',
            ),
        ]

    def __str__(self):
        return f'{self.user} / {self.program} / {self.status}'


class FollowUpReminder(models.Model):
    KIND_CHOICES = (
        ('pdf', 'PDF report'),
        ('step', 'Follow-up step'),
        ('manual', 'Manual SMS'),
    )
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('sent', 'Sent'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    )

    plan = models.ForeignKey(
        FollowUpPlan,
        on_delete=models.CASCADE,
        related_name='reminders',
        null=True,
        blank=True,
    )
    step = models.ForeignKey(
        FollowUpStep,
        on_delete=models.SET_NULL,
        related_name='reminders',
        null=True,
        blank=True,
    )
    kind = models.CharField(max_length=20, choices=KIND_CHOICES)
    scheduled_for = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    attempts = models.PositiveIntegerField(default=0)
    sent_at = models.DateTimeField(null=True, blank=True)
    provider_message_id = models.CharField(max_length=100, blank=True)
    provider_status = models.PositiveIntegerField(null=True, blank=True)
    last_error = models.TextField(blank=True)
    message = models.TextField(blank=True, help_text='Rendered SMS body kept for delivery auditing.')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('status', 'scheduled_for')
        constraints = [
            models.UniqueConstraint(
                fields=('plan', 'step', 'kind'),
                name='unique_follow_up_reminder_kind',
            ),
        ]

    def __str__(self):
        return f'{self.get_kind_display()} / {self.get_status_display()} / {self.scheduled_for:%Y-%m-%d}'
