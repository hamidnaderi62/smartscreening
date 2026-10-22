"""Signed, language-aware links for direct screening PDF access."""

from django.conf import settings
from django.core import signing
from django.http import Http404
from django.shortcuts import get_object_or_404

from .localization import localized_reverse, normalize_language
from ..models import MyModel


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
