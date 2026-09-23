import re

from django.contrib.auth import authenticate, get_user_model, login, logout
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.db import transaction
from django.utils.translation import gettext as _

from .models import Organization, OrganizationMembership
from .forms import RegistrationForm
from .views import ensure_profile
from my_model.services.localization import (
    language_for_request,
    localize_objects,
    localized_reverse,
    normalize_language,
)


User = get_user_model()


ORG_LABELS = {
    'fa': {
        'page_login': 'غربالگری هوشمند سلامت - ورود',
        'page_register': 'غربالگری هوشمند سلامت - ثبت نام',
        'site_title': 'غربالگری هوشمند سلامت',
        'tagline': 'پیشگیری هوشمندانه ، زندگی بهتر',
        'login_title': 'ورود به حساب کاربری',
        'login_intro': 'از دیدن شما خوشحالم! لطفا با حساب کاربری خود وارد شوید.',
        'register': 'ثبت نام',
        'register_intro': 'از دیدن شما خوشحالم! لطفا با حساب کاربری خود ثبت نام کنید.',
        'username': 'نام کاربری',
        'username_required': 'نام کاربری *',
        'username_required_message': 'لطفاً نام کاربری خود را وارد کنید',
        'email': 'ایمیل',
        'password_required': 'رمز عبور *',
        'password_help': 'رمز عبور شما باید حداقل 8 کاراکتر باشد',
        'password_required_message': 'لطفا رمز عبور را وارد کنید',
        'password_length_message': 'رمز عبور باید حداقل 8 کاراکتر باشد',
        'confirm_password_required': 'تایید رمز عبور *',
        'remember_me': 'مرا به خاطر بسپار',
        'forgot_password': 'رمز خود را فراموش کرده اید؟',
        'no_account': 'حساب کاربری ندارید؟',
        'have_account': 'آیا قبلا ثبت نام کرده اید؟',
        'terms_prefix': 'با ثبت نام',
        'terms': 'شرایط و قوانین سایت',
        'terms_suffix': 'را خواهید پذیرفت.',
        'register_users': 'ثبت نام کاربران',
        'login_users': 'ورود کاربران و مدیر سازمان',
        'organization_dashboard': 'داشبورد سازمان',
        'organization_welcome': 'به صفحه اختصاصی سازمان خوش آمدید.',
        'not_member': 'شما عضو این سازمان نیستید.',
        'invalid_login': 'نام کاربری یا رمز عبور اشتباه است.',
        'login': 'ورود',
        'organization_access': 'ورود امن به فضای سازمانی شما',
        'organization_code': 'کد سازمان',
        'change_language': 'زبان',
        'visit_website': 'وب‌سایت سازمان',
        'powered_by': 'ارائه شده توسط غربالگری هوشمند سلامت',
    },
    'en': {
        'page_login': 'Smart Health Screening - Organization Login',
        'page_register': 'Smart Health Screening - Organization Registration',
        'site_title': 'Smart Health Screening',
        'tagline': 'Smart prevention, better living',
        'login_title': 'Sign in to your account',
        'login_intro': 'Welcome back! Please sign in with your account.',
        'register': 'Register',
        'register_intro': 'Welcome! Please register your account.',
        'username': 'Username',
        'username_required': 'Username *',
        'username_required_message': 'Please enter your username',
        'email': 'Email',
        'password_required': 'Password *',
        'password_help': 'Your password must be at least 8 characters',
        'password_required_message': 'Please enter your password',
        'password_length_message': 'Password must be at least 8 characters',
        'confirm_password_required': 'Confirm password *',
        'remember_me': 'Remember me',
        'forgot_password': 'Forgot your password?',
        'no_account': "Don't have an account?",
        'have_account': 'Already registered?',
        'terms_prefix': 'By registering, you accept the',
        'terms': 'site terms and conditions',
        'terms_suffix': '.',
        'register_users': 'Register users',
        'login_users': 'User and administrator login',
        'organization_dashboard': 'Organization dashboard',
        'organization_welcome': 'Welcome to the organization page.',
        'not_member': 'You are not a member of this organization.',
        'invalid_login': 'Incorrect username or password.',
        'login': 'Sign in',
        'organization_access': 'Secure access to your organization portal',
        'organization_code': 'Organization code',
        'change_language': 'Language',
        'visit_website': 'Organization website',
        'powered_by': 'Powered by Smart Health Screening',
    },
    'ar': {
        'page_login': 'الفحص الصحي الذكي - تسجيل الدخول للمؤسسة',
        'page_register': 'الفحص الصحي الذكي - التسجيل في المؤسسة',
        'site_title': 'الفحص الصحي الذكي',
        'tagline': 'وقاية ذكية، حياة أفضل',
        'login_title': 'تسجيل الدخول إلى الحساب',
        'login_intro': 'مرحباً بعودتك! يرجى تسجيل الدخول بحسابك.',
        'register': 'إنشاء حساب',
        'register_intro': 'مرحباً! يرجى إنشاء حسابك.',
        'username': 'اسم المستخدم',
        'username_required': 'اسم المستخدم *',
        'username_required_message': 'يرجى إدخال اسم المستخدم',
        'email': 'البريد الإلكتروني',
        'password_required': 'كلمة المرور *',
        'password_help': 'يجب أن تتكون كلمة المرور من 8 أحرف على الأقل',
        'password_required_message': 'يرجى إدخال كلمة المرور',
        'password_length_message': 'يجب أن تتكون كلمة المرور من 8 أحرف على الأقل',
        'confirm_password_required': 'تأكيد كلمة المرور *',
        'remember_me': 'تذكرني',
        'forgot_password': 'هل نسيت كلمة المرور؟',
        'no_account': 'ليس لديك حساب؟',
        'have_account': 'هل سجلت من قبل؟',
        'terms_prefix': 'بالتسجيل، فإنك توافق على',
        'terms': 'شروط وأحكام الموقع',
        'terms_suffix': '.',
        'register_users': 'تسجيل المستخدمين',
        'login_users': 'تسجيل دخول المستخدم والمدير',
        'organization_dashboard': 'لوحة تحكم المؤسسة',
        'organization_welcome': 'مرحباً بك في صفحة المؤسسة.',
        'not_member': 'أنت لست عضواً في هذه المؤسسة.',
        'invalid_login': 'اسم المستخدم أو كلمة المرور غير صحيحة.',
        'login': 'تسجيل الدخول',
        'organization_access': 'دخول آمن إلى بوابة مؤسستك',
        'organization_code': 'رمز المؤسسة',
        'change_language': 'اللغة',
        'visit_website': 'موقع المؤسسة',
        'powered_by': 'مدعوم بواسطة الفحص الصحي الذكي',
    },
}


