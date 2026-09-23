"""Follow-up scheduling and Kavenegar SMS delivery."""

import logging
from datetime import timedelta
from urllib.parse import urljoin

import requests
from django.conf import settings
from django.utils import timezone

from my_model.assessment_catalog import ASSESSMENTS
from my_model.services.pdf_reports import selected_assessments_for_record
from my_model.services.localization import localized_reverse, normalize_language

from .models import FollowUpPlan, FollowUpProgram, FollowUpReminder

logger = logging.getLogger(__name__)


class SMSConfigurationError(Exception):
    """The SMS provider is not configured for sending."""


class SMSDeliveryError(Exception):
    """The SMS provider rejected or could not process a request."""


def normalize_phone_number(value):
    """Normalize common Iranian phone formats to the Kavenegar-compatible form."""
    value = ''.join(str(value or '').split()).replace('-', '')
    if value.startswith('00'):
        value = f'+{value[2:]}'
    elif value.startswith('09'):
        value = f'+98{value[1:]}'
    elif value.startswith('98'):
        value = f'+{value}'
    if value.startswith('+') and value[1:].isdigit() and 10 <= len(value[1:]) <= 15:
        return value
    if value.isdigit() and 10 <= len(value) <= 15:
        return f'+{value}'
    return ''


class KavenegarClient:
    """Small provider adapter for Kavenegar's REST SMS send endpoint."""

    def __init__(self):
        self.api_key = getattr(settings, 'KAVENEGAR_API_KEY', '')
        self.sender = getattr(settings, 'KAVENEGAR_SENDER', '')
        self.base_url = getattr(settings, 'KAVENEGAR_BASE_URL', 'https://api.kavenegar.com').rstrip('/')
        self.timeout = getattr(settings, 'KAVENEGAR_TIMEOUT', 15)

    def send(self, receptor, message, localid=None):
        if not self.api_key:
            raise SMSConfigurationError('KAVENEGAR_API_KEY is not configured.')
        url = f'{self.base_url}/v1/{self.api_key}/sms/send.json'
        payload = {'receptor': receptor, 'message': message}
        if self.sender:
            payload['sender'] = self.sender
        if localid:
            payload['localid'] = localid
        try:
            response = requests.post(url, data=payload, timeout=self.timeout)
            response.raise_for_status()
            result = response.json()
        except (requests.RequestException, ValueError) as exc:
            raise SMSDeliveryError(str(exc)) from exc

        provider_return = result.get('return') or {}
        status = provider_return.get('status')
        if status != 200:
            raise SMSDeliveryError(provider_return.get('message') or f'Kavenegar status: {status}')
        entries = result.get('entries') or []
        entry = entries[0] if isinstance(entries, list) and entries else {}
        return {
            'message_id': str(entry.get('messageid') or ''),
            'status': entry.get('status'),
            'status_text': entry.get('statustext') or provider_return.get('message', ''),
        }


def _profile_language(user, fallback='fa'):
    return normalize_language(getattr(getattr(user, 'profile', None), 'language', None) or fallback)


def _absolute_url(path):
    base_url = getattr(settings, 'SMARTSCREENING_PUBLIC_URL', '').strip()
    if not base_url:
        raise SMSConfigurationError('SMARTSCREENING_PUBLIC_URL is not configured.')
    return urljoin(base_url.rstrip('/') + '/', path.lstrip('/'))


def _pdf_url(screening, language):
    return _absolute_url(
        localized_reverse(
            'my_model:pdf_report',
            language,
            kwargs={'model_id': screening.pk},
        )
    )


def _follow_up_url(language):
    return _absolute_url(localized_reverse('followup:list', language))


def _render_step_message(reminder):
    plan = reminder.plan
    language = normalize_language(plan.language)
    user = plan.user
    values = {
        'name': user.first_name or user.username,
        'program': plan.program.display_title(language),
        'pdf_url': _pdf_url(plan.screening, language),
        'follow_up_url': _follow_up_url(language),
    }
    template = reminder.step.display_message(language) if reminder.step else ''
    try:
        return template.format(**values)
    except (KeyError, ValueError):
        logger.warning('Invalid follow-up SMS placeholders for reminder %s', reminder.pk)
        return template


