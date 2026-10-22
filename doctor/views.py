from functools import wraps

from django.contrib import messages
from django.contrib.auth import authenticate, get_user_model, login, logout
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from my_model.assessment_catalog import ASSESSMENTS, get_assessment_or_404
from my_model.models import MyModel
from my_model.services.localization import language_for_request, localized_reverse, localized_value, normalize_language
from my_model.services.pdf_reports import selected_assessments_for_record

from .forms import DoctorCommentForm, DoctorReferralForm
from .models import DoctorProfile, DoctorReferral
from .services import screening_assessment_ids, suggest_doctors_for_assessment


LABELS = {
    'en': {
        'login_title': 'Doctor portal', 'username': 'Username or email', 'password': 'Password',
        'login': 'Sign in', 'invalid_login': 'Invalid credentials or doctor account is not active.',
        'dashboard': 'Doctor dashboard', 'welcome': 'Welcome, {name}', 'pending': 'Pending referrals',
        'reviewed': 'Reviewed', 'total': 'Total referrals', 'no_referrals': 'No referrals match this filter.',
        'all': 'All', 'patient': 'Patient', 'disease': 'Screening', 'status': 'Status',
        'received': 'Received', 'open': 'Open referral', 'recommendations': 'Recommended doctors',
        'choose_intro': 'Choose a doctor for follow-up on each screening result.', 'choose': 'Choose this doctor',
        'message': 'Message for doctor (optional)', 'sent': 'Referral sent successfully.',
        'already_sent': 'This referral already exists.', 'no_doctors': 'No verified doctor is currently available for this screening.',
        'back': 'Back', 'comment': 'Doctor comment', 'save_comment': 'Save comment',
        'comment_saved': 'Comment saved.', 'patient_info': 'Patient screening information',
        'screening_code': 'Screening code', 'result': 'Result', 'update_status': 'Update status',
        'status_updated': 'Status updated.', 'pending_label': 'Pending review', 'reviewed_label': 'Reviewed',
        'closed_label': 'Closed', 'cancelled_label': 'Cancelled', 'logout': 'Sign out', 'questions': 'Questions and answers', 'question': 'Question', 'answer': 'Answer',
    },
    'fa': {
        'login_title': 'درگاه پزشکان', 'username': 'نام کاربری یا ایمیل', 'password': 'رمز عبور',
        'login': 'ورود', 'invalid_login': 'اطلاعات ورود نادرست است یا حساب پزشک فعال نیست.',
        'dashboard': 'داشبورد پزشک', 'welcome': 'خوش آمدید، {name}', 'pending': 'ارجاع‌های در انتظار',
        'reviewed': 'بررسی‌شده', 'total': 'کل ارجاع‌ها', 'no_referrals': 'ارجاعی با این فیلتر وجود ندارد.',
        'all': 'همه', 'patient': 'بیمار', 'disease': 'غربالگری', 'status': 'وضعیت',
        'received': 'دریافت‌شده', 'open': 'مشاهده ارجاع', 'recommendations': 'پزشکان پیشنهادی',
        'choose_intro': 'برای پیگیری هر نتیجه غربالگری یک پزشک انتخاب کنید.', 'choose': 'انتخاب این پزشک',
        'message': 'پیام برای پزشک (اختیاری)', 'sent': 'ارجاع با موفقیت ارسال شد.',
        'already_sent': 'این ارجاع قبلاً ثبت شده است.', 'no_doctors': 'در حال حاضر پزشک تأییدشده‌ای برای این غربالگری موجود نیست.',
        'back': 'بازگشت', 'comment': 'نظر پزشک', 'save_comment': 'ذخیره نظر',
        'comment_saved': 'نظر ذخیره شد.', 'patient_info': 'اطلاعات غربالگری بیمار',
        'screening_code': 'کد غربالگری', 'result': 'نتیجه', 'update_status': 'به‌روزرسانی وضعیت',
        'status_updated': 'وضعیت به‌روزرسانی شد.', 'pending_label': 'در انتظار بررسی', 'reviewed_label': 'بررسی‌شده',
        'closed_label': 'بسته‌شده', 'cancelled_label': 'لغوشده', 'logout': 'خروج', 'questions': 'پرسش‌ها و پاسخ‌ها', 'question': 'پرسش', 'answer': 'پاسخ',
    },
    'ar': {
        'login_title': 'بوابة الطبيب', 'username': 'اسم المستخدم أو البريد الإلكتروني', 'password': 'كلمة المرور',
        'login': 'تسجيل الدخول', 'invalid_login': 'بيانات الدخول غير صحيحة أو حساب الطبيب غير نشط.',
        'dashboard': 'لوحة الطبيب', 'welcome': 'مرحباً، {name}', 'pending': 'الإحالات قيد الانتظار',
        'reviewed': 'تمت المراجعة', 'total': 'إجمالي الإحالات', 'no_referrals': 'لا توجد إحالات بهذا التصفية.',
        'all': 'الكل', 'patient': 'المريض', 'disease': 'الفحص', 'status': 'الحالة',
        'received': 'تاريخ الاستلام', 'open': 'فتح الإحالة', 'recommendations': 'الأطباء المقترحون',
        'choose_intro': 'اختر طبيباً لمتابعة كل نتيجة فحص.', 'choose': 'اختيار هذا الطبيب',
        'message': 'رسالة للطبيب (اختياري)', 'sent': 'تم إرسال الإحالة بنجاح.',
        'already_sent': 'تم إنشاء هذه الإحالة مسبقاً.', 'no_doctors': 'لا يوجد طبيب موثق متاح حالياً لهذا الفحص.',
        'back': 'رجوع', 'comment': 'تعليق الطبيب', 'save_comment': 'حفظ التعليق',
        'comment_saved': 'تم حفظ التعليق.', 'patient_info': 'معلومات فحص المريض',
        'screening_code': 'رمز الفحص', 'result': 'النتيجة', 'update_status': 'تحديث الحالة',
        'status_updated': 'تم تحديث الحالة.', 'pending_label': 'قيد المراجعة', 'reviewed_label': 'تمت المراجعة',
        'closed_label': 'مغلقة', 'cancelled_label': 'ملغاة', 'logout': 'تسجيل الخروج', 'questions': 'الأسئلة والأجوبة', 'question': 'السؤال', 'answer': 'الإجابة',
    },
}


