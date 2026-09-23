"""Dashboard and report views for screening results."""

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import render

from .assessment_catalog import ASSESSMENTS, get_assessment_or_404
from .models import MyModel
from .permissions import can_view_screening, screening_queryset_for_user
from .services.recommendations import get_related_resources
from .services.localization import (
    format_localized_date,
    language_for_request,
    normalize_language,
)


assessments = ASSESSMENTS


REPORT_LABELS = {
    'en': {
        'breast_5': '5-Year Breast Cancer Risk',
        'breast_lifetime': 'Lifetime Breast Cancer Risk',
        'colorectal': 'Colorectal Cancer Risk',
        'prostate': 'Prostate Cancer Risk',
        'cervical': 'Cervical Cancer Risk',
        'diabetes': 'Type 2 Diabetes Risk',
        'cardiovascular': 'Cardiovascular Risk',
        'skin': 'Skin Cancer Risk',
        'osteoporosis': 'Osteoporosis Risk',
        'ovarian': 'Ovarian Cancer Risk',
        'stomach': 'Stomach Cancer Risk',
        'stroke': 'Stroke Risk',
        'pancreatic': 'Pancreatic Cancer Risk',
        'change': 'Change',
        'suggested_content': 'Suggested Content',
        'title': 'Title',
        'duration': 'Duration',
        'content_type': 'Content Type',
        'details': 'Details',
        'minutes': 'minutes',
        'more_content': 'More Content',
        'suggested_specialists': 'Suggested Specialists',
        'specialist_name': 'Specialist Name',
        'specialty': 'Specialty',
        'status': 'Status',
        'more_info': 'More Info',
        'active': 'Active',
        'doctor_comment': "Doctor's Comment",
        'your_5_year': 'Your 5-Year Risk',
        'average_5_year': 'Average 5-Year Risk for Population',
        'your_lifetime': 'Your Lifetime Risk',
        'average_lifetime': 'Average Lifetime Risk for Population',
        'date': 'Date',
        'risk': 'Risk',
        'high_risk': 'High Risk',
        'low_risk': 'Low Risk',
        'no_risk': 'No Risk',
        'crc_risk': 'CRC Risk',
        'idf_score': 'IDF Score',
        'idf_history': 'IDF Score History',
        'content_language': 'en',
    },
    'fa': {
        'breast_5': 'ریسک 5 ساله سرطان سینه',
        'breast_lifetime': 'ریسک بلندمدت سرطان سینه',
        'colorectal': 'ریسک سرطان کلورکتال',
        'prostate': 'ریسک سرطان پروستات',
        'cervical': 'ریسک سرطان دهانه رحم',
        'diabetes': 'ریسک دیابت نوع 2',
        'cardiovascular': 'ریسک قلبی - عروقی',
        'skin': 'ریسک سرطان پوست',
        'osteoporosis': 'ریسک پوکی استخوان',
        'ovarian': 'ریسک سرطان تخمدان',
        'stomach': 'ریسک سرطان معده',
        'stroke': 'ریسک سکته مغزی',
        'pancreatic': 'ریسک سرطان پانکراس',
        'change': 'تغییرات',
        'suggested_content': 'محتوای پیشنهادی',
        'title': 'عنوان',
        'duration': 'مدت',
        'content_type': 'نوع محتوا',
        'details': 'جزئیات',
        'minutes': 'دقیقه',
        'more_content': 'محتوای بیشتر',
        'suggested_specialists': 'متخصصین پیشنهادی',
        'specialist_name': 'نام متخصص',
        'specialty': 'تخصص',
        'status': 'وضعیت',
        'more_info': 'اطلاعات بیشتر',
        'active': 'فعال',
        'doctor_comment': 'نظریه پزشک',
        'your_5_year': 'ریسک 5 ساله برای شما',
        'average_5_year': 'میانگین ریسک 5 ساله برای جمعیت',
        'your_lifetime': 'ریسک بلندمدت برای شما',
        'average_lifetime': 'میانگین ریسک بلندمدت برای جمعیت',
        'date': 'تاریخ',
        'risk': 'ریسک',
        'high_risk': 'ریسک بالا',
        'low_risk': 'ریسک کم',
        'no_risk': 'بدون ریسک',
        'crc_risk': 'ریسک CRC',
        'idf_score': 'امتیاز IDF',
        'idf_history': 'تاریخچه امتیاز IDF',
        'content_language': 'fa',
    },
    'ar': {
        'breast_5': 'خطر الإصابة بسرطان الثدي لمدة 5 سنوات',
        'breast_lifetime': 'خطر الإصابة بسرطان الثدي مدى الحياة',
        'colorectal': 'خطر الإصابة بسرطان القولون والمستقيم',
        'prostate': 'خطر الإصابة بسرطان البروستاتا',
        'cervical': 'خطر الإصابة بسرطان عنق الرحم',
        'diabetes': 'خطر الإصابة بالسكري من النوع الثاني',
        'cardiovascular': 'خطر الإصابة بأمراض القلب والأوعية الدموية',
        'skin': 'خطر الإصابة بسرطان الجلد',
        'osteoporosis': 'خطر الإصابة بهشاشة العظام',
        'ovarian': 'خطر الإصابة بسرطان المبيض',
        'stomach': 'خطر الإصابة بسرطان المعدة',
        'stroke': 'خطر الإصابة بالسكتة الدماغية',
        'pancreatic': 'خطر الإصابة بسرطان البنكرياس',
        'change': 'التغيير',
        'suggested_content': 'المحتوى المقترح',
        'title': 'العنوان',
        'duration': 'المدة',
        'content_type': 'نوع المحتوى',
        'details': 'التفاصيل',
        'minutes': 'دقيقة',
        'more_content': 'المزيد من المحتوى',
        'suggested_specialists': 'الأخصائيون المقترحون',
        'specialist_name': 'اسم الأخصائي',
        'specialty': 'التخصص',
        'status': 'الحالة',
        'more_info': 'مزيد من المعلومات',
        'active': 'نشط',
        'doctor_comment': 'تعليق الطبيب',
        'your_5_year': 'المخاطر لمدة 5 سنوات بالنسبة لك',
        'average_5_year': 'متوسط المخاطر لمدة 5 سنوات للسكان',
        'your_lifetime': 'المخاطر مدى الحياة بالنسبة لك',
        'average_lifetime': 'متوسط المخاطر مدى الحياة للسكان',
        'date': 'التاريخ',
        'risk': 'المخاطر',
        'high_risk': 'مخاطر عالية',
        'low_risk': 'مخاطر منخفضة',
        'no_risk': 'بدون مخاطر',
        'crc_risk': 'مخاطر CRC',
        'idf_score': 'درجة IDF',
        'idf_history': 'سجل درجات IDF',
        'content_language': 'ar',
    },
}


