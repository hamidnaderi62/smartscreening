from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse
from django.db.models import Count
from django.db.models import Prefetch
from .models import Blog,Team
from django.core.paginator import Paginator
from django.http import HttpResponse,JsonResponse
from django.core import serializers
from my_model.assessment_catalog import ASSESSMENTS
from my_model.models import MyModel
from doctor.models import DoctorReferral
from my_model.services.localization import (
    language_for_request,
    localize_objects,
    localize_assessments,
    normalize_language,
)


HOME_LABELS = {
    'fa': {
        'title': 'غربالگری هوشمند سلامت | تصمیم‌های بهتر برای زندگی بهتر',
        'brand_mark': 'غربالگری هوشمند', 'scroll': 'برای کشف بیشتر حرکت کنید',
        'clarity': 'شفافیت', 'health_insight': 'بینش سلامت', 'process_eyebrow': 'شروعی ساده', 'cta_eyebrow': 'قدم بعدی سلامت شما',
        'eyebrow': 'مراقبت پیشگیرانه، با دیدی روشن‌تر',
        'hero_title': 'سلامت خود را با داده‌های قابل فهم دنبال کنید.',
        'hero_text': 'حوزه‌های متناسب با حساب خود را انتخاب کنید، به پرسش‌های سلامت پاسخ دهید و نتیجه و گزارش قابل‌فهمی برای گفت‌وگو با پزشک دریافت کنید.',
        'start': 'شروع غربالگری',
        'register': 'ثبت نام',
        'doctor_portal': 'ورود پزشکان',
        'learn': 'چطور کار می‌کند؟',
        'secure': 'حریم خصوصی شما در اولویت است',
        'secure_text': 'اطلاعات غربالگری شما فقط برای ارائه بینش شخصی و پیگیری بهتر استفاده می‌شود.',
        'feature_title': 'از پاسخ‌های شما تا یک مسیر روشن‌تر',
        'feature_text': 'غربالگری، ارزیابی اولیه عوامل خطر است؛ نه تشخیص پزشکی. اطلاعات روشن به شما و پزشکتان کمک می‌کند درباره قدم بعدی گفت‌وگو کنید.',
        'feature_1_title': 'ارزیابی متناسب با شما',
        'feature_1_text': 'حوزه‌های در دسترس بر اساس اطلاعات حساب شما نمایش داده می‌شوند. پاسخ‌ها برای برآورد عوامل خطر هر حوزه استفاده می‌شوند.',
        'feature_2_title': 'بررسی توسط پزشک عمومی',
        'feature_2_text': 'می‌توانید گزارش کامل یک غربالگری را برای پزشک عمومی فعال در سازمان خود بفرستید و نظر او را دریافت کنید.',
        'feature_3_title': 'گزارش و سابقه قابل پیگیری',
        'feature_3_text': 'گزارش PDF، نظر پزشک و غربالگری‌های قبلی را در حساب خود نگه دارید و تغییرات را در طول زمان مرور کنید.',
        'steps_title': 'مسیر غربالگری شما، از شروع تا پیگیری',
        'step_1': 'انتخاب کنید',
        'step_1_text': 'از میان ارزیابی‌های متناسب با حساب خود، حوزه‌های موردنظر را انتخاب کنید.',
        'step_2': 'پاسخ دهید',
        'step_2_text': 'اطلاعات پایه، سبک زندگی و سابقه مرتبط را وارد کنید تا نتیجه بر اساس پاسخ‌های شما محاسبه شود.',
        'step_3': 'آگاهانه پیگیری کنید',
        'step_3_text': 'نتیجه و PDF را مرور کنید؛ در صورت نیاز گزارش را برای پزشک بفرستید و برنامه پیگیری را دنبال کنید.',
        'cta_title': 'آگاهی امروز، آرامش فردا را می‌سازد.',
        'cta_text': 'با یک غربالگری ساده، قدم بعدی سلامت خود را روشن‌تر کنید.',
        'scope_title': 'چه حوزه‌هایی را می‌توانید بررسی کنید؟',
        'scope_text': 'ارزیابی‌های موجود می‌توانند شامل سرطان‌ها، سلامت قلب و عروق، دیابت، پوکی استخوان و سکته باشند. فهرست دقیق با توجه به سن و جنسیت حساب شما تغییر می‌کند.',
        'scope_cancer': 'ارزیابی خطر سرطان', 'scope_heart': 'قلب و عروق', 'scope_diabetes': 'دیابت و متابولیسم', 'scope_bone': 'سلامت استخوان',
        'safety_title': 'غربالگری، تشخیص پزشکی نیست',
        'safety_text': 'نتیجه برآوردی بر اساس پاسخ‌های شماست و بیماری را تأیید یا رد نمی‌کند. برای تفسیر نتیجه یا نگرانی درباره سلامتتان با پزشک مشورت کنید؛ در شرایط اورژانسی فوراً به مراکز درمانی مراجعه کنید.',
        'report_preview_title': 'گزارش غربالگری شما',
        'report_preview_text': 'نتیجه، پاسخ‌ها و مسیر بعدی در یک گزارش',
        'doctor_review_label': 'امکان بررسی توسط پزشک',
        'dashboard_eyebrow': 'فضای شخصی سلامت شما',
        'welcome': 'خوش آمدید، {name}',
        'dashboard_text': 'اینجا می‌توانید غربالگری جدید شروع کنید و مسیر نتایج خود را دنبال کنید.',
        'new_screening': 'غربالگری جدید',
        'my_screenings': 'غربالگری‌های من',
        'reports': 'گزارش‌ها',
        'organization_admin': 'داشبورد سازمان',
        'platform_admin': 'مرکز کنترل پلتفرم',
        'screening_count': 'تعداد غربالگری',
        'tracks_count': 'حوزه‌های بررسی‌شده',
        'last_activity': 'آخرین فعالیت',
        'not_started': 'هنوز شروع نشده',
        'latest_title': 'سه غربالگری اخیر شما',
        'screening_history': 'همه غربالگری‌ها',
        'view_all_screenings': 'مشاهده همه',
        'status_no_doctor': 'تکمیل‌شده؛ بدون ارجاع به پزشک',
        'status_waiting_doctor': 'در انتظار بررسی پزشک',
        'status_checked_doctor': 'بررسی‌شده توسط پزشک',
        'screening_history_title': 'همه غربالگری‌های قبلی',
        'screening_history_empty': 'هنوز غربالگری‌ای برای نمایش وجود ندارد.',
        'back_home': 'بازگشت به خانه', 'previous_page': 'صفحه قبل', 'next_page': 'صفحه بعد',
        'no_screenings': 'هنوز غربالگری ثبت نکرده‌اید.',
        'no_screenings_text': 'با پاسخ دادن به چند پرسش، اولین تصویر شخصی خود از عوامل خطر را بسازید.',
        'view_result': 'مشاهده نتیجه',
        'download_pdf': 'دریافت PDF',
        'assessment_count': 'حوزه بررسی',
        'health_tip': 'قدم پیشنهادی',
        'health_tip_text': 'غربالگری‌ها را در فواصل منظم تکرار کنید و نتیجه را با پزشک خود در میان بگذارید.',
        'continue': 'ادامه مسیر',
        'private_workspace': 'فضای خصوصی شما',
        'private_workspace_text': 'نتایج شما در حساب کاربری‌تان ذخیره می‌شود تا روند سلامت‌تان را بهتر ببینید.',
        'follow_up': 'برنامه پیگیری',
    },
    'en': {
        'title': 'Smart Screening | Make better health decisions',
        'brand_mark': 'SMART SCREENING', 'scroll': 'SCROLL TO EXPLORE',
        'clarity': 'clarity', 'health_insight': 'Health insight', 'process_eyebrow': 'A SIMPLE START', 'cta_eyebrow': 'YOUR NEXT HEALTH DECISION',
        'eyebrow': 'Prevention, with a clearer point of view',
        'hero_title': 'Understand your health before it becomes urgent.',
        'hero_text': 'Choose assessments available for your profile, answer health questions, and receive a clear result and report to discuss with your doctor.',
        'start': 'Start a screening',
        'register': 'Register',
        'doctor_portal': 'Doctor login',
        'learn': 'How it works',
        'secure': 'Your privacy comes first',
        'secure_text': 'Your screening information is used to provide personal insight and better follow-up.',
        'feature_title': 'From your answers to a clearer next step',
        'feature_text': 'Screening is an initial assessment of risk factors, not a medical diagnosis. Clear information can help you and your doctor discuss what to do next.',
        'feature_1_title': 'An assessment shaped around you',
        'feature_1_text': 'Available assessments depend on your profile. Your answers are used to estimate risk factors for each selected area.',
        'feature_2_title': 'Review by a general practitioner',
        'feature_2_text': 'You can send the complete screening report to an active GP in your organization and receive their written review.',
        'feature_3_title': 'Reports and history in one place',
        'feature_3_text': 'Keep your PDF reports, doctor notes, and previous screenings in your account to review changes over time.',
        'steps_title': 'Your screening, from start to follow-up',
        'step_1': 'Choose',
        'step_1_text': 'Choose from the assessments available for your account.',
        'step_2': 'Answer',
        'step_2_text': 'Provide basic information, lifestyle details, and relevant history so results reflect your answers.',
        'step_3': 'Follow up with confidence',
        'step_3_text': 'Review your result and PDF, share the report with a doctor if needed, and follow any follow-up plan.',
        'cta_title': 'Clarity today can create confidence tomorrow.',
        'cta_text': 'Take a simple screening and make your next health decision clearer.',
        'scope_title': 'What can you screen?',
        'scope_text': 'Available assessments may cover cancer risks, cardiovascular health, diabetes, osteoporosis, and stroke. The exact list depends on your account’s age and gender.',
        'scope_cancer': 'Cancer risk', 'scope_heart': 'Heart & vascular health', 'scope_diabetes': 'Diabetes & metabolism', 'scope_bone': 'Bone health',
        'safety_title': 'Screening is not a diagnosis',
        'safety_text': 'Results are estimates based on your answers; they cannot confirm or rule out disease. Discuss your results or health concerns with a doctor. For urgent symptoms, seek immediate medical care.',
        'report_preview_title': 'Your screening report',
        'report_preview_text': 'Results, answers, and next steps in one report',
        'doctor_review_label': 'Doctor review available',
        'dashboard_eyebrow': 'Your personal health workspace',
        'welcome': 'Welcome, {name}',
        'dashboard_text': 'Start a new screening or continue following your health results from one place.',
        'new_screening': 'New screening',
        'my_screenings': 'My screenings',
        'reports': 'Reports',
        'organization_admin': 'Organization dashboard',
        'platform_admin': 'Platform control center',
        'screening_count': 'Screenings completed',
        'tracks_count': 'Health areas explored',
        'last_activity': 'Last activity',
        'not_started': 'Not started yet',
        'latest_title': 'Your latest screenings',
        'screening_history': 'All screenings',
        'view_all_screenings': 'View all',
        'status_no_doctor': 'Completed · no doctor referral',
        'status_waiting_doctor': 'Waiting for doctor review',
        'status_checked_doctor': 'Reviewed by doctor',
        'screening_history_title': 'All previous screenings',
        'screening_history_empty': 'There are no screenings to show yet.',
        'back_home': 'Back to home', 'previous_page': 'Previous', 'next_page': 'Next',
        'no_screenings': 'You have not completed a screening yet.',
        'no_screenings_text': 'Answer a few questions to create your first personal view of important risk factors.',
        'view_result': 'View result',
        'download_pdf': 'Download PDF',
        'assessment_count': 'Health areas',
        'health_tip': 'Suggested next step',
        'health_tip_text': 'Repeat screenings at appropriate intervals and discuss the results with your doctor.',
        'continue': 'Continue your journey',
        'private_workspace': 'Your private workspace',
        'private_workspace_text': 'Your results stay in your account so you can understand your health journey over time.',
        'follow_up': 'Follow-up plan',
    },
    'ar': {
        'title': 'الفحص الذكي | قرارات صحية أفضل',
        'brand_mark': 'الفحص الذكي', 'scroll': 'مرر لاكتشاف المزيد',
        'clarity': 'وضوح', 'health_insight': 'رؤية صحية', 'process_eyebrow': 'بداية بسيطة', 'cta_eyebrow': 'خطوتك الصحية التالية',
        'eyebrow': 'الوقاية برؤية أوضح',
        'hero_title': 'افهم صحتك قبل أن تصبح الحالة طارئة.',
        'hero_text': 'اختر التقييمات المتاحة لملفك، وأجب عن أسئلة صحية، واحصل على نتيجة وتقرير واضحين لمناقشتهما مع طبيبك.',
        'start': 'ابدأ الفحص',
        'register': 'إنشاء حساب',
        'doctor_portal': 'دخول الطبيب',
        'learn': 'كيف يعمل؟',
        'secure': 'خصوصيتك أولاً',
        'secure_text': 'تُستخدم معلومات الفحص لتقديم رؤية شخصية ومتابعة أفضل.',
        'feature_title': 'من إجاباتك إلى خطوة أوضح',
        'feature_text': 'الفحص تقييم أولي لعوامل الخطر وليس تشخيصاً طبياً. تساعدك المعلومات الواضحة أنت وطبيبك على مناقشة الخطوة التالية.',
        'feature_1_title': 'تقييم يناسب ملفك',
        'feature_1_text': 'تعتمد الفحوصات المتاحة على بيانات ملفك. تُستخدم إجاباتك لتقدير عوامل الخطر في كل مجال تختاره.',
        'feature_2_title': 'مراجعة طبيب عام',
        'feature_2_text': 'يمكنك إرسال تقرير الفحص الكامل إلى طبيب عام نشط في مؤسستك والحصول على مراجعته المكتوبة.',
        'feature_3_title': 'تقارير وسجل في مكان واحد',
        'feature_3_text': 'احتفظ بتقارير PDF وملاحظات الطبيب والفحوصات السابقة في حسابك لمراجعة التغيّرات بمرور الوقت.',
        'steps_title': 'فحصك من البداية وحتى المتابعة',
        'step_1': 'اختر',
        'step_1_text': 'اختر من الفحوصات المتاحة في حسابك.',
        'step_2': 'أجب',
        'step_2_text': 'أدخل المعلومات الأساسية ونمط الحياة والتاريخ ذي الصلة ليعكس التقييم إجاباتك.',
        'step_3': 'تابع بثقة',
        'step_3_text': 'راجع النتيجة والتقرير، وأرسله للطبيب عند الحاجة، واتبع خطة المتابعة إن وُجدت.',
        'cta_title': 'وضوح اليوم يصنع ثقة الغد.',
        'cta_text': 'ابدأ فحصاً بسيطاً واجعل خطوتك الصحية التالية أوضح.',
        'scope_title': 'ما المجالات التي يمكنك فحصها؟',
        'scope_text': 'قد تشمل التقييمات مخاطر السرطان وصحة القلب والأوعية والسكري وهشاشة العظام والسكتة الدماغية. تختلف القائمة حسب العمر والجنس المسجلين في حسابك.',
        'scope_cancer': 'مخاطر السرطان', 'scope_heart': 'القلب والأوعية', 'scope_diabetes': 'السكري والتمثيل الغذائي', 'scope_bone': 'صحة العظام',
        'safety_title': 'الفحص ليس تشخيصاً',
        'safety_text': 'النتائج تقديرات مبنية على إجاباتك ولا تؤكد المرض أو تنفيه. ناقش النتائج أو مخاوفك الصحية مع الطبيب. اطلب الرعاية الطبية فوراً عند وجود أعراض طارئة.',
        'report_preview_title': 'تقرير الفحص الخاص بك',
        'report_preview_text': 'النتائج والإجابات والخطوة التالية في تقرير واحد',
        'doctor_review_label': 'إمكانية مراجعة الطبيب',
        'dashboard_eyebrow': 'مساحتك الصحية الشخصية',
        'welcome': 'مرحباً، {name}',
        'dashboard_text': 'ابدأ فحصاً جديداً أو تابع نتائجك الصحية من مكان واحد.',
        'new_screening': 'فحص جديد',
        'my_screenings': 'فحوصاتي',
        'reports': 'التقارير',
        'organization_admin': 'لوحة تحكم المؤسسة',
        'platform_admin': 'مركز التحكم بالمنصة',
        'screening_count': 'الفحوصات المكتملة',
        'tracks_count': 'مجالات الصحة المستكشفة',
        'last_activity': 'آخر نشاط',
        'not_started': 'لم يبدأ بعد',
        'latest_title': 'أحدث ثلاثة فحوصات لك',
        'screening_history': 'كل الفحوصات',
        'view_all_screenings': 'عرض الكل',
        'status_no_doctor': 'مكتمل · دون إحالة إلى طبيب',
        'status_waiting_doctor': 'بانتظار مراجعة الطبيب',
        'status_checked_doctor': 'تمت مراجعته من الطبيب',
        'screening_history_title': 'جميع الفحوصات السابقة',
        'screening_history_empty': 'لا توجد فحوصات لعرضها حتى الآن.',
        'back_home': 'العودة إلى الرئيسية', 'previous_page': 'السابق', 'next_page': 'التالي',
        'no_screenings': 'لم تكمل أي فحص بعد.',
        'no_screenings_text': 'أجب عن بعض الأسئلة لإنشاء أول صورة شخصية لعوامل الخطر المهمة.',
        'view_result': 'عرض النتيجة',
        'download_pdf': 'تنزيل PDF',
        'assessment_count': 'مجالات صحية',
        'health_tip': 'الخطوة المقترحة',
        'health_tip_text': 'كرر الفحوصات في الفترات المناسبة وناقش النتائج مع طبيبك.',
        'continue': 'تابع رحلتك',
        'private_workspace': 'مساحتك الخاصة',
        'private_workspace_text': 'تبقى نتائجك في حسابك لتتمكن من فهم رحلتك الصحية مع مرور الوقت.',
        'follow_up': 'خطة المتابعة',
    },
}