def _safe_brand_color(value, fallback):
    """Keep organization-controlled CSS values limited to hex colors."""
    return value if re.fullmatch(r'#[0-9A-Fa-f]{6}', value or '') else fallback


def _organization_page_context(request, organization, language, **extra):
    language = normalize_language(language)
    localized_organization = localize_objects(
        [organization],
        ('title', 'sentence'),
        language,
    )[0]
    page_name = extra.pop('page_name', 'login')
    context = {
        'organization': localized_organization,
        'organization_language': language,
        'org_labels': ORG_LABELS[language],
        'organization_brand': {
            'primary': _safe_brand_color(organization.brand_primary_color, '#066ac9'),
            'accent': _safe_brand_color(organization.brand_accent_color, '#0cbc87'),
            'surface': _safe_brand_color(organization.brand_surface_color, '#f5f8fb'),
        },
        'organization_languages': [
            {
                'code': code,
                'name': {'fa': 'فارسی', 'en': 'English', 'ar': 'العربية'}[code],
                'url': localized_reverse(
                    f'account:org_{page_name}',
                    code,
                    kwargs={'org_slug': organization.slug},
                ),
            }
            for code in ('fa', 'en', 'ar')
        ],
    }
    context.update(extra)
    return context


def _organization_context(request, organization):
    request.session['organization_id'] = organization.id
    request.session['organization_slug'] = organization.slug
    request.session['user_type'] = getattr(request.user.profile, 'user_type', 'Person')
    request.session['username'] = request.user.username


