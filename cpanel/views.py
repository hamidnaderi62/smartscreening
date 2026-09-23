from functools import wraps

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.db.models import Count, Exists, OuterRef
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.translation import gettext as _

from account.models import OrganizationMembership
from my_model.models import MyModel
from my_model.services.localization import (
    language_for_request,
    localize_objects,
    normalize_language,
)


CPANEL_LABELS = {
    'fa': {
        'dashboard': 'داشبورد', 'screening_reports': 'گزارش غربالگری‌ها',
        'workspace': 'فضای مدیریت سازمان', 'overview': 'نمای کلی سازمان',
        'active_members': 'اعضای فعال', 'total_members': 'کل اعضا',
        'today_screenings': 'غربالگری امروز', 'monthly_screenings': 'غربالگری این ماه',
        'quick_actions': 'دسترسی سریع', 'manage_members': 'مدیریت اعضا',
        'view_all_reports': 'مشاهده همه گزارش‌ها', 'latest_activity': 'آخرین فعالیت‌ها',
        'organization_status': 'وضعیت سازمان', 'no_activity': 'هنوز فعالیتی ثبت نشده است.',
        'active_members_ratio': 'نسبت اعضای فعال',
        'user_count': 'تعداد کاربران', 'screening_count': 'تعداد غربالگری‌ها',
        'organization_users': 'کاربران سازمان', 'view_all': 'مشاهده همه',
        'username': 'نام کاربری', 'user': 'کاربر', 'code': 'کد',
        'report': 'گزارش', 'no_users': 'هنوز کاربری ثبت نام نکرده است.',
        'recent_screenings': 'آخرین غربالگری‌ها', 'date': 'تاریخ',
        'view': 'مشاهده', 'no_reports': 'گزارشی وجود ندارد.',
        'report_code': 'کد گزارش', 'actions': 'عملیات', 'view_report': 'مشاهده گزارش',
        'user_list': 'لیست کاربران', 'active_users': 'کاربران فعال',
        'search': 'جستجو ...', 'registration_date': 'تاریخ ثبت نام',
        'user_code': 'کد کاربر', 'status': 'وضعیت',
        'view_screening': 'نمایش غربالگری', 'access': 'مدیریت دسترسی',
        'active': 'فعال', 'inactive': 'غیرفعال',
        'deactivate': 'غیرفعال کردن', 'activate': 'فعال کردن',
    },
    'en': {
        'dashboard': 'Dashboard', 'screening_reports': 'Screening reports',
        'workspace': 'Organization workspace', 'overview': 'Organization overview',
        'active_members': 'Active members', 'total_members': 'Total members',
        'today_screenings': "Today's screenings", 'monthly_screenings': 'This month',
        'quick_actions': 'Quick actions', 'manage_members': 'Manage members',
        'view_all_reports': 'View all reports', 'latest_activity': 'Latest activity',
        'organization_status': 'Organization status', 'no_activity': 'No activity recorded yet.',
        'active_members_ratio': 'Active member ratio',
        'user_count': 'Users', 'screening_count': 'Screenings',
        'organization_users': 'Organization users', 'view_all': 'View all',
        'username': 'Username', 'user': 'User', 'code': 'Code',
        'report': 'Report', 'no_users': 'No users have registered yet.',
        'recent_screenings': 'Recent screenings', 'date': 'Date',
        'view': 'View', 'no_reports': 'No reports are available.',
        'report_code': 'Report code', 'actions': 'Actions', 'view_report': 'View report',
        'user_list': 'User list', 'active_users': 'Active users',
        'search': 'Search ...', 'registration_date': 'Registration date',
        'user_code': 'User code', 'status': 'Status',
        'view_screening': 'View screening', 'access': 'Access management',
        'active': 'Active', 'inactive': 'Inactive',
        'deactivate': 'Deactivate', 'activate': 'Activate',
    },
    'ar': {
        'dashboard': 'لوحة التحكم', 'screening_reports': 'تقارير الفحص',
        'workspace': 'مساحة إدارة المؤسسة', 'overview': 'نظرة عامة على المؤسسة',
        'active_members': 'الأعضاء النشطون', 'total_members': 'إجمالي الأعضاء',
        'today_screenings': 'فحوصات اليوم', 'monthly_screenings': 'فحوصات هذا الشهر',
        'quick_actions': 'إجراءات سريعة', 'manage_members': 'إدارة الأعضاء',
        'view_all_reports': 'عرض جميع التقارير', 'latest_activity': 'آخر الأنشطة',
        'organization_status': 'حالة المؤسسة', 'no_activity': 'لم يتم تسجيل أي نشاط بعد.',
        'active_members_ratio': 'نسبة الأعضاء النشطين',
        'user_count': 'المستخدمون', 'screening_count': 'الفحوصات',
        'organization_users': 'مستخدمو المؤسسة', 'view_all': 'عرض الكل',
        'username': 'اسم المستخدم', 'user': 'المستخدم', 'code': 'الرمز',
        'report': 'التقرير', 'no_users': 'لم يسجل أي مستخدم بعد.',
        'recent_screenings': 'الفحوصات الأخيرة', 'date': 'التاريخ',
        'view': 'عرض', 'no_reports': 'لا توجد تقارير متاحة.',
        'report_code': 'رمز التقرير', 'actions': 'الإجراءات', 'view_report': 'عرض التقرير',
        'user_list': 'قائمة المستخدمين', 'active_users': 'المستخدمون النشطون',
        'search': 'بحث ...', 'registration_date': 'تاريخ التسجيل',
        'user_code': 'رمز المستخدم', 'status': 'الحالة',
        'view_screening': 'عرض الفحص', 'access': 'إدارة الوصول',
        'active': 'نشط', 'inactive': 'غير نشط',
        'deactivate': 'تعطيل', 'activate': 'تفعيل',
    },
}


