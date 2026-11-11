from functools import wraps

from django.contrib import messages
from django.contrib.auth import authenticate, get_user_model, login, logout
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Case, IntegerField, Q, Value, When
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from my_model.assessment_catalog import ASSESSMENTS
from my_model.models import MyModel
from my_model.services.localization import language_for_request, localized_reverse, normalize_language
from my_model.services.pdf_reports import SCORE_FIELDS, selected_assessments_for_record
from my_model.services.questionnaire_translations import localized_answer, localized_question

from .forms import DoctorCommentForm, DoctorReferralForm
from .models import DoctorProfile, DoctorReferral
from .services import active_gp_doctors_for_screening, screening_assessment_ids


LABELS = {
    'en': {
        'login_title': 'Doctor portal', 'username': 'Username or email', 'password': 'Password',
        'login': 'Sign in', 'invalid_login': 'Invalid credentials or doctor account is not active.',
        'dashboard': 'Doctor dashboard', 'welcome': 'Welcome, {name}', 'pending': 'Pending referrals',
        'dashboard_intro': 'Your patients’ screening referrals, ready for your review.',
        'reviewed': 'Reviewed', 'total': 'Total referrals', 'no_referrals': 'No referrals match this filter.',
        'all': 'All', 'patient': 'Patient', 'disease': 'Screening', 'status': 'Status',
        'received': 'Received', 'open': 'Open referral', 'recommendations': 'Recommended doctors',
        'choose_intro': 'Choose one active general practitioner to review your complete screening result and follow-up.', 'choose': 'Choose this GP',
        'message': 'Message for doctor (optional)', 'sent': 'Referral sent successfully.',
        'already_sent': 'This referral already exists.', 'no_doctors': 'No verified doctor is currently available for this screening.',
        'back': 'Back', 'comment': 'Doctor comment and recommendation', 'save_comment': 'Save comment',
        'score': 'Score', 'recommendation': 'Suggested next step', 'screening_overview': 'Screening overview',
        'report_sections': 'Selected screening areas', 'no_answers': 'No saved question-and-answer details are available.',
        'follow_up_started': 'Plan started', 'next_reminder': 'Next reminder', 'patient_note': 'Message from patient',
        'follow_up_summary': 'Follow-up plans linked to this screening.',
        'note_pdf_hint': 'Your saved note is included in the patient’s screening PDF report.',
        'comment_saved': 'Comment saved.', 'patient_info': 'Patient screening information',
        'screening_code': 'Screening code', 'result': 'Result', 'update_status': 'Update status',
        'status_updated': 'Status updated.', 'pending_label': 'Pending review', 'reviewed_label': 'Reviewed',
        'closed_label': 'Closed', 'cancelled_label': 'Cancelled', 'logout': 'Sign out', 'questions': 'Questions and answers', 'question': 'Question', 'answer': 'Answer',
        'follow_up': 'Follow-up plans', 'no_follow_up': 'No follow-up plan has been created yet.',
        'screening_report': 'Screening report', 'screening_areas': 'screening areas',
        'no_report_details': 'No assessment details were recorded for this screening.',
        'search_doctors': 'Find a doctor', 'search_placeholder': 'Search by doctor or clinic name',
        'search': 'Search', 'clear_search': 'Clear', 'last_selected': 'Previously selected',
        'general_practitioner': 'General practitioner', 'doctor_count': 'doctors available',
        'no_search_results': 'No doctors match your search. Try another name.',
    },
    'fa': {
        'login_title': 'درگاه پزشکان', 'username': 'نام کاربری یا ایمیل', 'password': 'رمز عبور',
        'login': 'ورود', 'invalid_login': 'اطلاعات ورود نادرست است یا حساب پزشک فعال نیست.',
        'dashboard': 'داشبورد پزشک', 'welcome': 'خوش آمدید، {name}', 'pending': 'ارجاع‌های در انتظار',
        'dashboard_intro': 'ارجاع‌های غربالگری بیماران شما برای بررسی آماده است.',
        'reviewed': 'بررسی‌شده', 'total': 'کل ارجاع‌ها', 'no_referrals': 'ارجاعی با این فیلتر وجود ندارد.',
        'all': 'همه', 'patient': 'بیمار', 'disease': 'غربالگری', 'status': 'وضعیت',
        'received': 'دریافت‌شده', 'open': 'مشاهده ارجاع', 'recommendations': 'پزشکان پیشنهادی',
        'choose_intro': 'یک پزشک عمومی فعال را برای بررسی نتیجه کامل غربالگری و پیگیری انتخاب کنید.', 'choose': 'انتخاب این پزشک عمومی',
        'message': 'پیام برای پزشک (اختیاری)', 'sent': 'ارجاع با موفقیت ارسال شد.',
        'already_sent': 'این ارجاع قبلاً ثبت شده است.', 'no_doctors': 'در حال حاضر پزشک تأییدشده‌ای برای این غربالگری موجود نیست.',
        'back': 'بازگشت', 'comment': 'نظر و توصیه پزشک', 'save_comment': 'ذخیره نظر',
        'score': 'امتیاز', 'recommendation': 'اقدام پیشنهادی', 'screening_overview': 'خلاصه غربالگری',
        'report_sections': 'حوزه‌های انتخاب‌شده', 'no_answers': 'جزئیات پرسش و پاسخ ذخیره‌شده‌ای در دسترس نیست.',
        'follow_up_started': 'شروع برنامه', 'next_reminder': 'یادآوری بعدی', 'patient_note': 'پیام بیمار',
        'follow_up_summary': 'برنامه‌های پیگیری مرتبط با این غربالگری.',
        'note_pdf_hint': 'نظر ذخیره‌شده شما در فایل PDF غربالگری بیمار درج می‌شود.',
        'comment_saved': 'نظر ذخیره شد.', 'patient_info': 'اطلاعات غربالگری بیمار',
        'screening_code': 'کد غربالگری', 'result': 'نتیجه', 'update_status': 'به‌روزرسانی وضعیت',
        'status_updated': 'وضعیت به‌روزرسانی شد.', 'pending_label': 'در انتظار بررسی', 'reviewed_label': 'بررسی‌شده',
        'closed_label': 'بسته‌شده', 'cancelled_label': 'لغوشده', 'logout': 'خروج', 'questions': 'پرسش‌ها و پاسخ‌ها', 'question': 'پرسش', 'answer': 'پاسخ',
        'follow_up': 'برنامه‌های پیگیری', 'no_follow_up': 'هنوز برنامه پیگیری ایجاد نشده است.',
        'screening_report': 'گزارش غربالگری', 'screening_areas': 'حوزه غربالگری',
        'no_report_details': 'جزئیات ارزیابی برای این غربالگری ثبت نشده است.',
        'search_doctors': 'جستجوی پزشک', 'search_placeholder': 'جستجو بر اساس نام پزشک یا مرکز درمانی',
        'search': 'جستجو', 'clear_search': 'پاک کردن', 'last_selected': 'پزشک انتخاب‌شده قبلی',
        'general_practitioner': 'پزشک عمومی', 'doctor_count': 'پزشک در دسترس',
        'no_search_results': 'پزشکی با این مشخصات پیدا نشد. نام دیگری را جستجو کنید.',
    },
    'ar': {
        'login_title': 'بوابة الطبيب', 'username': 'اسم المستخدم أو البريد الإلكتروني', 'password': 'كلمة المرور',
        'login': 'تسجيل الدخول', 'invalid_login': 'بيانات الدخول غير صحيحة أو حساب الطبيب غير نشط.',
        'dashboard': 'لوحة الطبيب', 'welcome': 'مرحباً، {name}', 'pending': 'الإحالات قيد الانتظار',
        'dashboard_intro': 'إحالات الفحص الخاصة بمرضاك جاهزة لمراجعتك.',
        'reviewed': 'تمت المراجعة', 'total': 'إجمالي الإحالات', 'no_referrals': 'لا توجد إحالات بهذا التصفية.',
        'all': 'الكل', 'patient': 'المريض', 'disease': 'الفحص', 'status': 'الحالة',
        'received': 'تاريخ الاستلام', 'open': 'فتح الإحالة', 'recommendations': 'الأطباء المقترحون',
        'choose_intro': 'اختر طبيباً عاماً نشطاً لمراجعة نتيجة الفحص كاملة ومتابعة حالتك.', 'choose': 'اختيار هذا الطبيب العام',
        'message': 'رسالة للطبيب (اختياري)', 'sent': 'تم إرسال الإحالة بنجاح.',
        'already_sent': 'تم إنشاء هذه الإحالة مسبقاً.', 'no_doctors': 'لا يوجد طبيب موثق متاح حالياً لهذا الفحص.',
        'back': 'رجوع', 'comment': 'ملاحظة وتوصية الطبيب', 'save_comment': 'حفظ التعليق',
        'score': 'النتيجة', 'recommendation': 'الخطوة المقترحة', 'screening_overview': 'ملخص الفحص',
        'report_sections': 'مجالات الفحص المختارة', 'no_answers': 'لا تتوفر تفاصيل محفوظة للأسئلة والأجوبة.',
        'follow_up_started': 'بدء الخطة', 'next_reminder': 'التذكير التالي', 'patient_note': 'رسالة المريض',
        'follow_up_summary': 'خطط المتابعة المرتبطة بهذا الفحص.',
        'note_pdf_hint': 'ستُضاف ملاحظتك المحفوظة إلى تقرير الفحص بصيغة PDF للمريض.',
        'comment_saved': 'تم حفظ التعليق.', 'patient_info': 'معلومات فحص المريض',
        'screening_code': 'رمز الفحص', 'result': 'النتيجة', 'update_status': 'تحديث الحالة',
        'status_updated': 'تم تحديث الحالة.', 'pending_label': 'قيد المراجعة', 'reviewed_label': 'تمت المراجعة',
        'closed_label': 'مغلقة', 'cancelled_label': 'ملغاة', 'logout': 'تسجيل الخروج', 'questions': 'الأسئلة والأجوبة', 'question': 'السؤال', 'answer': 'الإجابة',
        'follow_up': 'خطط المتابعة', 'no_follow_up': 'لم يتم إنشاء خطة متابعة بعد.',
        'screening_report': 'تقرير الفحص', 'screening_areas': 'مجالات الفحص',
        'no_report_details': 'لم يتم تسجيل تفاصيل التقييم لهذا الفحص.',
        'search_doctors': 'ابحث عن طبيب', 'search_placeholder': 'ابحث باسم الطبيب أو العيادة',
        'search': 'بحث', 'clear_search': 'مسح', 'last_selected': 'تم اختياره سابقاً',
        'general_practitioner': 'طبيب عام', 'doctor_count': 'أطباء متاحون',
        'no_search_results': 'لا يوجد أطباء يطابقون هذا البحث. جرّب اسماً آخر.',
    },
}


