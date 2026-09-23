import hashlib
import logging

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.core.cache import cache
from django.shortcuts import redirect, render
from django.utils.translation import gettext as _

from my_model.services.localization import (
    language_for_request,
    localized_reverse,
    normalize_language,
)


logger = logging.getLogger(__name__)


def _login_cache_key(request, username):
    value = f'{username.strip().lower()}:{request.META.get("REMOTE_ADDR", "unknown")}'
    digest = hashlib.sha256(value.encode('utf-8')).hexdigest()
    return f'login-attempts:{digest}'


def _increment_login_attempts(cache_key):
    if cache.add(cache_key, 1, timeout=settings.LOGIN_ATTEMPTS_TIMEOUT):
        return 1
    try:
        return cache.incr(cache_key)
    except ValueError:
        cache.set(cache_key, 1, timeout=settings.LOGIN_ATTEMPTS_TIMEOUT)
        return 1


def _login_view(request, *, template_name, success_url, locked_message, invalid_message):
    if request.user.is_authenticated:
        return redirect(success_url)

    username = ''
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        cache_key = _login_cache_key(request, username)
        attempts = cache.get(cache_key, 0)

        if attempts >= settings.MAX_LOGIN_ATTEMPTS:
            messages.error(request, locked_message)
            logger.warning(
                'Login locked for remote address %s',
                request.META.get('REMOTE_ADDR', 'unknown'),
            )
            return render(request, template_name)

        user = authenticate(request, username=username, password=password)
        if user is not None:
            cache.delete(cache_key)
            login(request, user)
            request.session.set_expiry(
                None if request.POST.get('remember_me') == 'on' else 0,
            )
            logger.info('Successful login for user id %s', user.pk)
            return redirect(success_url)

        attempts = _increment_login_attempts(cache_key)
        logger.warning(
            'Failed login for remote address %s; attempt %s',
            request.META.get('REMOTE_ADDR', 'unknown'),
            attempts,
        )
        messages.error(request, invalid_message)

    return render(request, template_name)


def _localized_login_view(request, language):
    """Render the single styled login page in the active language."""
    return _login_view(
        request,
        template_name='account/login.html',
        success_url=localized_reverse('home:home', language),
        locked_message={
            'fa': 'تعداد تلاش‌های شما بیش از حد بوده است. لطفاً بعداً تلاش کنید.',
            'ar': 'تم تجاوز عدد محاولات تسجيل الدخول. حاول لاحقاً.',
            'en': _('Too many login attempts. Please try again later.'),
        }[language],
        invalid_message={
            'fa': 'نام کاربری یا رمز عبور اشتباه است.',
            'ar': 'اسم المستخدم أو كلمة المرور غير صحيحة.',
            'en': _('Incorrect username or password.'),
        }[language],
    )


def user_login(request):
    """Language-neutral login endpoint used by the i18n URL set."""
    return _localized_login_view(
        request,
        normalize_language(language_for_request(request)),
    )


def user_login_fa(request):
    return _localized_login_view(request, 'fa')


def user_login_en(request):
    return _localized_login_view(request, 'en')


def user_login_ar(request):
    return _localized_login_view(request, 'ar')