def home(request):
    if request.user.is_authenticated:
        doctor_profile = getattr(request.user, 'doctor_profile', None)
        if doctor_profile and doctor_profile.is_available:
            return redirect('doctor:dashboard')
    language = normalize_language(language_for_request(request))
    labels = HOME_LABELS[language]
    localized_assessments = localize_assessments(
        [assessment for assessment in ASSESSMENTS if assessment.get('active')],
        language,
    )
    context = {
        'home_labels': labels,
        'welcome_text': '',
        'home_language': language,
        'assessment_highlights': localized_assessments[:4],
        'screening_count': 0,
        'health_area_count': 0,
        'recent_screenings': [],
        'last_screening': None,
        'is_org_admin': False,
        'is_platform_admin': False,
        'organization': None,
    }

    if request.user.is_authenticated:
        profile = getattr(request.user, 'profile', None)
        display_name = request.user.first_name or request.user.username
        referral_queryset = DoctorReferral.objects.filter(
            patient=request.user,
        ).exclude(status=DoctorReferral.STATUS_CANCELLED).order_by('-created', '-pk')
        screenings = list(
            MyModel.objects.filter(userid=request.user)
            .prefetch_related(Prefetch('doctor_referrals', queryset=referral_queryset))
            .order_by('-created', '-pk')[:3]
        )
        for screening in screenings:
            screening.assessment_count = len([
                value for value in (screening.selected_assessments_id or '').split(',')
                if value.strip()
            ])
            _set_screening_review_status(screening, labels)
        total_screenings = MyModel.objects.filter(userid=request.user).count()
        all_screening_ids = set()
        for screening in MyModel.objects.filter(userid=request.user).only('selected_assessments_id'):
            all_screening_ids.update(
                value.strip()
                for value in (screening.selected_assessments_id or '').split(',')
                if value.strip()
            )
        organization = getattr(profile, 'organization', None)
        if organization:
            organization = localize_objects([organization], ('title',), language)[0]
        context.update({
            'welcome_text': labels['welcome'].format(name=display_name),
            'screening_count': total_screenings,
            'health_area_count': len(all_screening_ids),
            'recent_screenings': screenings,
            'last_screening': screenings[0] if screenings else None,
            'is_org_admin': bool(getattr(profile, 'is_org_admin', False)),
            'is_platform_admin': bool(request.user.is_staff),
            'organization': organization,
        })

    return render(request, 'home.html', context)


