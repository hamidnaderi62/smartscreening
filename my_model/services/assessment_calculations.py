"""Run the selected risk-assessment calculators."""

from ..utils.diabetes import Diabetes
from ..utils.breast_cancer import BreastCancer
from ..utils.crc import CRC
from ..utils.pbcg import ProstateRiskCalculator
from ..utils.ascvd import ASCVD_RiskCalculator
from ..utils.cervical import Cervical_RiskCalculator
from ..utils.melanoma_cancer import Melanoma_RiskCalculator
from ..utils.osteoporosis import Osteoporosis_RiskCalculator
from ..utils.ovarian_cancer import Ovarian_RiskCalculator
from ..utils.pancreatic_cancer import Pancreatic_RiskCalculator
from ..utils.stomach_cancer import Stomach_RiskCalculator
from ..utils.stroke import Stroke_RiskCalculator


def calculate_selected_assessments(post_data, selected_assessments, data):
    """Calculate selected assessments and merge their fields into data."""
    gender = data['gender']
    age = data['age']
    weight = data['weight']
    height = data['height']
    waist_size = data['waist_size']
    ethnicity = data['ethnicity']
    born_place = data['born_place']
    education = data['education']
    activity = data['activity']
    smoking = data['smoking']
    alcohol = data['alcohol']
    meat = data['meat']
    cereal = data['cereal']
    vegetables = data['vegetables']
    dairy = data['dairy']
    multivitamin = data['multivitamin']
    blood_pressure = data['blood_pressure']
    blood_glucose = data['blood_glucose']
    totchol = data['totchol']
    blood_group = data['blood_group']
    previous_cancer = data['previous_cancer']

    # Process each selected assessment
    for item in selected_assessments:
        if item['title'] == 'Diabetes':
            relatives_diabetes = post_data.get('relatives_diabetes')
            diabetes_results = Diabetes.calculate_risk(
                gender, age, weight, height, waist_size, activity,
                vegetables, blood_pressure, blood_glucose, relatives_diabetes,
                ethnicity, born_place, smoking
            )
            diabetes_fields = {
                'relatives_diabetes': relatives_diabetes,
                'ausdrisk_score': diabetes_results['ausdrisk_score'],
                'idf_score': diabetes_results['idf_score'],
                'uk_score': diabetes_results['uk_score'],
                'ada_score': diabetes_results['ada_score'],
                'ausdrisk_status': diabetes_results['ausdrisk_status'],
                'idf_status': diabetes_results['idf_status'],
                'uk_status': diabetes_results['uk_status'],
                'ada_status': diabetes_results['ada_status'],
            }
            data.update(diabetes_fields)

        elif item['title'] == 'Cardiovascular_Disease':
            sbp = float(post_data.get('sbp'))
            hdl = float(post_data.get('hdl'))
            ascvd_score = ASCVD_RiskCalculator.ascvd_10y_accaha(
                ethnicity, gender, age, totchol, hdl, sbp,
                blood_pressure, smoking, blood_glucose
            )
            if ascvd_score is None:
                ascvd_score = 0
                ascvd_status = "Not supported"
            elif ascvd_score < 5:
                ascvd_status = "Low risk"
            elif ascvd_score <= 7.4:
                ascvd_status = "Borderline risk"
            elif ascvd_score < 19.9:
                ascvd_status = "Intermediate risk"
            else:
                ascvd_status = "High risk"

            cardiovascular_fields = {
                'sbp': sbp,
                'hdl': hdl,
                'ascvd_score': ascvd_score,
                'ascvd_status': ascvd_status,
            }
            data.update(cardiovascular_fields)

        elif item['title'] == 'Breast_Cancer':
            biopsy = int(post_data.get('biopsy'))
            biopsy_num = int(post_data.get('biopsy_num'))
            hyperplasia_biopsy = int(post_data.get('hyperplasia_biopsy'))
            menstruation_age = int(post_data.get('menstruation_age'))
            child_age = int(post_data.get('child_age'))
            fdr_cancer = int(post_data.get('fdr_cancer'))
            breastfeeding = post_data.get('breastfeeding')
            cbe = post_data.get('cbe')
            bse = post_data.get('bse')
            mammograms = post_data.get('mammograms')
            syndrome = post_data.get('syndrome')
            gene_mutation = post_data.get('gene_mutation')

            breast_cancer_results = BreastCancer.calculate_risk(
                age, ethnicity, biopsy, biopsy_num, hyperplasia_biopsy,
                menstruation_age, child_age, fdr_cancer, alcohol,
                breastfeeding, cbe, bse, mammograms, syndrome, gene_mutation
            )

            breast_cancer_fields = {
                'biopsy': biopsy,
                'biopsy_num': biopsy_num,
                'hyperplasia_biopsy': hyperplasia_biopsy,
                'menstruation_age': menstruation_age,
                'child_age': child_age,
                'fdr_cancer': fdr_cancer,
                'breastfeeding': breastfeeding,
                'cbe': cbe,
                'bse': bse,
                'mammograms': mammograms,
                'syndrome': syndrome,
                'gene_mutation': gene_mutation,
                'gene_mutation_fdr': breast_cancer_results['gene_mutation_fdr'],
                'gail_score_abs_5': breast_cancer_results['gail_score_abs_5'],
                'gail_score_ave_5': breast_cancer_results['gail_score_ave_5'],
                'gail_score_abs_90': breast_cancer_results['gail_score_abs_90'],
                'gail_score_ave_90': breast_cancer_results['gail_score_ave_90'],
                'mymodel_gail_score': breast_cancer_results['mymodel_gail_score'],
            }
            data.update(breast_cancer_fields)

        elif item['title'] == 'Colorectal_Cancer':
            family_crc = post_data.get('family_crc')
            diabetes = post_data.get('diabetes')
            aspirin = post_data.get('aspirin')
            estrogen = post_data.get('estrogen')
            painmed = post_data.get('painmed')

            v1_v2 = post_data.get('v1_v2')
            v3 = post_data.get('v3')
            v4 = post_data.get('v4')
            v5_AB = post_data.get('v5_AB')
            v5_CD = post_data.get('v5_CD')
            v6_AB = post_data.get('v6_AB')
            v6_CD = post_data.get('v6_CD')
            v7_E = post_data.get('v7_E')
            v7_F = post_data.get('v7_F')
            v8_MinAge_CRC = post_data.get('v8_MinAge_CRC')
            v8_MinAge_CRC_FDR = post_data.get('v8_MinAge_CRC_FDR')
            v8_MinAge_CRC_SDR = post_data.get('v8_MinAge_CRC_SDR')
            v9_MinAge_EC = post_data.get('v9_MinAge_EC')
            v9_MinAge_EC_FDR = post_data.get('v9_MinAge_EC_FDR')
            v9_MinAge_EC_SDR = post_data.get('v9_MinAge_EC_SDR')

            crc_results = CRC.calculate_risk(
                gender, age, ethnicity, smoking, alcohol, weight, height,
                education, family_crc, multivitamin, meat, diabetes,
                activity, aspirin, estrogen, painmed,
                v1_v2, v3, v4, v5_AB, v5_CD, v6_AB, v6_CD,
                v7_E, v7_F, v8_MinAge_CRC, v8_MinAge_CRC_FDR,
                v8_MinAge_CRC_SDR, v9_MinAge_EC, v9_MinAge_EC_FDR,
                v9_MinAge_EC_SDR
            )

            colorectal_fields = {
                'family_crc': family_crc,
                'diabetes': diabetes,
                'aspirin': aspirin,
                'estrogen': estrogen,
                'painmed': painmed,
                'crcpro_score': crc_results['crcpro_score'],
                'crc_history': crc_results['crc_history'],
                'crc2_history': crc_results['crc2_history'],
                'ec_history': crc_results['ec_history'],
                'ls_history': crc_results['ls_history'],
                'crc_fdr': crc_results['crc_fdr'],
                'crc_sdr': crc_results['crc_sdr'],
                'ec_fdr': crc_results['ec_fdr'],
                'ec_sdr': crc_results['ec_sdr'],
                'ls_fdr': crc_results['ls_fdr'],
                'ls_sdr': crc_results['ls_sdr'],
                'min_age_crc': crc_results['min_age_crc'],
                'min_age_crc_fdr': crc_results['min_age_crc_fdr'],
                'min_age_crc_sdr': crc_results['min_age_crc_sdr'],
                'min_age_ec': crc_results['min_age_ec'],
                'min_age_ec_fdr': crc_results['min_age_ec_fdr'],
                'min_age_ec_sdr': crc_results['min_age_ec_sdr'],
                'premm_score': crc_results['premm_score'],
            }
            data.update(colorectal_fields)

        elif item['title'] == 'Cervical_Cancer':
            num_sexual_partners = float(post_data.get('num_sexual_partners'))
            first_sexual_intercourse = float(post_data.get('first_sexual_intercourse'))
            num_pregnancies = float(post_data.get('num_pregnancies'))
            smoking = float(post_data.get('smoking'))
            hormonal_contraceptives_years = float(post_data.get('hormonal_contraceptives_years'))
            iud = float(post_data.get('iud'))
            std = post_data.get('std')
            cervical_cancer = post_data.get('cervical_cancer')
            cytology = float(post_data.get('cytology'))
            cin = float(post_data.get('cin'))
            hpv = float(post_data.get('hpv'))

            cervical_cancer_score = Cervical_RiskCalculator.calculate_risk(
                num_sexual_partners, first_sexual_intercourse, num_pregnancies,
                smoking, hormonal_contraceptives_years, iud, std,
                cervical_cancer, cytology, cin, hpv
            )

            cervical_cancer_grades = {
                1: 'Low risk (Follow up based on your health care provider and national guidline, e.g., USPSTF (174), ACS (177), and ACOG (175))',
                2: 'Follow up by health care provider and likely ask you to come back for additional testing to make sure that there are not more serious (high-grade) changes.)',
                3: 'High risk (Follow up by gynaecologist are needed. Your health care provider will recommend follow-up steps you need to take)',
            }
            cervical_cancer_grade = cervical_cancer_grades.get(cervical_cancer_score)

            cervical_fields = {
                'num_sexual_partners': num_sexual_partners,
                'first_sexual_intercourse': first_sexual_intercourse,
                'num_pregnancies': num_pregnancies,
                'hormonal_contraceptives_years': hormonal_contraceptives_years,
                'iud': iud,
                'std': std,
                'cervical_cancer': cervical_cancer,
                'cytology': cytology,
                'cin': cin,
                'hpv': hpv,
                'cervical_cancer_score': cervical_cancer_score,
                'cervical_cancer_grade': cervical_cancer_grade,
            }
            data.update(cervical_fields)

        elif item['title'] == 'Prostate_Cancer':
            psa = float(post_data.get('psa'))
            famhistory = post_data.get('famhistory')
            dre = post_data.get('dre')
            priorbiopsy = post_data.get('priorbiopsy')

            famhistory_value = 1 if famhistory == 'Yes' else 0
            dre_value = 1 if dre == 'Abnormal' else 0
            priorbiopsy_value = 1 if priorbiopsy == 'Prior negative biopsy' else 0

            pbcg_results = ProstateRiskCalculator.calculate_risk(
                psa, age, int(ethnicity), priorbiopsy_value, dre_value, famhistory_value
            )

            prostate_fields = {
                'psa': psa,
                'famhistory': famhistory,
                'dre': dre,
                'priorbiopsy': priorbiopsy,
                'pbcg_score_no_cancer': pbcg_results['pbcg_score_no_cancer'],
                'pbcg_score_low_cancer': pbcg_results['pbcg_score_low_cancer'],
                'pbcg_score_high_cancer': pbcg_results['pbcg_score_high_cancer'],
            }
            data.update(prostate_fields)

        elif item['title'] == 'Melanoma_Cancer':
            family_melanoma_cancer = post_data.get('family_melanoma_cancer')
            colored_hair = post_data.get('colored_hair')
            colored_eyes = post_data.get('colored_eyes')
            fair_skin = post_data.get('fair_skin')
            moles_count = float(post_data.get('moles_count'))
            sunburns = post_data.get('sunburns')
            sunlamp = post_data.get('sunlamp')
            immunosuppressive_drugs = post_data.get('immunosuppressive_drugs')

            melanoma_cancer_score = Melanoma_RiskCalculator.calculate_risk(
                previous_cancer, family_melanoma_cancer, colored_hair,
                colored_eyes, fair_skin, moles_count, sunburns,
                sunlamp, immunosuppressive_drugs
            )

            melanoma_fields = {
                'family_melanoma_cancer': family_melanoma_cancer,
                'colored_hair': colored_hair,
                'colored_eyes': colored_eyes,
                'fair_skin': fair_skin,
                'moles_count': moles_count,
                'sunburns': sunburns,
                'sunlamp': sunlamp,
                'immunosuppressive_drugs': immunosuppressive_drugs,
                'melanoma_cancer_score': melanoma_cancer_score,
            }
            data.update(melanoma_fields)

        elif item['title'] == 'Osteoporosis':
            rheumatoid_arthritis = post_data.get('rheumatoid_arthritis')
            have_bmd_test = post_data.get('have_bmd_test')
            result_bmd_test = post_data.get('result_bmd_test')
            chemotherapy = post_data.get('chemotherapy')
            steroid = post_data.get('steroid')
            anticonvulsants = post_data.get('anticonvulsants')
            calcium_supplements = post_data.get('calcium_supplements')
            vitamin_d = post_data.get('vitamin_d')
            family_break_bone = post_data.get('family_break_bone')

            osteoporosis_score = Osteoporosis_RiskCalculator.calculate_risk(
                rheumatoid_arthritis, have_bmd_test, result_bmd_test,
                blood_glucose, chemotherapy, steroid, anticonvulsants,
                multivitamin, cereal, vegetables, dairy,
                calcium_supplements, vitamin_d, alcohol,
                smoking, activity, family_break_bone
            )

            osteoporosis_fields = {
                'rheumatoid_arthritis': rheumatoid_arthritis,
                'have_bmd_test': have_bmd_test,
                'result_bmd_test': result_bmd_test,
                'chemotherapy': chemotherapy,
                'steroid': steroid,
                'anticonvulsants': anticonvulsants,
                'calcium_supplements': calcium_supplements,
                'vitamin_d': vitamin_d,
                'family_break_bone': family_break_bone,
                'osteoporosis_score': osteoporosis_score,
            }
            data.update(osteoporosis_fields)

        elif item['title'] == 'Ovarian_Cancer':
            family_breast_ovarian_prostate = post_data.get('family_breast_ovarian_prostate')
            family_ovarian_cancer = post_data.get('family_ovarian_cancer')
            gene_mutation = post_data.get('gene_mutation')
            talcum_powder = post_data.get('talcum_powder')
            hormonal_contraceptives_years = float(
                post_data.get('hormonal_contraceptives_years')
            )
            num_pregnancies = float(post_data.get('num_pregnancies'))
            breastfeeding = post_data.get('breastfeeding')
            menopause = post_data.get('menopause')
            menopause_hormone = float(post_data.get('menopause_hormone'))
            hysterectomy = post_data.get('hysterectomy')
            endometriosis = post_data.get('endometriosis')
            salpingectomy = post_data.get('salpingectomy')

            ovarian_cancer_score = Ovarian_RiskCalculator.calculate_risk(
                previous_cancer, family_breast_ovarian_prostate,
                family_ovarian_cancer, gene_mutation, talcum_powder,
                hormonal_contraceptives_years, num_pregnancies,
                menopause, menopause_hormone, breastfeeding,
                hysterectomy, endometriosis, salpingectomy
            )

            ovarian_fields = {
                'family_breast_ovarian_prostate': family_breast_ovarian_prostate,
                'family_ovarian_cancer': family_ovarian_cancer,
                'talcum_powder': talcum_powder,
                'menopause': menopause,
                'menopause_hormone': menopause_hormone,
                'hysterectomy': hysterectomy,
                'endometriosis': endometriosis,
                'salpingectomy': salpingectomy,
                'ovarian_cancer_score': ovarian_cancer_score,
            }
            data.update(ovarian_fields)

        elif item['title'] == 'Pancreatic_Cancer':
            family_pancreatic_cancer = post_data.get('family_pancreatic_cancer')
            chronic_pancreatitis = post_data.get('chronic_pancreatitis')

            pancreatic_cancer_score = Pancreatic_RiskCalculator.calculate_risk(
                previous_cancer, family_pancreatic_cancer, alcohol,
                smoking, blood_glucose, blood_group, chronic_pancreatitis
            )

            pancreatic_fields = {
                'family_pancreatic_cancer': family_pancreatic_cancer,
                'chronic_pancreatitis': chronic_pancreatitis,
                'pancreatic_cancer_score': pancreatic_cancer_score,
            }
            data.update(pancreatic_fields)

        elif item['title'] == 'Stomach_Cancer':
            family_stomach_cancer = post_data.get('family_stomach_cancer')
            fastfood = float(post_data.get('fastfood'))
            cannedfood = float(post_data.get('cannedfood'))
            h_pylori = post_data.get('h_pylori')

            stomach_cancer_score = Stomach_RiskCalculator.calculate_risk(
                previous_cancer, family_stomach_cancer, fastfood,
                cannedfood, alcohol, smoking, h_pylori, blood_group
            )

            stomach_fields = {
                'family_stomach_cancer': family_stomach_cancer,
                'fastfood': fastfood,
                'cannedfood': cannedfood,
                'h_pylori': h_pylori,
                'stomach_cancer_score': stomach_cancer_score,
            }
            data.update(stomach_fields)

        elif item['title'] == 'Stroke':
            previous_stroke = post_data.get('previous_stroke')
            history_totchol = post_data.get('history_totchol')
            family_history_stroke = post_data.get('family_history_stroke')

            stroke_score = Stroke_RiskCalculator.calculate_risk(
                previous_stroke, waist_size, cereal, vegetables,
                alcohol, smoking, activity, blood_glucose,
                blood_pressure, history_totchol, totchol,
                family_history_stroke
            )

            stroke_fields = {
                'previous_stroke': previous_stroke,
                'history_totchol': history_totchol,
                'family_history_stroke': family_history_stroke,
                'stroke_score': stroke_score,
            }
            data.update(stroke_fields)