def _render_pdf_message(reminder):
    plan = reminder.plan
    language = normalize_language(plan.language)
    url = _pdf_url(plan.screening, language)
    messages = {
        'fa': f'گزارش غربالگری سلامت شما آماده است: {url}',
        'en': f'Your health screening report is ready: {url}',
        'ar': f'تقرير الفحص الصحي الخاص بك جاهز: {url}',
    }
    return messages[language]


def render_reminder_message(reminder):
    if reminder.kind == 'pdf':
        return _render_pdf_message(reminder)
    if reminder.kind == 'manual':
        return _render_pdf_message(reminder)
    if reminder.kind == 'step':
        return _render_step_message(reminder)
    return reminder.message


def _assessment_statuses(record, selected_assessments=None):
    selected = selected_assessments or selected_assessments_for_record(record, ASSESSMENTS, 'en')
    return {item['id']: (item.get('status_en') or '') for item in selected}


def schedule_follow_up_for_screening(record, selected_assessments=None, language=None):
    """Create plans and reminder rows for all matching active programs."""
    language = normalize_language(language or _profile_language(record.userid))
    statuses = _assessment_statuses(record, selected_assessments)
    programs = FollowUpProgram.objects.filter(is_active=True, assessment_id__in=statuses)
    created_plans = []

    for program in programs:
        status = statuses.get(program.assessment_id, '')
        if not program.matches_status(status):
            continue
        plan, created = FollowUpPlan.objects.get_or_create(
            screening=record,
            program=program,
            defaults={
                'user': record.userid,
                'result_status': status,
                'language': language,
            },
        )
        if not created:
            continue
        created_plans.append(plan)
        if program.send_pdf_sms:
            FollowUpReminder.objects.create(
                plan=plan,
                kind='pdf',
                scheduled_for=record.created + timedelta(days=program.pdf_sms_delay_days),
            )
        for step in program.steps.filter(is_active=True, send_sms=True):
            FollowUpReminder.objects.create(
                plan=plan,
                step=step,
                kind='step',
                scheduled_for=record.created + timedelta(days=step.delay_days),
            )
        plan.next_reminder_at = plan.reminders.filter(status='pending').order_by('scheduled_for').values_list('scheduled_for', flat=True).first()
        plan.save(update_fields=('next_reminder_at',))
    return created_plans


def send_follow_up_reminder(reminder):
    """Send one pending/failed reminder and persist the provider result."""
    if reminder.status not in {'pending', 'failed'}:
        return reminder
    reminder.attempts += 1
    reminder.last_error = ''
    try:
        phone = normalize_phone_number(getattr(getattr(reminder.plan.user, 'profile', None), 'phone_number', ''))
        if not phone:
            raise SMSDeliveryError('User has no valid phone number.')
        message = render_reminder_message(reminder)
        result = KavenegarClient().send(phone, message, localid=reminder.pk)
        reminder.status = 'sent'
        reminder.sent_at = timezone.now()
        reminder.provider_message_id = result['message_id']
        reminder.provider_status = result['status']
        reminder.message = message
    except (SMSConfigurationError, SMSDeliveryError) as exc:
        reminder.status = 'failed'
        reminder.last_error = str(exc)
        logger.warning('Follow-up SMS %s failed: %s', reminder.pk, exc)
    reminder.save(update_fields=(
        'attempts', 'status', 'sent_at', 'provider_message_id',
        'provider_status', 'last_error', 'message', 'updated',
    ))
    if reminder.plan_id:
        plan = reminder.plan
        plan.next_reminder_at = plan.reminders.filter(status='pending').order_by('scheduled_for').values_list('scheduled_for', flat=True).first()
        plan.save(update_fields=('next_reminder_at',))
    return reminder


def process_due_reminders(limit=100, retry_failed=False):
    queryset = FollowUpReminder.objects.filter(
        scheduled_for__lte=timezone.now(),
    ).filter(status='failed' if retry_failed else 'pending').select_related(
        'plan__user__profile', 'plan__program', 'step',
    ).order_by('scheduled_for')[:limit]
    reminders = list(queryset)
    for reminder in reminders:
        send_follow_up_reminder(reminder)
    return reminders


def queue_manual_pdf_sms(plan):
    """Queue an immediate PDF SMS for an admin-triggered send."""
    reminder, _ = FollowUpReminder.objects.update_or_create(
        plan=plan,
        step=None,
        kind='manual',
        defaults={
            'scheduled_for': timezone.now(),
            'status': 'pending',
            'message': '',
            'last_error': '',
        },
    )
    return send_follow_up_reminder(reminder)