def _set_screening_review_status(screening, labels):
    referrals = list(screening.doctor_referrals.all())
    statuses = {referral.status for referral in referrals}
    if DoctorReferral.STATUS_PENDING in statuses:
        screening.review_status_key = 'waiting_doctor'
    elif statuses & {DoctorReferral.STATUS_REVIEWED, DoctorReferral.STATUS_CLOSED}:
        screening.review_status_key = 'checked_doctor'
    else:
        screening.review_status_key = 'no_doctor'
    screening.review_status_label = labels[f'status_{screening.review_status_key}']


def screening_history(request):
    if not request.user.is_authenticated:
        return redirect('account:login')
    language = normalize_language(language_for_request(request))
    labels = HOME_LABELS[language]
    referrals = DoctorReferral.objects.filter(
        patient=request.user,
    ).exclude(status=DoctorReferral.STATUS_CANCELLED).order_by('-created', '-pk')
    screenings = (
        MyModel.objects.filter(userid=request.user)
        .prefetch_related(Prefetch('doctor_referrals', queryset=referrals))
        .order_by('-created', '-pk')
    )
    page = Paginator(screenings, 12).get_page(request.GET.get('page'))
    for screening in page.object_list:
        screening.assessment_count = len([
            value for value in (screening.selected_assessments_id or '').split(',')
            if value.strip()
        ])
        _set_screening_review_status(screening, labels)
    return render(request, 'screening_history.html', {
        'home_labels': labels,
        'home_language': language,
        'screening_page': page,
    })


