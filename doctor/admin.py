from django import forms
from django.contrib import admin

from my_model.assessment_catalog import ASSESSMENTS

from .models import DoctorProfile, DoctorReferral, DoctorSpecialization


class DoctorSpecializationAdminForm(forms.ModelForm):
    assessment_ids = forms.MultipleChoiceField(
        choices=[(item['id'], item['title_en']) for item in ASSESSMENTS],
        required=False,
        widget=forms.CheckboxSelectMultiple,
        label='Covered screening diseases',
    )

    class Meta:
        model = DoctorSpecialization
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.initial['assessment_ids'] = [str(value) for value in (self.instance.assessment_ids or [])]

    def clean_assessment_ids(self):
        return [int(value) for value in self.cleaned_data['assessment_ids']]


@admin.register(DoctorSpecialization)
class DoctorSpecializationAdmin(admin.ModelAdmin):
    form = DoctorSpecializationAdminForm
    list_display = ('title', 'code', 'is_active', 'assessment_summary')
    list_filter = ('is_active',)
    search_fields = ('title', 'title_fa', 'title_ar', 'code')

    @admin.display(description='Screening diseases')
    def assessment_summary(self, obj):
        names = {item['id']: item['title_en'] for item in ASSESSMENTS}
        return ', '.join(names.get(value, str(value)) for value in obj.assessment_id_set)


@admin.register(DoctorProfile)
class DoctorProfileAdmin(admin.ModelAdmin):
    list_display = ('display_name', 'license_number', 'is_verified', 'is_active', 'specialization_summary')
    list_filter = ('is_verified', 'is_active', 'specializations')
    search_fields = ('display_name', 'license_number', 'user__username', 'user__email')
    filter_horizontal = ('specializations',)
    list_select_related = ('user',)
    actions = ('verify_doctors', 'unverify_doctors', 'activate_doctors', 'deactivate_doctors')

    @admin.display(description='Specializations')
    def specialization_summary(self, obj):
        return ', '.join(obj.specializations.values_list('title', flat=True))

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