def _report_labels(language):
    return REPORT_LABELS[normalize_language(language)]


@login_required
def dashboard(request):
    return _dashboard_home(request)


@login_required
def dashboard_fa(request):
    return _dashboard_home(request, 'fa')


@login_required
def dashboard_en(request):
    return _dashboard_home(request, 'en')


@login_required
def dashboard_ar(request):
    return _dashboard_home(request, 'ar')


def _dashboard_home(request, language=None):
    language = normalize_language(language or language_for_request(request))
    return render(request, 'dashboard.html', {
        'base_template': 'base_raw.html',
        'selected_assessments': [],
    })


DETAIL_HISTORY_FIELDS = {
    1: (
        'gail_score_abs_5',
        'gail_score_ave_5',
        'gail_score_abs_90',
        'gail_score_ave_90',
    ),
    2: ('premm_score',),
    3: (
        'pbcg_score_high_cancer',
        'pbcg_score_low_cancer',
        'pbcg_score_no_cancer',
    ),
    4: ('cervical_cancer_score',),
    5: ('idf_score',),
    6: ('ascvd_score',),
    7: ('melanoma_cancer_score',),
    8: ('osteoporosis_score',),
    9: ('ovarian_cancer_score',),
    10: ('stomach_cancer_score',),
    11: ('stroke_score',),
    12: ('pancreatic_cancer_score',),
}


def _history_values(records, field_name):
    """Return numeric history in chronological order, including zero values."""
    return list(reversed([
        float(value)
        for value in (getattr(record, field_name) for record in records)
        if value is not None
    ]))