def blog_list(request):
    blogs = Paginator(
        localize_objects(
            Blog.objects.filter(is_active=True).order_by('-created'),
            ('title', 'desc'),
        ),
        4,
    ).get_page(request.GET.get('page'))
    return render(request, 'blog_list.html', {'blogs': blogs})


def blog_detail(request, pk=None):
    return render(request, 'blog_detail.html', {
        'blog': localize_objects(
            [get_object_or_404(Blog, id=pk)],
            ('title', 'desc'),
        )[0],
    })

def home_fa(request):
    all_blogs = Blog.objects.filter(is_active= True).all().order_by('-created')
    blogs = all_blogs[:4]

    main_teams = Team.objects.filter(is_active=True, team_type='Main').all()
    advisor_teams = Team.objects.filter(is_active=True, team_type='Advisor').all()

    return render(request, 'home_fa.html', context={'blogs':blogs, 'main_teams':main_teams, 'advisor_teams':advisor_teams})

def home_en(request):
    all_blogs = Blog.objects.filter(is_active= True).all().order_by('-created')
    blogs = all_blogs[:4]

    main_teams = Team.objects.filter(is_active=True, team_type='Main').all()
    advisor_teams = Team.objects.filter(is_active=True, team_type='Advisor').all()

    return render(request, 'home_en.html', context={'blogs':blogs, 'main_teams':main_teams, 'advisor_teams':advisor_teams})

def home_ar(request):
    all_blogs = Blog.objects.filter(is_active= True).all().order_by('-created')
    blogs = all_blogs[:4]

    main_teams = Team.objects.filter(is_active=True, team_type='Main').all()
    advisor_teams = Team.objects.filter(is_active=True, team_type='Advisor').all()

    return render(request, 'home_ar.html', context={'blogs':blogs, 'main_teams':main_teams, 'advisor_teams':advisor_teams})


def blog_list_fa(request):
    all_blogs = Blog.objects.filter(is_active=True).all()
    page_number = request.GET.get('page')
    paginator = Paginator(all_blogs, 4)
    blogs = paginator.get_page(page_number)

    return render(request, 'blog_list_fa.html', context={'blogs':blogs})

def blog_detail_fa(request, pk=None):
    blog = get_object_or_404(Blog, id=pk)
    return render(request, 'blog_detail_fa.html', context={'blog':blog})



def team_list(request):
    teams = Team.objects.filter(is_active=True).all()
    data = list(teams.values())
    return JsonResponse(data, safe=False)
