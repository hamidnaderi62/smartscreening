from django.contrib import admin

from .models import DoctorProfile, DoctorReferral


@admin.register(DoctorProfile)
class DoctorProfileAdmin(admin.ModelAdmin):
    list_display = ('display_name', 'license_number', 'is_gp', 'is_verified', 'is_active', 'organization_summary')
    list_filter = ('is_gp', 'is_verified', 'is_active', 'organizations')
    search_fields = ('display_name', 'license_number', 'user__username', 'user__email')
    filter_horizontal = ('organizations',)
    list_select_related = ('user',)
    actions = ('verify_doctors', 'unverify_doctors', 'activate_doctors', 'deactivate_doctors')

    @admin.display(description='Organizations')
    def organization_summary(self, obj):
        organizations = list(obj.organizations.values_list('title', flat=True))
        return ', '.join(organizations) if organizations else 'All organizations'

    @admin.action(description='Verify selected doctors')
    def verify_doctors(self, request, queryset):
        queryset.update(is_verified=True)

    @admin.action(description='Unverify selected doctors')
    def unverify_doctors(self, request, queryset):
        queryset.update(is_verified=False)

    @admin.action(description='Activate selected doctors')
    def activate_doctors(self, request, queryset):
        queryset.update(is_active=True)

    @admin.action(description='Deactivate selected doctors')
    def deactivate_doctors(self, request, queryset):
        queryset.update(is_active=False)


@admin.register(DoctorReferral)
class DoctorReferralAdmin(admin.ModelAdmin):
    list_display = ('screening', 'doctor', 'patient', 'assessment_id', 'status', 'created', 'reviewed_at')
    list_filter = ('status', 'doctor')
    search_fields = ('screening__code', 'doctor__display_name', 'patient__username', 'patient__email')
    readonly_fields = ('patient', 'screening', 'doctor', 'assessment_id', 'result_status', 'created', 'updated')
    list_select_related = ('patient', 'screening', 'doctor')
