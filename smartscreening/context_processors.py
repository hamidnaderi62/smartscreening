from my_model.services.localization import (
    LANGUAGE_NAMES,
    language_for_request,
    language_switch_urls,
)


SITE_LABELS = {
    'fa': {
        'main_navigation': 'ناوبری اصلی',
        'select_language': 'انتخاب زبان',
        'choose_language': 'زبان خود را انتخاب کنید',
        'how_it_works': 'چطور کار می‌کند؟',
        'dashboard': 'داشبورد',
        'follow_up': 'پیگیری سلامت',
        'explore': 'دسترسی سریع',
        'privacy': 'حریم خصوصی شما',
    },
    'en': {
        'main_navigation': 'Main navigation',
        'select_language': 'Select language',
        'choose_language': 'Choose your language',
        'how_it_works': 'How it works',
        'dashboard': 'Dashboard',
        'follow_up': 'Follow-up',
        'explore': 'Explore',
        'privacy': 'Your privacy',
    },
    'ar': {
        'main_navigation': 'التنقل الرئيسي',
        'select_language': 'اختر اللغة',
        'choose_language': 'اختر لغتك',
        'how_it_works': 'كيف يعمل؟',
        'dashboard': 'لوحة التحكم',
        'follow_up': 'المتابعة',
        'explore': 'استكشف',
        'privacy': 'خصوصيتك',
    },
}


def language_context(request):
    language = language_for_request(request)
    return {
        'CURRENT_LANGUAGE': language,
        'LANGUAGE_NAMES': LANGUAGE_NAMES,
        'LANGUAGE_SWITCH_URLS': language_switch_urls(request),
        'IS_RTL': language in {'fa', 'ar'},
        'SITE_LABELS': SITE_LABELS.get(language, SITE_LABELS['fa']),
    }