def _cpanel_context(request, organization, language, **extra):
    language = normalize_language(language)
    context = {
        'organization': localize_objects([organization], ('title', 'sentence'), language)[0],
        # Use the current shared shell so organization pages receive the
        # branded header/footer and language-aware layout.
        'base_template': 'base_raw.html',
        'cpanel_language': language,
        'cpanel_labels': CPANEL_LABELS[language],
    }
    context.update(extra)
    return context


def organization_admin_required(view_func):
    @wraps(view_func)
    @login_required
    def wrapped(request, *args, **kwargs):
        memberships = OrganizationMembership.objects.filter(
            user=request.user,
            role='admin',
            is_active=True,
        ).select_related('organization')
        session_organization_id = request.session.get('organization_id')
        membership = memberships.filter(
            organization_id=session_organization_id,
        ).first() if session_organization_id else memberships.first()
        membership = membership or memberships.first()
        organization = membership.organization if membership else None
        is_admin = bool(membership)
        if not organization or not is_admin:
            raise PermissionDenied('Organization administrator access is required.')
        request.organization = organization
        return view_func(request, *args, **kwargs)

    return wrapped


def _organization_users(organization, query='', include_inactive=False):
    memberships = OrganizationMembership.objects.filter(
        organization=organization,
        role='member',
    )
    if not include_inactive:
        memberships = memberships.filter(is_active=True)
    organization_membership = OrganizationMembership.objects.filter(
        user_id=OuterRef('pk'),
        organization=organization,
        role='member',
        is_active=True,
    )
    users = User.objects.filter(
        organization_memberships__in=memberships,
    ).select_related('profile').annotate(
        organization_membership_active=Exists(organization_membership),
    ).distinct().order_by('-date_joined')
    if query:
        users = users.filter(username__icontains=query)
    return users


@organization_admin_required
def organization_dashboard_fa(request):
    return _organization_dashboard(request, 'fa')


@organization_admin_required
def organization_dashboard(request):
    return _organization_dashboard(request, language_for_request(request))


def _organization_dashboard(request, language):
    organization = request.organization
    users = _organization_users(organization).annotate(
        screening_count=Count('screenings', distinct=True),
    ).order_by('-screening_count', '-date_joined')

    memberships = OrganizationMembership.objects.filter(
        organization=organization,
        role='member',
    )
    active_user_count = memberships.filter(is_active=True).count()
    total_user_count = memberships.count()

    screenings = MyModel.objects.filter(
        userid__organization_memberships__organization=organization,
        userid__organization_memberships__is_active=True,
    ).select_related('userid')
    recent_screenings = screenings.order_by('-created')[:10]
    now = timezone.localtime(timezone.now())
    active_member_percent = round((active_user_count / total_user_count) * 100) if total_user_count else 0

    return render(request, 'organization_dashboard.html', _cpanel_context(request, organization, language, **{
        'org_users': users[:8],
        'user_count': active_user_count,
        'total_user_count': total_user_count,
        'screening_count': screenings.count(),
        'today_screening_count': screenings.filter(created__date=now.date()).count(),
        'monthly_screening_count': screenings.filter(
            created__year=now.year,
            created__month=now.month,
        ).count(),
        'active_member_percent': active_member_percent,
        'recent_screenings': recent_screenings,
    }))


@organization_admin_required
def admin_users_list_fa(request):
    return _admin_users_list(request, 'fa')


@organization_admin_required
def admin_users_list(request):
    return _admin_users_list(request, language_for_request(request))


def _admin_users_list(request, language):
    organization = request.organization
    users = _organization_users(
        organization,
        request.GET.get('q', '').strip(),
        include_inactive=True,
    )
    paginator = Paginator(users, 20)
    org_users = paginator.get_page(request.GET.get('page'))
    return render(request, 'admin_users_list.html', _cpanel_context(request, organization, language, **{
        'org_users': org_users,
    }))


@organization_admin_required
@require_POST
def toggle_user_status(request, user_id):
    return _toggle_user_status(request, user_id, 'cpanel:admin_users_list_fa')


@organization_admin_required
@require_POST
def toggle_user_status_i18n(request, user_id):
    return _toggle_user_status(request, user_id, 'cpanel:admin_users_list')


def _toggle_user_status(request, user_id, redirect_name):
    membership = get_object_or_404(
        OrganizationMembership,
        user_id=user_id,
        organization=request.organization,
        role='member',
    )
    membership.is_active = not membership.is_active
    membership.save(update_fields=('is_active',))
    messages.success(request, _('User status updated successfully.'))
    return redirect(redirect_name)


@organization_admin_required
def organization_reports_fa(request):
    return _organization_reports(request, 'fa')


@organization_admin_required
def organization_reports(request):
    return _organization_reports(request, language_for_request(request))


def _organization_reports(request, language):
    organization = request.organization
    user_id = request.GET.get('user_id')
    selected_user = None
    screenings = MyModel.objects.filter(
        userid__organization_memberships__organization=organization,
        userid__organization_memberships__is_active=True,
    ).select_related('userid').order_by('-created')

    if user_id:
        selected_user = get_object_or_404(
            User.objects.filter(
                organization_memberships__organization=organization,
                organization_memberships__is_active=True,
            ).distinct(),
            id=user_id,
        )
        screenings = screenings.filter(userid=selected_user)

    paginator = Paginator(screenings, 20)
    return render(request, 'organization_reports.html', _cpanel_context(request, organization, language, **{
        'selected_user': selected_user,
        'screenings': paginator.get_page(request.GET.get('page')),
    }))
