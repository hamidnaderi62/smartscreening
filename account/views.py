from django.contrib.auth import get_user_model, login, logout
from django.contrib import messages
from django.db import transaction
from django.shortcuts import redirect, render

from .auth_views import user_login_ar, user_login_en, user_login_fa
from .forms import RegistrationForm
from .models import OrganizationMembership, Profile
from my_model.services.localization import (
    language_for_request,
    localized_reverse,
    normalize_language,
)


User = get_user_model()


def ensure_profile(user, organization=None, user_type='Person', is_org_admin=False):
    profile, _ = Profile.objects.get_or_create(
        user=user,
        defaults={
            'code': str(user.pk),
            'language': getattr(organization, 'default_language', 'fa'),
        },
    )
    changed_fields = []
    if not profile.code:
        profile.code = str(user.pk)
        changed_fields.append('code')
    if organization is not None and profile.organization_id != organization.id:
        profile.organization = organization
        changed_fields.append('organization')
    if profile.user_type != user_type:
        profile.user_type = user_type
        changed_fields.append('user_type')
    if profile.is_org_admin != is_org_admin:
        profile.is_org_admin = is_org_admin
        changed_fields.append('is_org_admin')
    if changed_fields:
        profile.save(update_fields=changed_fields)

    if organization is not None:
        OrganizationMembership.objects.update_or_create(
            user=user,
            organization=organization,
            defaults={
                'role': 'admin' if is_org_admin else 'member',
                'is_active': True,
            },
        )
    return profile


def _registration_view(request, template_name, redirect_name):
    if request.user.is_authenticated:
        return redirect(redirect_name)

    form = RegistrationForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        with transaction.atomic():
            user = form.save()
            profile = ensure_profile(user)
            profile.phone_number = form.cleaned_data.get('phone_number', '')
            profile.save(update_fields=('phone_number',))
        login(request, user)
        return redirect(redirect_name)

    if form.errors:
        for errors in form.errors.get_json_data().values():
            for error in errors:
                messages.error(request, error['message'])
    return render(request, template_name, {'form': form})


def _localized_registration_view(request, language):
    return _registration_view(
        request,
        'account/register.html',
        localized_reverse('home:home', language),
    )


def user_register_fa(request):
    return _localized_registration_view(request, 'fa')


def user_register_en(request):
    return _localized_registration_view(request, 'en')


def user_register_ar(request):
    return _localized_registration_view(request, 'ar')


def user_register(request):
    language = normalize_language(language_for_request(request))
    return _localized_registration_view(request, language)


def user_logout(request):
    language = normalize_language(language_for_request(request))
    logout(request)
    return redirect(localized_reverse('home:home', language))


def user_logout_fa(request):
    logout(request)
    return redirect(localized_reverse('home:home', 'fa'))


def user_logout_en(request):
    logout(request)
    return redirect(localized_reverse('home:home', 'en'))


def user_logout_ar(request):
    logout(request)
    return redirect(localized_reverse('home:home', 'ar'))


user_logout_fa1 = user_logout_fa