def _labels(request):
    language = normalize_language(language_for_request(request))
    return language, LABELS[language]


def _screening_answer_sections(screening, language="en", selected_assessments=None, labels=None):
    labels = labels or LABELS.get(language, LABELS['en'])
    section_names = {
        "en": {"demographic": "Demographic information", "lifestyle": "Lifestyle information", "medical": "Medical history", "assessments": "Assessment answers"},
        "fa": {"demographic": "اطلاعات جمعیت‌شناختی", "lifestyle": "سبک زندگی", "medical": "سوابق پزشکی", "assessments": "پاسخ‌های ارزیابی"},
        "ar": {"demographic": "المعلومات الديموغرافية", "lifestyle": "نمط الحياة", "medical": "التاريخ الطبي", "assessments": "إجابات الفحص"},
    }.get(language, {})
    snapshot = screening.get_screening_data()
    localized_assessment_titles = {
        item.get('title'): item.get('display_title') or item.get('title_en') or item.get('title')
        for item in (selected_assessments or [])
    }

    def localized_rows(values, assessment_title=None):
        rows = []
        for key, entry in values.items():
            if not isinstance(entry, dict) or 'question' not in entry or entry.get('answer') is None:
                continue
            question_key = entry.get('question_key') or key
            if question_key in {'risk_score', 'max_score', 'risk_level'}:
                continue
            if question_key == 'risk_status':
                question = labels['result']
            elif question_key == 'recommendation':
                question = labels['recommendation']
            else:
                question = localized_question(
                    question_key,
                    language,
                    fallback=entry.get('question'),
                )

            assessment = next(
                (item for item in (selected_assessments or []) if item.get('title') == assessment_title),
                {},
            )
            if question_key == 'risk_status':
                answer = assessment.get('display_status') or assessment.get('status_en') or entry.get('answer')
            elif question_key == 'recommendation':
                answer = assessment.get('display_recommendation') or assessment.get('recommendation_en') or entry.get('answer')
            else:
                answer = localized_answer(question_key, entry.get('answer'), language)
            rows.append({'question': question, 'answer': answer})
        return rows

    sections = []
    for section_name, values in snapshot.items():
        if section_name == "assessments":
            if not isinstance(values, dict):
                continue
            for assessment_title, assessment_values in values.items():
                if not isinstance(assessment_values, dict):
                    continue
                rows = localized_rows(assessment_values, assessment_title)
                if rows:
                    sections.append({
                        "name": localized_assessment_titles.get(assessment_title, assessment_title.replace('_', ' ')),
                        "rows": rows,
                    })
            continue
        if not isinstance(values, dict):
            continue
        rows = localized_rows(values)
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
    referral_groups = {}
    for referral in referrals.order_by('screening_id', '-created', '-id'):
        referral_groups.setdefault(referral.screening_id, []).append(referral)

    screening_referrals = []
    for grouped_referrals in referral_groups.values():
        referral = grouped_referrals[0]
        selected = selected_assessments_for_record(referral.screening, ASSESSMENTS, language)
        if not selected:
            # Older or partially migrated records may not contain the selected
            # IDs on the screening itself. Use referral assessment IDs as a
            # safe fallback so the doctor still sees what was referred.
            referral_assessment_ids = {item.assessment_id for item in grouped_referrals}
            selected = [
                {**item, 'display_title': item.get(f'title_{language}') or item.get('title_en') or item['title']}
                for item in ASSESSMENTS
                if item.get('id') in referral_assessment_ids
            ]
        referral.display_assessments = [
            {
                'title': item.get('display_title') or item.get('title_en') or item.get('title', ''),
                'status': item.get('display_status') or item.get('status_en') or '',
            }
            for item in selected
        ]
        referral.display_assessment_title = f"{len(referral.display_assessments)} {labels['screening_areas']}"
        screening_referrals.append(referral)
    return render(request, 'doctor/dashboard.html', {
        'labels': labels, 'current_language': language, 'doctor': doctor,
        'referrals': screening_referrals, 'status_filter': status_filter,
        'counts': {
            'pending': doctor.referrals.filter(status=DoctorReferral.STATUS_PENDING).values('screening_id').distinct().count(),
            'reviewed': doctor.referrals.filter(status=DoctorReferral.STATUS_REVIEWED).values('screening_id').distinct().count(),
            'total': doctor.referrals.values('screening_id').distinct().count(),
        },
        'status_labels': dict(DoctorReferral.STATUS_CHOICES),
    })


