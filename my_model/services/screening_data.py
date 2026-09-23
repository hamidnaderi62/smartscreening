"""Build the structured answer snapshot stored with a screening record."""

from .serialization import convert_numpy_to_python


COMMON_SECTIONS = {
    'demographic': (
        ('age', 'Age (years)'),
        ('weight', 'Weight (kg)'),
        ('height', 'Height (cm)'),
        ('waist_size', 'Waist circumference (cm)'),
        ('education', 'Education level (years)'),
        ('born_place', 'Place of Birth'),
        ('ethnicity', 'Ethnicity'),
        ('blood_group', 'Blood Group'),
    ),
    'lifestyle': (
        ('activity', 'Average daily physical activity (hours/day)'),
        ('smoking', 'Number of cigarette packs per year'),
        ('alcohol', 'Average alcohol consumption (shots/day)'),
        ('meat', 'Average daily red meat consumption (grams/day)'),
        ('cereal', 'Eat fortified breakfast cereals most days'),
        ('vegetables', 'Frequency of fruit and vegetable consumption'),
        ('dairy', 'Servings of milk or dairy products per day'),
        ('multivitamin', 'Regular use of multivitamins'),
    ),
    'medical': (
        ('blood_pressure', 'Ever taken medication for high blood pressure'),
        ('blood_glucose', 'Ever told you have high blood sugar'),
        ('totchol', 'Total cholesterol level (mg/dL)'),
        ('previous_cancer', 'History of cancer'),
    ),
}


# Entries are (stored key, display question, optional source key).
ASSESSMENT_FIELDS = {
    'Diabetes': (
        ('relatives_diabetes', 'Family member diagnosed with diabetes'),
        ('idf_score', 'Diabetes Risk Score'),
        ('ausdrisk_score', 'AUSDRISK Score'),
        ('uk_score', 'UK Diabetes Risk Score'),
        ('ada_score', 'ADA Diabetes Risk Score'),
    ),
    'Breast_Cancer': (
        ('biopsy', 'Ever had a breast biopsy with benign diagnosis'),
        ('biopsy_num', 'Number of breast biopsies with benign diagnosis'),
        ('hyperplasia_biopsy', 'Ever had a breast biopsy with atypical hyperplasia'),
        ('menstruation_age', 'Age at first menstruation'),
        ('child_age', 'Age at first childbirth'),
        ('fdr_cancer', 'First-degree relatives with breast cancer'),
        ('breastfeeding', 'Breastfeeding history'),
        ('cbe', 'Clinical Breast Examination'),
        ('bse', 'Breast Self-Examination'),
        ('mammograms', 'Mammogram results'),
        ('syndrome', 'Li-Fraumeni, Cowden, or Bannayan-Riley-Ruvalcaba syndrome'),
        ('gene_mutation', 'Known BRCA1 or BRCA2 gene mutation'),
        ('gail_score', 'Gail Model Risk Score', 'mymodel_gail_score'),
    ),
    'Cardiovascular_Disease': (
        ('sbp', 'Systolic blood pressure (mm Hg)'),
        ('hdl', 'HDL cholesterol level (mg/dL)'),
        ('ascvd_score', 'ASCVD Risk Score (10-year)'),
    ),
    'Prostate_Cancer': (
        ('psa', 'PSA blood test result (ng/mL)'),
        ('famhistory', 'Family history of prostate cancer'),
        ('dre', 'Digital Rectal Exam (DRE) result'),
        ('priorbiopsy', 'Prior biopsy history'),
        ('pbcg_no_cancer', 'PBCG No Cancer Risk (%)', 'pbcg_score_no_cancer'),
        ('pbcg_low_cancer', 'PBCG Low-Grade Cancer Risk (%)', 'pbcg_score_low_cancer'),
        ('pbcg_high_cancer', 'PBCG High-Grade Cancer Risk (%)', 'pbcg_score_high_cancer'),
    ),
    'Cervical_Cancer': (
        ('num_sexual_partners', 'Number of sexual partners'),
        ('first_sexual_intercourse', 'Age at first sexual intercourse'),
        ('num_pregnancies', 'Number of pregnancies'),
        ('hormonal_contraceptives_years', 'Years using hormonal contraceptives'),
        ('iud', 'Years using IUD'),
        ('std', 'History of STD'),
        ('cervical_cancer', 'Family history of cervical cancer'),
        ('cytology', 'Cytology result'),
        ('cin', 'Pathology result (CIN grade)'),
        ('hpv', 'HPV test result'),
        ('cervical_cancer_score', 'Cervical Cancer Risk Score'),
    ),
    'Colorectal_Cancer': (
        ('family_crc', 'Family history of colorectal cancer'),
        ('diabetes', 'History of diabetes'),
        ('aspirin', 'Aspirin/Estrogen use'),
        ('estrogen', 'Estrogen use'),
        ('painmed', 'Regular use of NSAIDs'),
        ('v1_v2', 'Number of separate colorectal cancers'),
        ('v3', 'History of endometrial cancer'),
        ('v4', 'History of another Lynch syndrome-related cancer'),
        ('v5_AB', 'First-degree relatives with colorectal cancer'),
        ('v5_CD', 'Second-degree relatives with colorectal cancer'),
        ('v6_AB', 'First-degree relatives with endometrial cancer'),
        ('v6_CD', 'Second-degree relatives with endometrial cancer'),
        ('v7_E', 'Other first-degree relatives with Lynch syndrome-related cancer'),
        ('v7_F', 'Other second-degree relatives with Lynch syndrome-related cancer'),
        ('v8_MinAge_CRC', 'Age at first colorectal cancer diagnosis'),
        ('v8_MinAge_CRC_FDR', 'Youngest first-degree relative with colorectal cancer (age)'),
        ('v8_MinAge_CRC_SDR', 'Youngest second-degree relative with colorectal cancer (age)'),
        ('v9_MinAge_EC', 'Age at first endometrial cancer diagnosis'),
        ('v9_MinAge_EC_FDR', 'Youngest first-degree relative with endometrial cancer (age)'),
        ('v9_MinAge_EC_SDR', 'Youngest second-degree relative with endometrial cancer (age)'),
        ('premm_score', 'PREMM Lynch Syndrome Risk Score (%)'),
        ('crcpro_score', 'CRCPro Risk Score (%)'),
    ),
    'Melanoma_Cancer': (
        ('family_melanoma_cancer', 'History of skin cancer in siblings and parents'),
        ('colored_hair', 'Naturally blonde or red hair'),
        ('colored_eyes', 'Naturally blue, green, or hazel eyes'),
        ('fair_skin', 'Fair skin'),
        ('moles_count', 'Number of moles on arms (≥3mm)'),
        ('sunburns', 'Severe and frequent sunburns in childhood'),
        ('sunlamp', 'Ever used tanning bed or sunlamp'),
        ('immunosuppressive_drugs', 'Ever taken immunosuppressive drugs'),
        ('melanoma_score', 'Melanoma Cancer Risk Score', 'melanoma_cancer_score'),
    ),
    'Osteoporosis': (
        ('rheumatoid_arthritis', 'Ever told you have rheumatoid arthritis'),
        ('have_bmd_test', 'Ever had a bone mineral density test'),
        ('result_bmd_test', 'Last BMD test result'),
        ('chemotherapy', 'Ever undergone chemotherapy for cancer'),
        ('steroid', 'Taking steroid pills for 3+ consecutive months'),
        ('anticonvulsants', 'Use of anticonvulsant medications'),
        ('calcium_supplements', 'Take calcium supplements most days'),
        ('vitamin_d', 'Take vitamin D supplement most days'),
        ('family_break_bone', 'Mother or father broke bone after age 50'),
        ('osteoporosis_score', 'Osteoporosis Risk Score'),
    ),
    'Ovarian_Cancer': (
        ('family_breast_ovarian_prostate', 'Multiple family members with breast, ovarian, prostate cancer'),
        ('family_ovarian_cancer', 'Mother or sister with ovarian cancer'),
        ('gene_mutation', 'Known BRCA1 or BRCA2 gene mutation'),
        ('talcum_powder', 'Regular use of talcum powder'),
        ('hormonal_contraceptives_years', 'Years using hormonal contraceptives'),
        ('num_pregnancies', 'Number of pregnancies'),
        ('breastfeeding', 'Breastfeeding history'),
        ('menopause', 'Early menopause'),
        ('menopause_hormone', 'Duration of menopausal hormone therapy'),
        ('hysterectomy', 'Hysterectomy (removal of uterus)'),
        ('endometriosis', 'History of endometriosis'),
        ('salpingectomy', 'Tubal ligation or salpingectomy'),
        ('ovarian_score', 'Ovarian Cancer Risk Score', 'ovarian_cancer_score'),
    ),
    'Pancreatic_Cancer': (
        ('family_pancreatic_cancer', 'Brother, sister, or parent with pancreatic cancer'),
        ('chronic_pancreatitis', 'History of chronic pancreatitis'),
        ('pancreatic_score', 'Pancreatic Cancer Risk Score', 'pancreatic_cancer_score'),
    ),
    'Stomach_Cancer': (
        ('family_stomach_cancer', 'Brother, sister, or parent with stomach cancer'),
        ('fastfood', 'Meals per week at restaurant/fast food'),
        ('cannedfood', 'Frequency of canned/processed foods'),
        ('h_pylori', 'History of H. Pylori infection'),
        ('stomach_score', 'Stomach Cancer Risk Score', 'stomach_cancer_score'),
    ),
    'Stroke': (
        ('previous_stroke', 'History of stroke'),
        ('history_totchol', 'Ever told total cholesterol is high'),
        ('family_history_stroke', 'Close family member had heart attack or stroke'),
        ('stroke_score', 'Stroke Risk Score'),
    ),
}