def _detail_report_context(request, assessment_id, language=None):
    language = normalize_language(language or language_for_request(request))
    my_models = MyModel.objects.filter(
        userid=request.user,
        selected_assessments_id__regex=fr'(^|, ){assessment_id}(,|$)'
    ).order_by('-created')[:5]

    assessment = get_assessment_or_404(assessment_id)
    context = {
        'base_template': 'base_raw.html',
        'report_labels': _report_labels(language),
        'date_history': list(reversed([
            format_localized_date(record.created, language)
            for record in my_models
        ])),
    }
    for field_name in DETAIL_HISTORY_FIELDS.get(assessment_id, ()):
        context[f'{field_name}_history'] = _history_values(my_models, field_name)

    related_contents, related_doctors = get_related_resources(
        settings.SMARTLIFE_BASE_URL,
        tags=assessment['tags'],
        speciality=assessment['speciality'],
    )

    context['related_contents'] = related_contents
    context['related_doctors'] = related_doctors
    return context


@login_required
def dashboard_detail_fa(request, assessment_id=None):
    return render(
        request,
        'dashboard_detail.html',
        _detail_report_context(request, assessment_id, 'fa'),
    )


@login_required
def dashboard_detail(request, assessment_id=None):
    return render(
        request,
        'dashboard_detail.html',
        _detail_report_context(request, assessment_id),
    )


@login_required
def dashboard_detail_en(request, assessment_id=None):
    return render(
        request,
        'dashboard_detail.html',
        _detail_report_context(request, assessment_id, 'en'),
    )


@login_required
def dashboard_detail_ar(request, assessment_id=None):
    return render(
        request,
        'dashboard_detail.html',
        _detail_report_context(request, assessment_id, 'ar'),
    )


def _can_view_screening_user(request, target_user):
    return can_view_screening(request.user, target_user)


def _report_queryset(request, code=None):
    """Return reports visible to this user, optionally for one organization user."""
    target_user_id = request.GET.get('user_id')
    if target_user_id:
        queryset = screening_queryset_for_user(
            request.user,
            target_user_id=target_user_id,
        )
        if not queryset.exists():
            raise PermissionDenied('You cannot view this screening report.')
        return queryset
    return screening_queryset_for_user(request.user, code=code)

COMPREHENSIVE_HISTORY_FIELDS = {
    str(assessment_id): field_names
    for assessment_id, field_names in DETAIL_HISTORY_FIELDS.items()
}


def _comprehensive_report_context(request, code=None, language=None):
    language = normalize_language(language or language_for_request(request))
    report_queryset = _report_queryset(request, code)
    my_models = list(report_queryset.order_by('-created')[:5])
    my_model_last = report_queryset.order_by('-created').first()
    if my_model_last is None:
        raise PermissionDenied('No screening report is available.')

    context = {
        'base_template': 'base_raw.html',
        'report_labels': _report_labels(language),
        'my_model_last': my_model_last,
        'date_history': list(reversed([
            format_localized_date(my_model.created, language)
            for my_model in my_models
        ])),
    }
    selected_ids = {
        value.strip()
        for value in (my_model_last.selected_assessments_id or '').split(',')
        if value.strip()
    }

    for assessment_id, field_names in COMPREHENSIVE_HISTORY_FIELDS.items():
        if assessment_id not in selected_ids:
            continue
        for field_name in field_names:
            context[f'{field_name}_history'] = _history_values(my_models, field_name)
    return context


@login_required
def dashboard_comprehensive_fa(request, code=None):
    return _render_comprehensive_report(request, code, 'fa')


@login_required
def dashboard_comprehensive(request, code=None):
    return _render_comprehensive_report(request, code)


@login_required
def dashboard_comprehensive_en(request, code=None):
    return _render_comprehensive_report(request, code, 'en')


@login_required
def dashboard_comprehensive_ar(request, code=None):
    return _render_comprehensive_report(request, code, 'ar')


def _render_comprehensive_report(request, code, language=None):
    return render(
        request,
        'dashboard_comprehensive.html',
        _comprehensive_report_context(request, code, language),
    )