@login_required
def recommendations(request, screening_id):
    language, labels = _labels(request)
    screening = get_object_or_404(MyModel, pk=screening_id, userid=request.user)
    selected = selected_assessments_for_record(screening, ASSESSMENTS, language)
    selected_referral = (
        screening.doctor_referrals.select_related('doctor')
        .filter(patient=request.user)
        .exclude(status=DoctorReferral.STATUS_CANCELLED)
        .first()
    )
    doctor_queryset = active_gp_doctors_for_screening(screening)
    search_query = request.GET.get('q', '').strip()[:120]
    if search_query:
        doctor_queryset = doctor_queryset.filter(
            Q(display_name__icontains=search_query)
            | Q(clinic_name__icontains=search_query)
            | Q(bio__icontains=search_query)
        )

    # Suggest the patient's most recently selected doctor, but only if that
    # doctor is still active and eligible for this screening's organization.
    eligible_doctor_ids = active_gp_doctors_for_screening(screening).values('pk')
    last_selected_doctor_id = (
        DoctorReferral.objects.filter(
            patient=request.user,
            doctor_id__in=eligible_doctor_ids,
        )
        .exclude(status=DoctorReferral.STATUS_CANCELLED)
        .order_by('-created', '-pk')
        .values_list('doctor_id', flat=True)
        .first()
    )
    if last_selected_doctor_id:
        doctor_queryset = doctor_queryset.order_by(
            Case(
                When(pk=last_selected_doctor_id, then=Value(0)),
                default=Value(1),
                output_field=IntegerField(),
            ),
            'display_name',
            'pk',
        )
    doctor_list = list(doctor_queryset)
    return render(request, 'doctor/recommendations.html', {
        'labels': labels, 'current_language': language, 'screening': screening,
        'selected_assessments': selected,
        'doctors': doctor_list,
        'selected_doctor': selected_referral.doctor if selected_referral else None,
        'search_query': search_query,
        'doctor_count': len(doctor_list),
        'recommended_doctor_id': last_selected_doctor_id,
        'referral_form': DoctorReferralForm(),
    })