def _labels(request):
    language = normalize_language(language_for_request(request))
    return language, LABELS[language]


def _screening_answer_sections(screening, assessment_title, language="en"):
    section_names = {
        "en": {"demographic": "Demographic information", "lifestyle": "Lifestyle information", "medical": "Medical history", "assessments": "Assessment answers"},
        "fa": {"demographic": "اطلاعات جمعیت‌شناختی", "lifestyle": "سبک زندگی", "medical": "سوابق پزشکی", "assessments": "پاسخ‌های ارزیابی"},
        "ar": {"demographic": "المعلومات الديموغرافية", "lifestyle": "نمط الحياة", "medical": "التاريخ الطبي", "assessments": "إجابات الفحص"},
    }.get(language, {})
    snapshot = screening.get_screening_data()
    sections = []
    for section_name, values in snapshot.items():
        if section_name == "assessments":
            values = values.get(assessment_title, {}) if isinstance(values, dict) else {}
        if not isinstance(values, dict):
            continue
        rows = [
            {"question": entry.get("question"), "answer": entry.get("answer")}
            for entry in values.values()
            if isinstance(entry, dict) and entry.get("question") and entry.get("answer") is not None
            and entry.get("question_key") not in {"risk_score", "max_score", "risk_level"}
        ]
        if rows:
            sections.append({"name": section_names.get(section_name, section_name.replace("_", " ").title()), "rows": rows})
    return sections


def _doctor_for_user(user):
    try:
        doctor = user.doctor_profile
    except (AttributeError, DoctorProfile.DoesNotExist):
        return None
    return doctor if doctor.is_available else None


def doctor_required(view):
    @wraps(view)
    @login_required
    def wrapped(request, *args, **kwargs):
        doctor = _doctor_for_user(request.user)
        if doctor is None:
            language, _ = _labels(request)
            return redirect(localized_reverse('doctor:login', language))
        request.doctor_profile = doctor
        return view(request, *args, **kwargs)
    return wrapped


def doctor_login(request):
    language, labels = _labels(request)
    if request.user.is_authenticated and _doctor_for_user(request.user):
        return redirect(localized_reverse('doctor:dashboard', language))
    if request.method == 'POST':
        identifier = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        username = identifier
        if '@' in identifier:
            user = get_user_model().objects.filter(email__iexact=identifier).first()
            username = user.get_username() if user else identifier
        user = authenticate(request, username=username, password=password)
        if user and _doctor_for_user(user):
            login(request, user)
            return redirect(localized_reverse('doctor:dashboard', language))
        messages.error(request, labels['invalid_login'])
    return render(request, 'doctor/login.html', {'labels': labels, 'current_language': language})


@login_required
def doctor_logout(request):
    language, _ = _labels(request)
    logout(request)
    return redirect(localized_reverse('doctor:login', language))


@doctor_required
def doctor_dashboard(request):
    language, labels = _labels(request)
    doctor = request.doctor_profile
    referrals = doctor.referrals.select_related('patient', 'screening').all()
    status_filter = request.GET.get('status', 'all')
    if status_filter in dict(DoctorReferral.STATUS_CHOICES):
        referrals = referrals.filter(status=status_filter)
    referrals = list(referrals)
    for referral in referrals:
        assessment = get_assessment_or_404(referral.assessment_id)
        referral.display_assessment_title = localized_value(assessment, "title", language, assessment["title"])
        localized_result = next((item for item in selected_assessments_for_record(referral.screening, ASSESSMENTS, language) if item["id"] == referral.assessment_id), None)
        referral.display_result_status = (localized_result or {}).get("display_status") or referral.result_status
    return render(request, 'doctor/dashboard.html', {
        'labels': labels, 'current_language': language, 'doctor': doctor,
        'referrals': referrals, 'status_filter': status_filter,
        'counts': {
            'pending': doctor.referrals.filter(status=DoctorReferral.STATUS_PENDING).count(),
            'reviewed': doctor.referrals.filter(status=DoctorReferral.STATUS_REVIEWED).count(),
            'total': doctor.referrals.count(),
        },
        'status_labels': dict(DoctorReferral.STATUS_CHOICES),
    })


