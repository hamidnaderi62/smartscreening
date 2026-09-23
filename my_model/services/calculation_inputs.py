"""Validation for the shared screening calculation form."""


class InvalidCalculationInput(ValueError):
    """Raised when a required screening answer is missing or malformed."""


COMMON_FIELDS = {
    'age', 'weight', 'height', 'waist_size', 'ethnicity', 'born_place',
    'education', 'blood_group', 'activity', 'smoking', 'alcohol', 'meat',
    'cereal', 'vegetables', 'dairy', 'multivitamin', 'blood_pressure',
    'blood_glucose', 'totchol', 'previous_cancer',
}

ASSESSMENT_FIELDS = {
    'Diabetes': {'relatives_diabetes'},
    'Cardiovascular_Disease': {'sbp', 'hdl'},
    'Breast_Cancer': {
        'biopsy', 'biopsy_num', 'hyperplasia_biopsy', 'menstruation_age',
        'child_age', 'fdr_cancer', 'breastfeeding', 'cbe', 'bse',
        'mammograms', 'syndrome', 'gene_mutation',
    },
    'Colorectal_Cancer': {
        'family_crc', 'diabetes', 'aspirin', 'estrogen', 'painmed',
        'v1_v2', 'v3', 'v4', 'v5_AB', 'v5_CD', 'v6_AB', 'v6_CD',
        'v7_E', 'v7_F', 'v8_MinAge_CRC', 'v8_MinAge_CRC_FDR',
        'v8_MinAge_CRC_SDR', 'v9_MinAge_EC', 'v9_MinAge_EC_FDR',
        'v9_MinAge_EC_SDR',
    },
    'Cervical_Cancer': {
        'num_sexual_partners', 'first_sexual_intercourse', 'num_pregnancies',
        'hormonal_contraceptives_years', 'iud', 'std', 'cervical_cancer',
        'cytology', 'cin', 'hpv',
    },
    'Prostate_Cancer': {'psa', 'famhistory', 'dre', 'priorbiopsy'},
    'Melanoma_Cancer': {
        'family_melanoma_cancer', 'colored_hair', 'colored_eyes', 'fair_skin',
        'moles_count', 'sunburns', 'sunlamp', 'immunosuppressive_drugs',
    },
    'Osteoporosis': {
        'rheumatoid_arthritis', 'have_bmd_test', 'result_bmd_test',
        'chemotherapy', 'steroid', 'anticonvulsants', 'calcium_supplements',
        'vitamin_d', 'family_break_bone',
    },
    'Ovarian_Cancer': {
        'family_breast_ovarian_prostate', 'family_ovarian_cancer',
        'gene_mutation', 'talcum_powder', 'hormonal_contraceptives_years',
        'num_pregnancies', 'breastfeeding', 'menopause', 'menopause_hormone',
        'hysterectomy', 'endometriosis', 'salpingectomy',
    },
    'Pancreatic_Cancer': {'family_pancreatic_cancer', 'chronic_pancreatitis'},
    'Stomach_Cancer': {'family_stomach_cancer', 'fastfood', 'cannedfood', 'h_pylori'},
    'Stroke': {'previous_stroke', 'history_totchol', 'family_history_stroke'},
}

NUMERIC_FIELDS = {
    'age', 'weight', 'height', 'waist_size', 'ethnicity', 'education',
    'activity', 'smoking', 'alcohol', 'meat', 'dairy', 'totchol', 'sbp',
    'hdl', 'biopsy', 'biopsy_num', 'hyperplasia_biopsy', 'menstruation_age',
    'child_age', 'fdr_cancer', 'v1_v2', 'v3', 'v4', 'v5_AB', 'v5_CD',
    'v6_AB', 'v6_CD', 'v7_E', 'v7_F', 'v8_MinAge_CRC', 'v8_MinAge_CRC_FDR',
    'v8_MinAge_CRC_SDR', 'v9_MinAge_EC', 'v9_MinAge_EC_FDR',
    'v9_MinAge_EC_SDR', 'num_sexual_partners', 'first_sexual_intercourse',
    'num_pregnancies', 'hormonal_contraceptives_years', 'iud', 'cytology',
    'cin', 'hpv', 'psa', 'moles_count', 'menopause_hormone', 'fastfood',
    'cannedfood',
}


def validate_calculation_input(post_data, selected_assessments):
    """Validate answers required by the selected assessments.

    The original calculation code still owns type conversion for compatibility,
    but this boundary guarantees that every accessed field exists and contains
    a valid numeric value where appropriate.
    """
    selected_titles = {item.get('title') for item in selected_assessments}
    required_fields = set(COMMON_FIELDS)
    for title in selected_titles:
        required_fields.update(ASSESSMENT_FIELDS.get(title, set()))

    for field_name in required_fields:
        value = post_data.get(field_name)
        if value is None or str(value).strip() == '':
            raise InvalidCalculationInput(f'Missing screening field: {field_name}')
        if field_name in NUMERIC_FIELDS:
            try:
                float(value)
            except (TypeError, ValueError) as exc:
                raise InvalidCalculationInput(
                    f'Invalid numeric screening field: {field_name}'
                ) from exc

    return post_data