def _answer(data, source_key):
    return {'answer': convert_numpy_to_python(data.get(source_key))}


def _question_answer(data, key, question, source_key=None):
    # Keep the stable key alongside the legacy English label.  New reports
    # translate from question_key; old records can still use question.
    result = {'question_key': key, 'question': question}
    result.update(_answer(data, source_key or key))
    return result


def _section(data, fields):
    return {
        key: _question_answer(data, key, question, source_key)
        for entry in fields
        for key, question, *source in (entry,)
        for source_key in [source[0] if source else None]
    }


def collect_screening_data(selected_assessments, data):
    """Return a JSON-safe, human-readable snapshot of screening answers."""
    screening_data = {
        section_name: _section(data, fields)
        for section_name, fields in COMMON_SECTIONS.items()
    }
    screening_data['assessments'] = {}

    for assessment in selected_assessments:
        assessment_data = _section(
            data,
            ASSESSMENT_FIELDS.get(assessment['title'], ()),
        )
        optional_fields = (
            ('risk_status', 'Risk Status', assessment.get('status_en')),
            ('recommendation', 'Doctor Recommendation', assessment.get('recommendation_en')),
            ('risk_score', 'Risk Score', assessment.get('score')),
            ('max_score', 'Maximum Score', assessment.get('total_score')),
            ('risk_level', 'Risk Level', assessment.get('color_class')),
        )
        for key, question, answer in optional_fields:
            if answer is not None:
                assessment_data[key] = {
                    'question_key': key,
                    'question': question,
                    'answer': convert_numpy_to_python(answer),
                }
        screening_data['assessments'][assessment['title']] = assessment_data

    return convert_numpy_to_python(screening_data)
