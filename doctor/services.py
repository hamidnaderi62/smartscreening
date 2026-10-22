from django.db.models import Count, Q

from my_model.assessment_catalog import get_assessment_or_404
from my_model.services.localization import localized_value, normalize_language

from .models import DoctorProfile


def screening_assessment_ids(screening):
    return {
        int(value.strip())
        for value in (screening.selected_assessments_id or '').split(',')
        if value.strip().isdigit()
    }

def suggest_doctors_for_assessment(assessment_id, limit=3):
    """Return verified doctors covering one assessment, ranked by workload."""
    get_assessment_or_404(assessment_id)
    doctors = DoctorProfile.objects.filter(
        is_active=True,
        is_verified=True,
        user__is_active=True,
    ).prefetch_related('specializations').annotate(
        open_referral_count=Count(
            'referrals',
            filter=Q(
                referrals__status__in=('pending', 'reviewed'),
            ),
        ),
    )
    matching = [
        doctor for doctor in doctors
        if assessment_id in doctor.covered_assessment_ids
    ]
    return sorted(matching, key=lambda doctor: (doctor.open_referral_count, doctor.display_name.lower(), doctor.pk))[:limit]


def localized_assessment(assessment_id, language):
    assessment = get_assessment_or_404(assessment_id)
    language = normalize_language(language)
    return {
        'id': assessment_id,
        'title': localized_value(assessment, 'title', language, assessment['title']),
    }
