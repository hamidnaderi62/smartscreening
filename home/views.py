from django.shortcuts import render,get_object_or_404
from django.urls import reverse
from django.db.models import Count
from .models import Blog,Team
from django.core.paginator import Paginator
from django.http import HttpResponse,JsonResponse
from django.core import serializers
from my_model.assessment_catalog import ASSESSMENTS
from my_model.models import MyModel
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
        'hero_text': 'غربالگری هوشمند به شما کمک می‌کند عوامل خطر مهم را زودتر ببینید، مسیر بعدی را بهتر بشناسید و گفت‌وگوی آگاهانه‌تری با پزشک داشته باشید.',
        'start': 'شروع غربالگری',
        'learn': 'چطور کار می‌کند؟',
        'secure': 'حریم خصوصی شما در اولویت است',
        'secure_text': 'اطلاعات غربالگری شما فقط برای ارائه بینش شخصی و پیگیری بهتر استفاده می‌شود.',
        'feature_title': 'یک تصویر روشن از سلامت شما',
        'feature_text': 'ابزارهای ما نتیجه را به زبان ساده و قابل پیگیری تبدیل می‌کنند.',
        'feature_1_title': 'بینش شخصی',
        'feature_1_text': 'نتایج بر اساس اطلاعات و سابقه‌ای که وارد می‌کنید تنظیم می‌شوند.',
        'feature_2_title': 'پیگیری در طول زمان',
        'feature_2_text': 'تغییرات غربالگری‌های قبلی را کنار هم ببینید.',
        'feature_3_title': 'گفت‌وگوی بهتر با پزشک',
        'feature_3_text': 'گزارش خوانا و جامع خود را برای بررسی بعدی همراه داشته باشید.',
        'steps_title': 'از پرسش تا اقدام، در سه گام',
        'step_1': 'انتخاب کنید',
        'step_1_text': 'حوزه‌های سلامت موردنظر خود را انتخاب کنید.',
        'step_2': 'پاسخ دهید',
        'step_2_text': 'به چند پرسش ساده درباره سبک زندگی و سابقه پزشکی پاسخ دهید.',
        'step_3': 'آگاهانه پیگیری کنید',
        'step_3_text': 'نتیجه، روند تغییرات و توصیه‌های پیگیری را ببینید.',
        'cta_title': 'آگاهی امروز، آرامش فردا را می‌سازد.',
        'cta_text': 'با یک غربالگری ساده، قدم بعدی سلامت خود را روشن‌تر کنید.',
        'dashboard_eyebrow': 'فضای شخصی سلامت شما',
        'welcome': 'خوش آمدید، {name}',
        'dashboard_text': 'اینجا می‌توانید غربالگری جدید شروع کنید و مسیر نتایج خود را دنبال کنید.',
        'new_screening': 'غربالگری جدید',
        'my_screenings': 'غربالگری‌های من',
        'reports': 'گزارش‌ها',
        'organization_admin': 'داشبورد سازمان',
        'screening_count': 'تعداد غربالگری',
        'tracks_count': 'حوزه‌های بررسی‌شده',
        'last_activity': 'آخرین فعالیت',
        'not_started': 'هنوز شروع نشده',
        'latest_title': 'آخرین غربالگری شما',
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
        'hero_text': 'Smart Screening helps you spot important risk factors earlier, understand what to do next, and have more informed conversations with your doctor.',
        'start': 'Start a screening',
        'learn': 'How it works',
        'secure': 'Your privacy comes first',
        'secure_text': 'Your screening information is used to provide personal insight and better follow-up.',
        'feature_title': 'A clearer picture of your health',
        'feature_text': 'Turn personal health information into simple, useful next steps.',
        'feature_1_title': 'Personal insight',
        'feature_1_text': 'Results are tailored to the information and history you provide.',
        'feature_2_title': 'Track change over time',
        'feature_2_text': 'See how your previous screening results move together.',
        'feature_3_title': 'Better doctor conversations',
        'feature_3_text': 'Bring a clear, comprehensive report to your next appointment.',
        'steps_title': 'From questions to action, in three steps',
        'step_1': 'Choose',
        'step_1_text': 'Select the health areas you want to explore.',
        'step_2': 'Answer',
        'step_2_text': 'Complete a few simple questions about lifestyle and medical history.',
        'step_3': 'Follow up with confidence',
        'step_3_text': 'Review your result, trends, and recommended next steps.',
        'cta_title': 'Clarity today can create confidence tomorrow.',
        'cta_text': 'Take a simple screening and make your next health decision clearer.',
        'dashboard_eyebrow': 'Your personal health workspace',
        'welcome': 'Welcome, {name}',
        'dashboard_text': 'Start a new screening or continue following your health results from one place.',
        'new_screening': 'New screening',
        'my_screenings': 'My screenings',
        'reports': 'Reports',
        'organization_admin': 'Organization dashboard',
        'screening_count': 'Screenings completed',
        'tracks_count': 'Health areas explored',
        'last_activity': 'Last activity',
        'not_started': 'Not started yet',
        'latest_title': 'Your latest screening',
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
        'hero_text': 'يساعدك الفحص الذكي على اكتشاف عوامل الخطر مبكراً، وفهم الخطوة التالية، وإجراء محادثة أكثر وعياً مع طبيبك.',
        'start': 'ابدأ الفحص',
        'learn': 'كيف يعمل؟',
        'secure': 'خصوصيتك أولاً',
        'secure_text': 'تُستخدم معلومات الفحص لتقديم رؤية شخصية ومتابعة أفضل.',
        'feature_title': 'صورة أوضح لصحتك',
        'feature_text': 'حوّل معلوماتك الصحية إلى خطوات بسيطة ومفيدة.',
        'feature_1_title': 'رؤية شخصية',
        'feature_1_text': 'تُصمّم النتائج وفق المعلومات والتاريخ الذي تقدمه.',
        'feature_2_title': 'تتبّع التغيّر',
        'feature_2_text': 'شاهد نتائج الفحوصات السابقة وتغيّرها مع الوقت.',
        'feature_3_title': 'حوار أفضل مع الطبيب',
        'feature_3_text': 'اصطحب تقريراً واضحاً وشاملاً إلى موعدك التالي.',
        'steps_title': 'من الأسئلة إلى الإجراء في ثلاث خطوات',
        'step_1': 'اختر',
        'step_1_text': 'حدد مجالات الصحة التي تريد استكشافها.',
        'step_2': 'أجب',
        'step_2_text': 'أجب عن أسئلة بسيطة حول نمط الحياة والتاريخ الطبي.',
        'step_3': 'تابع بثقة',
        'step_3_text': 'راجع النتيجة والاتجاهات والخطوات المقترحة.',
        'cta_title': 'وضوح اليوم يصنع ثقة الغد.',
        'cta_text': 'ابدأ فحصاً بسيطاً واجعل خطوتك الصحية التالية أوضح.',
        'dashboard_eyebrow': 'مساحتك الصحية الشخصية',
        'welcome': 'مرحباً، {name}',
        'dashboard_text': 'ابدأ فحصاً جديداً أو تابع نتائجك الصحية من مكان واحد.',
        'new_screening': 'فحص جديد',
        'my_screenings': 'فحوصاتي',
        'reports': 'التقارير',
        'organization_admin': 'لوحة تحكم المؤسسة',
        'screening_count': 'الفحوصات المكتملة',
        'tracks_count': 'مجالات الصحة المستكشفة',
        'last_activity': 'آخر نشاط',
        'not_started': 'لم يبدأ بعد',
        'latest_title': 'أحدث فحص لك',
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
        'organization': None,
    }

    if request.user.is_authenticated:
        profile = getattr(request.user, 'profile', None)
        display_name = request.user.first_name or request.user.username
        screenings = list(
            MyModel.objects.filter(userid=request.user).order_by('-created')[:6]
        )
        for screening in screenings:
            screening.assessment_count = len([
                value for value in (screening.selected_assessments_id or '').split(',')
                if value.strip()
            ])
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
            'organization': organization,
        })

    return render(request, 'home.html', context)


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
