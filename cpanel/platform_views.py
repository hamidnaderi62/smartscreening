from django.contrib.auth.models import User
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from django.utils import timezone

from account.models import Organization, Profile
from followup.models import FollowUpPlan, FollowUpProgram, FollowUpReminder
from my_model.models import MyModel
from my_model.services.localization import language_for_request, localize_objects, normalize_language


PLATFORM_LABELS = {
    'fa': {
        'title': 'مرکز کنترل پلتفرم',
        'eyebrow': 'مدیریت کل پلتفرم',
        'subtitle': 'نمایی یکپارچه از سازمان‌ها، کاربران، غربالگری‌ها و برنامه‌های پیگیری.',
        'organizations': 'سازمان‌ها', 'active_organizations': 'سازمان‌های فعال',
        'users': 'کاربران', 'active_users': 'کاربران فعال',
        'screenings': 'غربالگری‌ها', 'today_screenings': 'غربالگری امروز',
        'monthly_screenings': 'غربالگری این ماه',
        'followup_programs': 'برنامه‌های پیگیری', 'active_programs': 'برنامه‌های فعال',
        'active_plans': 'برنامه‌های فعال پیگیری', 'pending_reminders': 'یادآوری‌های در انتظار',
        'failed_reminders': 'یادآوری‌های ناموفق', 'sent_reminders': 'پیام‌های ارسال‌شده',
        'quick_actions': 'مدیریت سریع', 'manage_organizations': 'مدیریت سازمان‌ها',
        'manage_users': 'مدیریت کاربران', 'manage_memberships': 'عضویت‌های سازمانی',
        'manage_screenings': 'مشاهده غربالگری‌ها', 'manage_followup': 'مدیریت پیگیری',
        'manage_programs': 'برنامه‌ها', 'manage_plans': 'طرح‌های کاربران',
        'manage_reminders': 'یادآوری‌ها', 'recent_organizations': 'آخرین سازمان‌ها',
        'recent_users': 'آخرین کاربران', 'recent_screenings': 'آخرین غربالگری‌ها',
        'view_all': 'مشاهده همه', 'active': 'فعال', 'inactive': 'غیرفعال',
        'no_data': 'داده‌ای وجود ندارد.', 'open_admin': 'ورود به مدیریت اصلی',
        'organization_admin': 'داشبورد سازمان', 'organization_admins': 'مدیران سازمان', 'sms_settings': 'تنظیمات پیامک',
        'followup_sms': 'پیگیری', 'pdf_sms': 'گزارش PDF', 'enabled': 'فعال', 'disabled': 'غیرفعال',
        'platform_status': 'وضعیت پلتفرم',
        'health_areas': 'حوزه‌های سلامت', 'created': 'ایجاد شده',
        'screening_code': 'کد غربالگری', 'user': 'کاربر',
    },
    'en': {
        'title': 'Platform control center',
        'eyebrow': 'PLATFORM ADMINISTRATION',
        'subtitle': 'A unified view of organizations, users, screenings, and follow-up operations.',
        'organizations': 'Organizations', 'active_organizations': 'Active organizations',
        'users': 'Users', 'active_users': 'Active users',
        'screenings': 'Screenings', 'today_screenings': "Today's screenings",
        'monthly_screenings': 'This month', 'followup_programs': 'Follow-up programs',
        'active_programs': 'Active programs', 'active_plans': 'Active follow-up plans',
        'pending_reminders': 'Pending reminders', 'failed_reminders': 'Failed reminders',
        'sent_reminders': 'Sent messages', 'quick_actions': 'Quick management',
        'manage_organizations': 'Manage organizations', 'manage_users': 'Manage users',
        'manage_memberships': 'Organization memberships', 'manage_screenings': 'View screenings',
        'manage_followup': 'Follow-up management', 'manage_programs': 'Programs',
        'manage_plans': 'User plans', 'manage_reminders': 'Reminders',
        'recent_organizations': 'Recent organizations', 'recent_users': 'Recent users',
        'recent_screenings': 'Recent screenings', 'view_all': 'View all',
        'active': 'Active', 'inactive': 'Inactive', 'no_data': 'No data available.',
        'open_admin': 'Open main admin', 'organization_admin': 'Organization dashboard',
        'organization_admins': 'Organization admins', 'sms_settings': 'SMS settings',
        'followup_sms': 'Follow-up', 'pdf_sms': 'PDF report', 'enabled': 'Enabled', 'disabled': 'Disabled',
        'platform_status': 'Platform status', 'health_areas': 'Health areas',
        'created': 'Created', 'screening_code': 'Screening code', 'user': 'User',
    },
    'ar': {
        'title': 'مركز التحكم بالمنصة',
        'eyebrow': 'إدارة المنصة',
        'subtitle': 'نظرة موحدة على المؤسسات والمستخدمين والفحوصات وعمليات المتابعة.',
        'organizations': 'المؤسسات', 'active_organizations': 'المؤسسات النشطة',
        'users': 'المستخدمون', 'active_users': 'المستخدمون النشطون',
        'screenings': 'الفحوصات', 'today_screenings': 'فحوصات اليوم',
        'monthly_screenings': 'فحوصات هذا الشهر', 'followup_programs': 'برامج المتابعة',
        'active_programs': 'البرامج النشطة', 'active_plans': 'خطط المتابعة النشطة',
        'pending_reminders': 'التذكيرات المعلقة', 'failed_reminders': 'التذكيرات الفاشلة',
        'sent_reminders': 'الرسائل المرسلة', 'quick_actions': 'إدارة سريعة',
        'manage_organizations': 'إدارة المؤسسات', 'manage_users': 'إدارة المستخدمين',
        'manage_memberships': 'عضويات المؤسسات', 'manage_screenings': 'عرض الفحوصات',
        'manage_followup': 'إدارة المتابعة', 'manage_programs': 'البرامج',
        'manage_plans': 'خطط المستخدمين', 'manage_reminders': 'التذكيرات',
        'recent_organizations': 'أحدث المؤسسات', 'recent_users': 'أحدث المستخدمين',
        'recent_screenings': 'أحدث الفحوصات', 'view_all': 'عرض الكل',
        'active': 'نشط', 'inactive': 'غير نشط', 'no_data': 'لا توجد بيانات.',
        'open_admin': 'فتح الإدارة الرئيسية', 'organization_admin': 'لوحة تحكم المؤسسة',
        'organization_admins': 'مديرو المؤسسات', 'sms_settings': 'إعدادات الرسائل',
        'followup_sms': 'المتابعة', 'pdf_sms': 'تقرير PDF', 'enabled': 'نشط', 'disabled': 'معطل',
        'platform_status': 'حالة المنصة', 'health_areas': 'المجالات الصحية',
        'created': 'تاريخ الإنشاء', 'screening_code': 'رمز الفحص', 'user': 'المستخدم',
    },
}


