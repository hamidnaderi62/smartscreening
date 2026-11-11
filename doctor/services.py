from django.db.models import Q

from my_model.assessment_catalog import get_assessment_or_404
from my_model.services.localization import localized_value, normalize_language

from .models import DoctorProfile


def screening_assessment_ids(screening):
    return {
        int(value.strip())
        for value in (screening.selected_assessments_id or '').split(',')
        if value.strip().isdigit()
    }


def screening_organization(screening):
    """Return the organization selected for the screening patient's account."""
    try:
        return screening.userid.profile.organization
    except (AttributeError, ValueError):
        return None


def active_gp_doctors_for_organization(organization=None):
    """Return verified GPs available to one organization.

    A doctor with no explicit organization rows is intentionally treated as a
    global doctor, preserving the default-all-organizations behavior.
    """
    queryset = DoctorProfile.objects.filter(
        is_active=True,
        is_verified=True,
        is_gp=True,
        user__is_active=True,
    ).select_related('user').prefetch_related('organizations')
    if organization is None:
        return queryset.filter(organizations__isnull=True).distinct()
    return queryset.filter(Q(organizations__isnull=True) | Q(organizations=organization)).distinct()


def active_gp_doctors_for_screening(screening):
    return active_gp_doctors_for_organization(screening_organization(screening))

def localized_assessment(assessment_id, language):
    assessment = get_assessment_or_404(assessment_id)
    language = normalize_language(language)
    return {
        'id': assessment_id,
        'title': localized_value(assessment, 'title', language, assessment['title']),
    }
