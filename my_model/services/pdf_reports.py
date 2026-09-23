"""PDF report assembly services."""

from datetime import datetime

from .result_formatting import build_result_context
from .localization import language_for_request, localize_assessments, normalize_language


SCORE_FIELDS = {
    'Diabetes': 'idf_score',
    'Breast_Cancer': 'mymodel_gail_score',
    'Cardiovascular_Disease': 'ascvd_score',
    'Colorectal_Cancer': 'premm_score',
    'Cervical_Cancer': 'cervical_cancer_score',
    'Prostate_Cancer': 'pbcg_score_high_cancer',
    'Melanoma_Cancer': 'melanoma_cancer_score',
    'Osteoporosis': 'osteoporosis_score',
    'Ovarian_Cancer': 'ovarian_cancer_score',
    'Stomach_Cancer': 'stomach_cancer_score',
    'Stroke': 'stroke_score',
    'Pancreatic_Cancer': 'pancreatic_cancer_score',
}

STATUS_FIELDS = {
    'Diabetes': 'idf_status',
    'Cardiovascular_Disease': 'ascvd_status',
}


def selected_assessments_for_record(record, assessments, language=None):
    """Attach stored scores/statuses to catalog assessments for PDF output."""
    ids = {
        int(value.strip())
        for value in (record.selected_assessments_id or '').split(',')
        if value.strip()
    }
    selected = []
    for assessment in assessments:
        if assessment['id'] not in ids:
            continue

        item = assessment.copy()
        score_field = SCORE_FIELDS.get(assessment['title'])
        if score_field:
            item['score'] = getattr(record, score_field, 0) or 0
        status_field = STATUS_FIELDS.get(assessment['title'])
        if status_field:
            status = getattr(record, status_field, '')
            if status:
                item['status_en'] = status
        selected.append(item)

    # Rebuild the presentation metadata from the persisted answers. The
    # catalog is intentionally static, while status/recommendation values are
    # calculated per screening and are not stored in the catalog itself.
    record_data = {
        field.name: getattr(record, field.name)
        for field in record._meta.concrete_fields
    }
    for field_name in SCORE_FIELDS.values():
        if record_data.get(field_name) is None:
            record_data[field_name] = 0
    build_result_context(selected, record_data)
    return localize_assessments(selected, normalize_language(language))


def generate_screening_pdf(record, assessments, request):
    """Generate a PDF buffer and stable filename for one screening record."""
    from .report_pdf import generate_pdf_report

    language = language_for_request(request) if request else None
    selected = selected_assessments_for_record(record, assessments, language)
    pdf_buffer = generate_pdf_report(record, selected, request)
    filename = (
        f'screening_report_{record.code or "patient"}_'
        f'{datetime.now().strftime("%Y%m%d_%H%M")}.pdf'
    )
    return pdf_buffer, filename
