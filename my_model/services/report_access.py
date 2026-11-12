"""Signed, language-aware links for direct screening PDF access."""

import hashlib
import secrets
from datetime import timedelta

from django.conf import settings
from django.core import signing
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils import timezone

from .localization import localized_reverse, normalize_language
from ..models import MyModel, ScreeningReportShortLink


REPORT_ACCESS_SALT = 'my_model.screening-report-access'


def make_report_access_token(screening, language='fa'):
    """Create a tamper-resistant bearer token for one screening report."""
    return signing.dumps(
        {
            'screening_id': screening.pk,
            'user_id': screening.userid_id,
            'language': normalize_language(language),
        },
        salt=REPORT_ACCESS_SALT,
    )


def screening_from_report_token(token):
    max_age = getattr(settings, 'REPORT_ACCESS_TOKEN_MAX_AGE', 60 * 60 * 24 * 365)
    try:
        payload = signing.loads(token, salt=REPORT_ACCESS_SALT, max_age=max_age)
    except signing.BadSignature as exc:
        raise Http404('Invalid or expired report link.') from exc

    if not isinstance(payload, dict) or not payload.get('screening_id') or not payload.get('user_id'):
        raise Http404('Invalid report link.')
    return get_object_or_404(
        MyModel,
        pk=payload['screening_id'],
        userid_id=payload['user_id'],
    ), normalize_language(payload.get('language'))


def report_access_url(screening, language='fa'):
    token = make_report_access_token(screening, language)
    return localized_reverse(
        'my_model:pdf_report_access',
        language,
        kwargs={'token': token},
    )


def _short_link_max_age():
    return getattr(settings, 'REPORT_ACCESS_TOKEN_MAX_AGE', 60 * 60 * 24 * 365)


def _new_short_code():
    return secrets.token_urlsafe(9)


def report_short_url(screening, language='fa'):
    """Issue a compact bearer URL, storing only a hash of its random code."""
    language = normalize_language(language)
    code = _new_short_code()
    ScreeningReportShortLink.objects.create(
        screening=screening,
        token_hash=hashlib.sha256(code.encode('ascii')).hexdigest(),
        language=language,
    )
    return reverse('short_pdf_report', kwargs={'code': code})


def screening_from_short_report_code(code):
    """Resolve a short bearer code and reject unknown or expired links."""
    digest = hashlib.sha256(code.encode('ascii', errors='ignore')).hexdigest()
    link = get_object_or_404(
        ScreeningReportShortLink.objects.select_related('screening'),
        token_hash=digest,
    )
    if timezone.now() - link.created > timedelta(seconds=_short_link_max_age()):
        raise Http404('Invalid or expired report link.')
    return link.screening, normalize_language(link.language)