@login_required
def recommendations(request, screening_id):
    language, labels = _labels(request)
    screening = get_object_or_404(MyModel, pk=screening_id, userid=request.user)
    selected = selected_assessments_for_record(screening, ASSESSMENTS, language)
    referrals = {
        referral.assessment_id: referral
        for referral in screening.doctor_referrals.select_related('doctor').filter(patient=request.user)
    }
    disease_rows = [
        {
            'assessment': assessment,
            'doctors': suggest_doctors_for_assessment(assessment['id']),
            'referral': referrals.get(assessment['id']),
        }
        for assessment in selected
    ]
    return render(request, 'doctor/recommendations.html', {
        'labels': labels, 'current_language': language, 'screening': screening,
        'disease_rows': disease_rows, 'referral_form': DoctorReferralForm(),
    })


@require_POST
@login_required
def create_referral(request, screening_id, doctor_id, assessment_id):
    language, labels = _labels(request)
    screening = get_object_or_404(MyModel, pk=screening_id, userid=request.user)
    if assessment_id not in screening_assessment_ids(screening):
        raise Http404('Assessment is not part of this screening.')
    doctor = get_object_or_404(DoctorProfile, pk=doctor_id, is_active=True, is_verified=True, user__is_active=True)
    if assessment_id not in doctor.covered_assessment_ids:
        raise PermissionDenied('Doctor does not cover this assessment.')
    result = next((item for item in selected_assessments_for_record(screening, ASSESSMENTS, language) if item['id'] == assessment_id), None)
    with transaction.atomic():
        referral, created = DoctorReferral.objects.get_or_create(
            patient=request.user, screening=screening, doctor=doctor, assessment_id=assessment_id,
            defaults={'result_status': (result or {}).get('status_en', '')},
        )
        if not created:
            messages.info(request, labels['already_sent'])
        else:
            form = DoctorReferralForm(request.POST, instance=referral)
            if form.is_valid():
                form.save()
                messages.success(request, labels['sent'])
            else:
                referral.delete()
    return redirect(localized_reverse('doctor:recommendations', language, kwargs={'screening_id': screening_id}))


@doctor_required
def referral_detail(request, referral_id):
    language, labels = _labels(request)
    referral = get_object_or_404(
        DoctorReferral.objects.select_related('patient', 'screening', 'doctor'),
        pk=referral_id, doctor=request.doctor_profile,
    )
    selected = next((item for item in selected_assessments_for_record(referral.screening, ASSESSMENTS, language) if item['id'] == referral.assessment_id), None)
    return render(request, 'doctor/referral_detail.html', {
        'labels': labels, 'current_language': language, 'referral': referral,
        'assessment': selected or get_assessment_or_404(referral.assessment_id),
        'comment_form': DoctorCommentForm(instance=referral),
        'status_choices': DoctorReferral.STATUS_CHOICES,
        'answer_sections': _screening_answer_sections(referral.screening, (selected or {}).get('title', ''), language),
    })


@require_POST
@doctor_required
def save_comment(request, referral_id):
    language, labels = _labels(request)
    referral = get_object_or_404(DoctorReferral, pk=referral_id, doctor=request.doctor_profile)
    form = DoctorCommentForm(request.POST, instance=referral)
    if form.is_valid() and form.cleaned_data['doctor_comment'].strip():
        referral = form.save(commit=False)
        referral.status = DoctorReferral.STATUS_REVIEWED
        referral.reviewed_at = timezone.now()
        referral.save(update_fields=('doctor_comment', 'status', 'reviewed_at', 'updated'))
        messages.success(request, labels['comment_saved'])
    return redirect(localized_reverse('doctor:referral_detail', language, kwargs={'referral_id': referral.pk}))

@require_POST
@doctor_required
def update_status(request, referral_id):
    language, labels = _labels(request)
    referral = get_object_or_404(DoctorReferral, pk=referral_id, doctor=request.doctor_profile)
    status = request.POST.get('status')
    if status in dict(DoctorReferral.STATUS_CHOICES):
        referral.status = status
        if status == DoctorReferral.STATUS_REVIEWED and not referral.reviewed_at:
            referral.reviewed_at = timezone.now()
        referral.save(update_fields=('status', 'reviewed_at', 'updated'))
        messages.success(request, labels['status_updated'])
    return redirect(localized_reverse('doctor:referral_detail', language, kwargs={'referral_id': referral.pk}))