def organization_home_fa(request, org_slug):
    return _organization_home(request, org_slug, 'fa')


def organization_home(request, org_slug):
    return _organization_home(
        request,
        org_slug,
        language_for_request(request),
    )


def _organization_home(request, org_slug, language):
    organization = get_object_or_404(Organization, slug=org_slug, is_active=True)
    return render(
        request,
        'account/organization_home.html',
        _organization_page_context(request, organization, language),
    )


def org_register_fa(request, org_slug):
    return _org_register(request, org_slug, 'fa')


def org_register(request, org_slug):
    return _org_register(request, org_slug, language_for_request(request))


def _org_register(request, org_slug, language):
    organization = get_object_or_404(Organization, slug=org_slug, is_active=True)

    if request.user.is_authenticated:
        return redirect(localized_reverse(
            'account:organization_home',
            language,
            kwargs={'org_slug': organization.slug},
        ))

    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                user = form.save()
                profile = ensure_profile(user, organization=organization)
                profile.phone_number = form.cleaned_data.get('phone_number', '')
                profile.save(update_fields=('phone_number',))
                OrganizationMembership.objects.update_or_create(
                    user=user,
                    organization=organization,
                    defaults={'role': 'member', 'is_active': True},
                )
            login(request, user)
            _organization_context(request, organization)
            return redirect(localized_reverse(
                'account:organization_home',
                language,
                kwargs={'org_slug': organization.slug},
            ))
        for error in form.errors.get_json_data().values():
            for message in error:
                messages.error(request, message['message'])
    else:
        form = RegistrationForm()

    return render(
        request,
        'account/org_register.html',
        _organization_page_context(request, organization, language, page_name='register', form=form, org_labels={
            **ORG_LABELS[normalize_language(language)],
            'page_title': ORG_LABELS[normalize_language(language)]['page_register'],
        }),
    )


def org_login_fa(request, org_slug):
    return _org_login(request, org_slug, 'fa')


def org_login(request, org_slug):
    return _org_login(request, org_slug, language_for_request(request))


def _org_login(request, org_slug, language):
    organization = get_object_or_404(Organization, slug=org_slug, is_active=True)

    if request.user.is_authenticated:
        return redirect(localized_reverse(
            'account:organization_home',
            language,
            kwargs={'org_slug': organization.slug},
        ))

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        remember_me = request.POST.get('remember_me')
        user = authenticate(request, username=username, password=password)
        membership = OrganizationMembership.objects.filter(
            user=user,
            organization=organization,
            is_active=True,
        ).first() if user else None

        if user and membership:
            login(request, user)
            request.session.set_expiry(None if remember_me == 'on' else 0)
            _organization_context(request, organization)
            return redirect(localized_reverse(
                'account:organization_home',
                language,
                kwargs={'org_slug': organization.slug},
            ))

        if user and not membership:
            messages.error(request, ORG_LABELS[normalize_language(language)]['not_member'])
        else:
            messages.error(request, ORG_LABELS[normalize_language(language)]['invalid_login'])

    labels = {
        **ORG_LABELS[normalize_language(language)],
        'page_title': ORG_LABELS[normalize_language(language)]['page_login'],
    }
    return render(
        request,
        'account/org_login.html',
        _organization_page_context(request, organization, language, page_name='login', org_labels=labels),
    )


def org_logout_fa(request):
    org_slug = request.session.get('organization_slug')
    logout(request)
    if org_slug:
        return redirect(localized_reverse(
            'account:org_login', 'fa', kwargs={'org_slug': org_slug},
        ))
    return redirect(localized_reverse('home:home', 'fa'))


def org_logout(request):
    org_slug = request.session.get('organization_slug')
    language = language_for_request(request)
    logout(request)
    if org_slug:
        return redirect(localized_reverse(
            'account:org_login', language, kwargs={'org_slug': org_slug},
        ))
    return redirect(localized_reverse('home:home', language))


org_logout_fa1 = org_logout_fa