@staff_member_required(login_url='/admin/login/')
def platform_dashboard(request):
    language = normalize_language(language_for_request(request))
    labels = PLATFORM_LABELS[language]
    now = timezone.localtime(timezone.now())

    organizations = Organization.objects.all()
    screenings = MyModel.objects.select_related('userid').order_by('-created')
    recent_organizations = localize_objects(
        organizations.order_by('-id')[:6],
        ('title', 'sentence'),
        language,
    )

    context = {
        'base_template': 'base_raw.html',
        'platform_language': language,
        'platform_labels': labels,
        'organization_count': organizations.count(),
        'active_organization_count': organizations.filter(is_active=True).count(),
        'user_count': User.objects.count(),
        'active_user_count': User.objects.filter(is_active=True).count(),
        'organization_admin_count': Profile.objects.filter(is_org_admin=True).count(),
        'screening_count': screenings.count(),
        'today_screening_count': screenings.filter(created__date=now.date()).count(),
        'monthly_screening_count': screenings.filter(
            created__year=now.year,
            created__month=now.month,
        ).count(),
        'followup_program_count': FollowUpProgram.objects.count(),
        'active_followup_program_count': FollowUpProgram.objects.filter(is_active=True).count(),
        'active_plan_count': FollowUpPlan.objects.filter(status='active').count(),
        'pending_reminder_count': FollowUpReminder.objects.filter(status='pending').count(),
        'failed_reminder_count': FollowUpReminder.objects.filter(status='failed').count(),
        'sent_reminder_count': FollowUpReminder.objects.filter(status='sent').count(),
        'recent_organizations': recent_organizations,
        'recent_users': User.objects.select_related('profile').order_by('-date_joined')[:7],
        'recent_screenings': screenings[:8],
    }
    return render(request, 'platform_dashboard.html', context)