def _create_screening_referrals(*, screening, patient, doctor, language):
    """Create one referral row for a complete screening report."""
    assessment_ids = sorted(screening_assessment_ids(screening))
    if not assessment_ids:
        return False
    result_by_id = {
        item['id']: item
        for item in selected_assessments_for_record(screening, ASSESSMENTS, language)
    }
    DoctorReferral.objects.filter(
        screening=screening,
        patient=patient,
    ).exclude(doctor=doctor).exclude(status=DoctorReferral.STATUS_CANCELLED).update(
        status=DoctorReferral.STATUS_CANCELLED,
    )
    referral = DoctorReferral.objects.filter(
        patient=patient,
        screening=screening,
        doctor=doctor,
    ).order_by('created', 'id').first()
    created = referral is None
    if created:
        primary_assessment_id = assessment_ids[0]
        referral = DoctorReferral.objects.create(
            patient=patient,
            screening=screening,
            doctor=doctor,
            assessment_id=primary_assessment_id,
            result_status=(result_by_id.get(primary_assessment_id) or {}).get('status_en', ''),
        )
    elif referral.status == DoctorReferral.STATUS_CANCELLED:
        referral.status = DoctorReferral.STATUS_PENDING
        referral.reviewed_at = None
        referral.result_status = (result_by_id.get(referral.assessment_id) or {}).get('status_en', '')
        referral.save(update_fields=('status', 'reviewed_at', 'result_status', 'updated'))
        created = True
    return created


