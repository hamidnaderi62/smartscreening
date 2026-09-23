from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from my_model.services.localization import language_for_request, normalize_language

from .models import FollowUpPlan


FOLLOWUP_LABELS = {
    'fa': {
        'title': 'برنامه پیگیری سلامت',
        'intro': 'برنامه‌های پیگیری پیشنهادی بر اساس نتایج غربالگری شما.',
        'active': 'در حال پیگیری',
        'completed': 'تکمیل شده',
        'cancelled': 'لغو شده',
        'next_reminder': 'یادآوری بعدی',
        'no_reminder': 'یادآوری زمان‌بندی نشده',
        'screening': 'غربالگری',
        'result': 'نتیجه',
        'pdf': 'گزارش PDF',
        'pending': 'در انتظار ارسال',
        'sent': 'ارسال شده',
        'failed': 'ناموفق',
        'empty': 'هنوز برنامه پیگیری برای شما ایجاد نشده است.',
        'empty_text': 'پس از انجام غربالگری و فعال بودن برنامه مرتبط، مراحل پیگیری اینجا نمایش داده می‌شوند.',
    },
    'en': {
        'title': 'Your follow-up plan',
        'intro': 'Follow-up programs recommended from your screening results.',
        'active': 'Active',
        'completed': 'Completed',
        'cancelled': 'Cancelled',
        'next_reminder': 'Next reminder',
        'no_reminder': 'No reminder scheduled',
        'screening': 'Screening',
        'result': 'Result',
        'pdf': 'PDF report',
        'pending': 'Pending',
        'sent': 'Sent',
        'failed': 'Failed',
        'empty': 'No follow-up program has been created for you yet.',
        'empty_text': 'Your follow-up steps will appear here after a screening matches an active program.',
    },
    'ar': {
        'title': 'خطة المتابعة الخاصة بك',
        'intro': 'برامج المتابعة المقترحة بناءً على نتائج الفحص.',
        'active': 'نشطة',
        'completed': 'مكتملة',
        'cancelled': 'ملغاة',
        'next_reminder': 'التذكير التالي',
        'no_reminder': 'لا يوجد تذكير مجدول',
        'screening': 'الفحص',
        'result': 'النتيجة',
        'pdf': 'تقرير PDF',
        'pending': 'قيد الانتظار',
        'sent': 'تم الإرسال',
        'failed': 'فشل',
        'empty': 'لم يتم إنشاء برنامج متابعة لك بعد.',
        'empty_text': 'ستظهر خطوات المتابعة بعد أن تتطابق نتيجة الفحص مع برنامج نشط.',
    },
}


@login_required
def follow_up_list(request):
    language = normalize_language(language_for_request(request))
    plans = FollowUpPlan.objects.filter(
        user=request.user,
    ).select_related('program', 'screening').prefetch_related('reminders__step')
    for plan in plans:
        plan.display_title = plan.program.display_title(language)
        plan.display_description = plan.program.display_description(language)
        for reminder in plan.reminders.all():
            reminder.display_title = (
                reminder.step.display_title(language)
                if reminder.step else ''
            )
    return render(request, 'followup/list.html', {
        'base_template': 'base.html',
        'followup_language': language,
        'followup_labels': FOLLOWUP_LABELS[language],
        'follow_up_plans': plans,
    })
