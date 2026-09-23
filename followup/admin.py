from django.contrib import admin, messages

from .models import FollowUpPlan, FollowUpProgram, FollowUpReminder, FollowUpStep
from .services import queue_manual_pdf_sms, send_follow_up_reminder


class FollowUpStepInline(admin.TabularInline):
    model = FollowUpStep
    extra = 1
    ordering = ('order',)
    fields = (
        'order', 'delay_days', 'title', 'title_en', 'title_ar',
        'message', 'message_en', 'message_ar', 'send_sms', 'is_active',
    )


@admin.register(FollowUpProgram)
class FollowUpProgramAdmin(admin.ModelAdmin):
    list_display = (
        'assessment_id', 'title_en', 'trigger_statuses',
        'send_pdf_sms', 'pdf_sms_delay_days', 'is_active',
    )
    list_filter = ('is_active', 'send_pdf_sms')
    search_fields = ('title', 'title_en', 'title_ar', 'trigger_statuses')
    inlines = (FollowUpStepInline,)


@admin.action(description='Send PDF report SMS now')
def send_pdf_sms_action(modeladmin, request, queryset):
    sent = failed = 0
    for plan in queryset:
        reminder = queue_manual_pdf_sms(plan)
        if reminder.status == 'sent':
            sent += 1
        else:
            failed += 1
    modeladmin.message_user(
        request,
        f'PDF SMS sent: {sent}; failed: {failed}.',
        messages.SUCCESS if not failed else messages.WARNING,
    )


@admin.action(description='Mark selected follow-up plans completed')
def complete_plans(modeladmin, request, queryset):
    from django.utils import timezone

    updated = queryset.filter(status='active').update(
        status='completed',
        completed_at=timezone.now(),
    )
    FollowUpReminder.objects.filter(
        plan__in=queryset,
        status='pending',
    ).update(status='cancelled')
    queryset.update(next_reminder_at=None)
    modeladmin.message_user(request, f'{updated} follow-up plan(s) completed.')


@admin.register(FollowUpPlan)
class FollowUpPlanAdmin(admin.ModelAdmin):
    list_display = (
        'user', 'program', 'screening', 'result_status', 'status',
        'language', 'next_reminder_at',
    )
    list_filter = ('status', 'language', 'program')
    search_fields = ('user__username', 'user__email', 'screening__code', 'result_status')
    readonly_fields = ('started_at', 'completed_at', 'next_reminder_at')
    actions = (send_pdf_sms_action, complete_plans)


@admin.action(description='Send selected pending/failed SMS now')
def send_reminders_now(modeladmin, request, queryset):
    sent = failed = 0
    for reminder in queryset.filter(status__in=('pending', 'failed')):
        send_follow_up_reminder(reminder)
        if reminder.status == 'sent':
            sent += 1
        else:
            failed += 1
    modeladmin.message_user(
        request,
        f'SMS sent: {sent}; failed: {failed}.',
        messages.SUCCESS if not failed else messages.WARNING,
    )


@admin.register(FollowUpReminder)
class FollowUpReminderAdmin(admin.ModelAdmin):
    list_display = (
        'plan', 'kind', 'scheduled_for', 'status', 'attempts',
        'sent_at', 'provider_message_id',
    )
    list_filter = ('kind', 'status', 'scheduled_for')
    search_fields = ('plan__user__username', 'plan__screening__code', 'provider_message_id')
    readonly_fields = (
        'attempts', 'sent_at', 'provider_message_id', 'provider_status',
        'last_error', 'message', 'created', 'updated',
    )
    actions = (send_reminders_now,)