@require_POST
@login_required
def create_screening_referral(request, screening_id, doctor_id):
    language, labels = _labels(request)
    screening = get_object_or_404(MyModel, pk=screening_id, userid=request.user)
    doctor = get_object_or_404(active_gp_doctors_for_screening(screening), pk=doctor_id)
    with transaction.atomic():
        created = _create_screening_referrals(
            screening=screening,
            patient=request.user,
            doctor=doctor,
            language=language,
        )
        if created:
            form = DoctorReferralForm(request.POST)
            if form.is_valid():
                message = form.cleaned_data.get('patient_message', '').strip()
                screening.doctor_referrals.filter(
                    patient=request.user,
                    doctor=doctor,
                ).update(patient_message=message)
            messages.success(request, labels['sent'])
        else:
            messages.info(request, labels['already_sent'])
    return redirect(localized_reverse('doctor:recommendations', language, kwargs={'screening_id': screening_id}))


@require_POST
@login_required
def create_referral(request, screening_id, doctor_id, assessment_id):
    # Backward-compatible endpoint: the referral is now for the whole screening.
    return create_screening_referral(request, screening_id, doctor_id)


@doctor_required
def referral_detail(request, referral_id):
    language, labels = _labels(request)
    referral = get_object_or_404(
        DoctorReferral.objects.select_related('patient', 'screening', 'doctor'),
        pk=referral_id, doctor=request.doctor_profile,
    )
    selected_assessments = selected_assessments_for_record(referral.screening, ASSESSMENTS, language)
    for assessment in selected_assessments:
        score_field = SCORE_FIELDS.get(assessment['title'])
        stored_score = getattr(referral.screening, score_field, None) if score_field else None
        assessment['has_score'] = stored_score is not None
        if assessment['has_score']:
            assessment['score'] = stored_score
    follow_up_plans = list(
        referral.screening.follow_up_plans.select_related('program').prefetch_related('reminders__step')
    )
    for plan in follow_up_plans:
        plan.display_title = plan.program.display_title(language)
        plan.display_description = plan.program.display_description(language)
    return render(request, 'doctor/referral_detail.html', {
        'labels': labels, 'current_language': language, 'referral': referral,
        'selected_assessments': selected_assessments,
        'comment_form': DoctorCommentForm(instance=referral),
        'status_choices': DoctorReferral.STATUS_CHOICES,
        'answer_sections': _screening_answer_sections(
            referral.screening, language, selected_assessments, labels,
        ),
        'follow_up_plans': follow_up_plans,
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
        referral.screening.doctor_referrals.filter(doctor=referral.doctor).exclude(
            pk=referral.pk,
        ).update(status=DoctorReferral.STATUS_REVIEWED, reviewed_at=referral.reviewed_at)
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
        referral.screening.doctor_referrals.filter(doctor=referral.doctor).exclude(
            pk=referral.pk,
        ).update(status=status, reviewed_at=referral.reviewed_at)
        messages.success(request, labels['status_updated'])
    return redirect(localized_reverse('doctor:referral_detail', language, kwargs={'referral_id': referral.pk}))
