"""Shared language helpers for the screening platform."""

from copy import copy
from datetime import datetime
from urllib.parse import urlsplit, urlunsplit

from django.urls import reverse
from django.utils import timezone
from django.utils.translation import get_language, override
from persiantools.jdatetime import JalaliDate, JalaliDateTime

DEFAULT_LANGUAGE = 'fa'
SUPPORTED_LANGUAGES = ('fa', 'en', 'ar')
LANGUAGE_NAMES = {
    'fa': 'فارسی',
    'en': 'English',
    'ar': 'العربية',
}

DASHBOARD_TEMPLATE = 'dashboard.html'

PERSIAN_DIGITS = str.maketrans('0123456789', '۰۱۲۳۴۵۶۷۸۹')
ARABIC_MONTHS = (
    '', 'يناير', 'فبراير', 'مارس', 'أبريل', 'مايو', 'يونيو',
    'يوليو', 'أغسطس', 'سبتمبر', 'أكتوبر', 'نوفمبر', 'ديسمبر',
)


def _native_digits(value, language):
    """Use Persian digits where they are conventional for a Persian date."""
    return value.translate(PERSIAN_DIGITS) if language == 'fa' else value


def _localized_datetime_value(value):
    if isinstance(value, datetime) and timezone.is_aware(value):
        return timezone.localtime(value)
    return value


def format_localized_date(value, language=None):
    """Format a date using the calendar and language selected by the user.

    Persian uses the Jalali calendar; English uses a readable Gregorian date;
    Arabic uses a Gregorian date with Arabic month names.
    """
    if not value:
        return ''
    language = normalize_language(language or get_language())
    value = _localized_datetime_value(value)

    if language == 'fa':
        jalali = JalaliDate(value.date() if isinstance(value, datetime) else value, locale='fa')
        return _native_digits(jalali.strftime('%Y/%m/%d'), language)
    if language == 'ar':
        month = ARABIC_MONTHS[value.month]
        return f'{value.day:02d} {month} {value.year}'
    return value.strftime('%b %d, %Y')


def format_localized_datetime(value, language=None):
    """Format a date and time using the selected language/calendar."""
    if not value:
        return ''
    language = normalize_language(language or get_language())
    value = _localized_datetime_value(value)
    if not isinstance(value, datetime):
        return format_localized_date(value, language)

    if language == 'fa':
        jalali = JalaliDateTime.to_jalali(value)
        return _native_digits(jalali.strftime('%Y/%m/%d - %H:%M'), language)
    if language == 'ar':
        month = ARABIC_MONTHS[value.month]
        return f'{value.day:02d} {month} {value.year} - {value:%H:%M}'
    return value.strftime('%b %d, %Y · %H:%M')


def normalize_language(language):
    """Return a supported base language code, falling back to Persian."""
    language = (language or '').lower().replace('_', '-')
    language = language.split('-', 1)[0]
    return language if language in SUPPORTED_LANGUAGES else DEFAULT_LANGUAGE


def language_for_request(request):
    """Return the active language, honoring the profile when no URL language exists."""
    active = normalize_language(getattr(request, 'LANGUAGE_CODE', None) or get_language())
    path_language = request.path.strip('/').split('/', 1)[0]
    user = getattr(request, 'user', None)
    if path_language in SUPPORTED_LANGUAGES:
        return path_language
    if active != DEFAULT_LANGUAGE or not getattr(user, 'is_authenticated', False):
        return active
    profile_language = getattr(getattr(user, 'profile', None), 'language', None)
    return normalize_language(profile_language or active)


def localized_value(item, field_name, language=None, default=''):
    """Read a catalog field using the active language with safe fallbacks."""
    language = normalize_language(language or get_language())
    for candidate in (f'{field_name}_{language}', f'{field_name}_en', field_name):
        value = item.get(candidate)
        if value not in (None, ''):
            return value
    return default


def localize_assessment(item, language=None):
    """Add language-neutral display fields to one assessment catalog item."""
    localized = copy(item)
    language = normalize_language(language or get_language())
    for field_name in ('title', 'desc', 'status', 'recommendation', 'desc_file'):
        value = localized_value(item, field_name, language)
        if value != '':
            localized[f'display_{field_name}'] = value
    localized['language'] = language
    return localized


def localize_assessments(assessments, language=None):
    return [localize_assessment(item, language) for item in assessments]


def localize_objects(objects, fields, language=None):
    """Attach display values to model instances without changing stored data."""
    language = normalize_language(language or get_language())
    localized_objects = list(objects)
    for obj in localized_objects:
        for field_name in fields:
            candidates = [f'{field_name}_{language}']
            if language != 'en':
                candidates.append(f'{field_name}_en')
            candidates.append(field_name)
            value = next(
                (
                    getattr(obj, candidate, None)
                    for candidate in candidates
                    if getattr(obj, candidate, None) not in (None, '')
                ),
                '',
            )
            setattr(obj, f'display_{field_name}', value)
    return localized_objects


def language_switch_urls(request):
    """Build language switch links without losing the current page."""
    parsed_url = urlsplit(request.get_full_path())
    path = parsed_url.path or '/'
    path_parts = path.lstrip('/').split('/', 1)
    if path_parts[0] in SUPPORTED_LANGUAGES:
        remaining_path = f"/{path_parts[1]}" if len(path_parts) > 1 else '/'
    else:
        remaining_path = path

    # Older screening pages encoded the language in the route name itself
    # (for example ``question_fa``). A language prefix alone cannot change
    # those routes, so always switch them to their shared canonical route.
    legacy_routes = {
        '/my_model/question_fa': '/my_model/screenings/questions/',
        '/my_model/question_en': '/my_model/screenings/questions/',
        '/my_model/question_ar': '/my_model/screenings/questions/',
        '/my_model/screening_list_fa': '/my_model/screenings/',
        '/my_model/screening_list_en': '/my_model/screenings/',
        '/my_model/screening_list_ar': '/my_model/screenings/',
        '/my_model/calculate_my_model': '/my_model/screenings/',
        '/my_model/calculate_my_model/': '/my_model/screenings/',
        '/my_model/screenings/calculate/': '/my_model/screenings/',
    }
    calculation_routes = {
        '/my_model/calculate_my_model',
        '/my_model/calculate_my_model/',
        '/my_model/screenings/calculate/',
    }
    session = getattr(request, 'session', None)
    result_id = session.get('last_screening_id') if session and remaining_path in calculation_routes else None
    remaining_path = (
        f'/my_model/screenings/result/{result_id}/'
        if result_id
        else legacy_routes.get(remaining_path, remaining_path)
    )

    def localized_url(code):
        localized_path = f'/{code}/' if remaining_path == '/' else f'/{code}{remaining_path}'
        return urlunsplit(('', '', localized_path, parsed_url.query, ''))

    return [
        {
            'code': code,
            'name': LANGUAGE_NAMES[code],
            'url': localized_url(code),
        }
        for code in SUPPORTED_LANGUAGES
    ]


def localized_reverse(viewname, language=None, args=None, kwargs=None):
    """Reverse a canonical i18n URL using an explicit language."""
    with override(normalize_language(language or get_language())):
        return reverse(viewname, args=args, kwargs=kwargs)


def dashboard_template(language):
    """Return the shared dashboard template for any supported language."""
    normalize_language(language)
    return DASHBOARD_TEMPLATE


def legacy_template(template_base, language=None):
    """Return the old localized template name during the migration period."""
    language = normalize_language(language or get_language())
    return f'{template_base}_{language}.html'
