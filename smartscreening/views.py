from django.shortcuts import render
from django.views.i18n import set_language as django_set_language
from django.views.decorators.http import require_POST

from my_model.services.localization import SUPPORTED_LANGUAGES, normalize_language


def home(request):
    return render(request, 'home.html', context={})


@require_POST
def set_language(request):
    """Use Django's language switcher and persist the choice for signed-in users."""
    requested_language = (request.POST.get('language') or '').lower()
    language = normalize_language(requested_language)
    if requested_language in SUPPORTED_LANGUAGES and request.user.is_authenticated:
        profile = getattr(request.user, 'profile', None)
        if profile and profile.language != language:
            profile.language = language
            profile.save(update_fields=('language',))
    return django_set_language(request)
