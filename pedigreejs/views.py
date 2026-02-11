import json
import random
import string
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from .models import Pedigree
from .utils.breast_cancer import *
from .utils.crc import *


def generate_random_id(length=4):
    """Generate random ID for family members"""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))


def pedigreejs_index_fa(request):
    """Main index page for pedigree application"""
    return render(request, 'pedigreejs/pedigreejs_index_fa.html')


def pedigree_form_view(request):
    """Main form view for adding family members"""
    if request.method == 'POST':
        # Handle form submission to save pedigree
        return save_pedigree_from_form(request)

    return render(request, 'pedigreejs/pedigree_form.html')


@csrf_exempt
def save_pedigree_from_form1(request):
    """Save pedigree data from form submission"""
    if request.method == 'POST':
        code = request.POST.get('code', '').strip()

        if not code:
            return JsonResponse({'success': False, 'message': 'کد الزامی است'})

        # Generate pedigree JSON from form data
        pedigree_data = generate_pedigree_json_from_form(request.POST)

        ### Calculate Cancer Risk Score
        print('aaaaaaaaaaaa')
        # Demographic Info
        gender_raw = request.POST.get('gender')
        gender = 'Male' if gender_raw == 'M' else 'Female'

        age = float(request.POST.get('age'))
        weight = float(request.POST.get('weight'))
        height = float(request.POST.get('height'))
        waist_size = float(request.POST.get('waist_size'))
        ethnicity = int(request.POST.get('ethnicity'))
        born_place = request.POST.get('born_place')
        education = float(request.POST.get('education'))
        blood_group = request.POST.get('blood_group')

        # Life Style
        activity = float(request.POST.get('activity'))
        smoking = float(request.POST.get('smoking'))
        alcohol = float(request.POST.get('alcohol'))
        meat = float(request.POST.get('meat'))
        cereal = request.POST.get('cereal')
        vegetables = request.POST.get('vegetables')
        dairy = float(request.POST.get('dairy'))
        multivitamin = request.POST.get('multivitamin')

        # Medical
        blood_pressure = request.POST.get('blood_pressure')
        blood_glucose = request.POST.get('blood_glucose')
        totchol = float(request.POST.get('totchol'))
        previous_cancer = request.POST.get('previous_cancer')

        # Breast_Cancer
        biopsy = int(request.POST.get('biopsy'))
        biopsy_num = int(request.POST.get('biopsy_num'))
        hyperplasia_biopsy = int(request.POST.get('hyperplasia_biopsy'))
        menstruation_age = int(request.POST.get('menstruation_age'))
        child_age = int(request.POST.get('child_age'))
        fdr_cancer = int(request.POST.get('fdr_cancer'))
        breastfeeding = request.POST.get('breastfeeding')
        cbe = request.POST.get('cbe')
        bse = request.POST.get('bse')
        mammograms = request.POST.get('mammograms')
        syndrome = request.POST.get('syndrome')
        gene_mutation = request.POST.get('gene_mutation')
        breast_cancer_results = BreastCancer.calculate_risk(
            age,
            ethnicity,
            biopsy,
            biopsy_num,
            hyperplasia_biopsy,
            menstruation_age,
            child_age,
            fdr_cancer,
            alcohol,
            breastfeeding,
            cbe,
            bse,
            mammograms,
            syndrome,
            gene_mutation
        )
        gail_score_abs_5 = breast_cancer_results['gail_score_abs_5']
        gail_score_ave_5 = breast_cancer_results['gail_score_ave_5']
        gail_score_abs_90 = breast_cancer_results['gail_score_abs_90']
        gail_score_ave_90 = breast_cancer_results['gail_score_ave_90']
        mymodel_gail_score = breast_cancer_results['mymodel_gail_score']
        gene_mutation_fdr = breast_cancer_results['gene_mutation_fdr']

        print(f'gail_score_abs_5 : {gail_score_abs_5}')
        print(f'gail_score_ave_5 : {gail_score_ave_5}')
        print(f'gail_score_abs_90 : {gail_score_abs_90}')
        print(f'gail_score_ave_90 : {gail_score_ave_90}')
        print(f'mymodel_gail_score : {mymodel_gail_score}')

        # Colorectal_Cancer
        family_crc = request.POST.get('family_crc')
        diabetes = request.POST.get('diabetes')
        aspirin = request.POST.get('aspirin')  # male
        estrogen = request.POST.get('estrogen')  # female
        painmed = request.POST.get('painmed')  # female

        v1_v2 = request.POST.get('v1_v2')
        v3 = request.POST.get('v3')
        v4 = request.POST.get('v4')
        v5_AB = request.POST.get('v5_AB')
        v5_CD = request.POST.get('v5_CD')
        v6_AB = request.POST.get('v6_AB')
        v6_CD = request.POST.get('v6_CD')
        v7_E = request.POST.get('v7_E')
        v7_F = request.POST.get('v7_F')
        v8_MinAge_CRC = request.POST.get('v8_MinAge_CRC')
        v8_MinAge_CRC_FDR = request.POST.get('v8_MinAge_CRC_FDR')
        v8_MinAge_CRC_SDR = request.POST.get('v8_MinAge_CRC_SDR')
        v9_MinAge_EC = request.POST.get('v9_MinAge_EC')
        v9_MinAge_EC_FDR = request.POST.get('v9_MinAge_EC_FDR')
        v9_MinAge_EC_SDR = request.POST.get('v9_MinAge_EC_SDR')

        crc_results = CRC.calculate_risk(
            gender,
            age,
            ethnicity,
            smoking,
            alcohol,
            weight,
            height,
            education,
            family_crc,
            multivitamin,
            meat,
            diabetes,
            activity,  # male
            aspirin,  # male
            estrogen,  # female
            painmed,  # female

            v1_v2,
            v3,
            v4,
            v5_AB,
            v5_CD,
            v6_AB,
            v6_CD,
            v7_E,
            v7_F,
            v8_MinAge_CRC,
            v8_MinAge_CRC_FDR,
            v8_MinAge_CRC_SDR,
            v9_MinAge_EC,
            v9_MinAge_EC_FDR,
            v9_MinAge_EC_SDR
        )

        crc_history = crc_results['crc_history']
        crc2_history = crc_results['crc2_history']
        ec_history = crc_results['ec_history']
        ls_history = crc_results['ls_history']
        crc_fdr = crc_results['crc_fdr']
        crc_sdr = crc_results['crc_sdr']
        ec_fdr = crc_results['ec_fdr']
        ec_sdr = crc_results['ec_sdr']
        ls_fdr = crc_results['ls_fdr']
        ls_sdr = crc_results['ls_sdr']
        min_age_crc = crc_results['min_age_crc']
        min_age_crc_fdr = crc_results['min_age_crc_fdr']
        min_age_crc_sdr = crc_results['min_age_crc_sdr']
        min_age_ec = crc_results['min_age_ec']
        min_age_ec_fdr = crc_results['min_age_ec_fdr']
        min_age_ec_sdr = crc_results['min_age_ec_sdr']
        crcpro_score = crc_results['crcpro_score']
        crcpro_threshold = crc_results['crcpro_threshold']
        premm_score = crc_results['premm_score']
        premm_threshold = crc_results['premm_threshold']

        print(f'crcpro_score : {crcpro_score}')
        print(f'premm_score : {premm_score}')

        # Save to database
        try:
            pedigree, created = Pedigree.objects.update_or_create(
                code=code,
                defaults={
                    'famid': 'FAM1',
                    'pedigree_data': pedigree_data
                }
            )

            return JsonResponse({
                'success': True,
                'message': f'شجره با موفقیت {"ذخیره" if created else "به روز"} شد',
                'code': code
            })

        except Exception as e:
            return JsonResponse({'success': False, 'message': f'خطا در ذخیره سازی: {str(e)}'})

    return JsonResponse({'success': False, 'message': 'درخواست نامعتبر'})


def save_pedigree_from_form(request):
    """Save pedigree data from form submission"""
    if request.method == 'POST':
        code = request.POST.get('code', '').strip()

        if not code:
            return JsonResponse({'success': False, 'message': 'کد الزامی است'})

        # Generate pedigree JSON from form data
        pedigree_data = generate_pedigree_json_from_form(request.POST)

        ### Calculate Cancer Risk Score
        print('aaaaaaaaaaaa')
        # Demographic Info
        gender_raw = request.POST.get('gender')
        gender = 'Male' if gender_raw == 'M' else 'Female'

        age = float(request.POST.get('age'))
        weight = float(request.POST.get('weight'))
        height = float(request.POST.get('height'))
        waist_size = float(request.POST.get('waist_size'))
        ethnicity = int(request.POST.get('ethnicity'))
        born_place = request.POST.get('born_place')
        education = float(request.POST.get('education'))
        blood_group = request.POST.get('blood_group')

        # Life Style
        activity = float(request.POST.get('activity'))
        smoking = float(request.POST.get('smoking'))
        alcohol = float(request.POST.get('alcohol'))
        meat = float(request.POST.get('meat'))
        cereal = request.POST.get('cereal')
        vegetables = request.POST.get('vegetables')
        dairy = float(request.POST.get('dairy'))
        multivitamin = request.POST.get('multivitamin')

        # Medical
        blood_pressure = request.POST.get('blood_pressure')
        blood_glucose = request.POST.get('blood_glucose')
        totchol = float(request.POST.get('totchol'))
        previous_cancer = request.POST.get('previous_cancer')

        # Breast_Cancer
        biopsy = int(request.POST.get('biopsy'))
        biopsy_num = int(request.POST.get('biopsy_num'))
        hyperplasia_biopsy = int(request.POST.get('hyperplasia_biopsy'))
        menstruation_age = int(request.POST.get('menstruation_age'))
        child_age = int(request.POST.get('child_age'))
        fdr_cancer = int(request.POST.get('fdr_cancer'))
        breastfeeding = request.POST.get('breastfeeding')
        cbe = request.POST.get('cbe')
        bse = request.POST.get('bse')
        mammograms = request.POST.get('mammograms')
        syndrome = request.POST.get('syndrome')
        gene_mutation = request.POST.get('gene_mutation')
        breast_cancer_results = BreastCancer.calculate_risk(
            age,
            ethnicity,
            biopsy,
            biopsy_num,
            hyperplasia_biopsy,
            menstruation_age,
            child_age,
            fdr_cancer,
            alcohol,
            breastfeeding,
            cbe,
            bse,
            mammograms,
            syndrome,
            gene_mutation
        )
        gail_score_abs_5 = breast_cancer_results['gail_score_abs_5']
        gail_score_ave_5 = breast_cancer_results['gail_score_ave_5']
        gail_score_abs_90 = breast_cancer_results['gail_score_abs_90']
        gail_score_ave_90 = breast_cancer_results['gail_score_ave_90']
        mymodel_gail_score = breast_cancer_results['mymodel_gail_score']
        gene_mutation_fdr = breast_cancer_results['gene_mutation_fdr']

        print(f'gail_score_abs_5 : {gail_score_abs_5}')
        print(f'gail_score_ave_5 : {gail_score_ave_5}')
        print(f'gail_score_abs_90 : {gail_score_abs_90}')
        print(f'gail_score_ave_90 : {gail_score_ave_90}')
        print(f'mymodel_gail_score : {mymodel_gail_score}')

        # Colorectal_Cancer
        family_crc = request.POST.get('family_crc')
        diabetes = request.POST.get('diabetes')
        aspirin = request.POST.get('aspirin')  # male
        estrogen = request.POST.get('estrogen')  # female
        painmed = request.POST.get('painmed')  # female

        v1_v2 = request.POST.get('v1_v2')
        v3 = request.POST.get('v3')
        v4 = request.POST.get('v4')
        v5_AB = request.POST.get('v5_AB')
        v5_CD = request.POST.get('v5_CD')
        v6_AB = request.POST.get('v6_AB')
        v6_CD = request.POST.get('v6_CD')
        v7_E = request.POST.get('v7_E')
        v7_F = request.POST.get('v7_F')
        v8_MinAge_CRC = request.POST.get('v8_MinAge_CRC')
        v8_MinAge_CRC_FDR = request.POST.get('v8_MinAge_CRC_FDR')
        v8_MinAge_CRC_SDR = request.POST.get('v8_MinAge_CRC_SDR')
        v9_MinAge_EC = request.POST.get('v9_MinAge_EC')
        v9_MinAge_EC_FDR = request.POST.get('v9_MinAge_EC_FDR')
        v9_MinAge_EC_SDR = request.POST.get('v9_MinAge_EC_SDR')

        crc_results = CRC.calculate_risk(
            gender,
            age,
            ethnicity,
            smoking,
            alcohol,
            weight,
            height,
            education,
            family_crc,
            multivitamin,
            meat,
            diabetes,
            activity,  # male
            aspirin,  # male
            estrogen,  # female
            painmed,  # female

            v1_v2,
            v3,
            v4,
            v5_AB,
            v5_CD,
            v6_AB,
            v6_CD,
            v7_E,
            v7_F,
            v8_MinAge_CRC,
            v8_MinAge_CRC_FDR,
            v8_MinAge_CRC_SDR,
            v9_MinAge_EC,
            v9_MinAge_EC_FDR,
            v9_MinAge_EC_SDR
        )

        crc_history = crc_results['crc_history']
        crc2_history = crc_results['crc2_history']
        ec_history = crc_results['ec_history']
        ls_history = crc_results['ls_history']
        crc_fdr = crc_results['crc_fdr']
        crc_sdr = crc_results['crc_sdr']
        ec_fdr = crc_results['ec_fdr']
        ec_sdr = crc_results['ec_sdr']
        ls_fdr = crc_results['ls_fdr']
        ls_sdr = crc_results['ls_sdr']
        min_age_crc = crc_results['min_age_crc']
        min_age_crc_fdr = crc_results['min_age_crc_fdr']
        min_age_crc_sdr = crc_results['min_age_crc_sdr']
        min_age_ec = crc_results['min_age_ec']
        min_age_ec_fdr = crc_results['min_age_ec_fdr']
        min_age_ec_sdr = crc_results['min_age_ec_sdr']
        crcpro_score = crc_results['crcpro_score']
        crcpro_threshold = crc_results['crcpro_threshold']
        premm_score = crc_results['premm_score']
        premm_threshold = crc_results['premm_threshold']

        print(f'crcpro_score : {crcpro_score}')
        print(f'premm_score : {premm_score}')

        # Prepare risk data as JSON
        risk_data = {
            'breast_cancer': {
                'gail_score_abs_5': gail_score_abs_5,
                'gail_score_ave_5': gail_score_ave_5,
                'gail_score_abs_90': gail_score_abs_90,
                'gail_score_ave_90': gail_score_ave_90,
                'mymodel_gail_score': mymodel_gail_score,
                'gene_mutation_fdr': gene_mutation_fdr
            },
            'colorectal_cancer': {
                'crcpro_score': crcpro_score,
                'crcpro_threshold': crcpro_threshold,
                'premm_score': premm_score,
                'premm_threshold': premm_threshold
            }
        }

        # Save to database
        try:
            pedigree, created = Pedigree.objects.update_or_create(
                code=code,
                defaults={
                    'famid': 'FAM1',
                    'pedigree_data': pedigree_data,
                    'risk_data': risk_data  # Add risk data here
                }
            )

            return JsonResponse({
                'success': True,
                'message': f'شجره با موفقیت {"ذخیره" if created else "به روز"} شد',
                'code': code
            })

        except Exception as e:
            return JsonResponse({'success': False, 'message': f'خطا در ذخیره سازی: {str(e)}'})

    return JsonResponse({'success': False, 'message': 'درخواست نامعتبر'})


def generate_pedigree_json_from_form(form_data):
    """Generate pedigree JSON structure from form data matching the sample format"""
    pedigree_data = []

    # Get form values
    main_name = form_data.get('name', '')
    main_gender = form_data.get('gender', 'F')
    main_age = int(form_data.get('age', '60'))
    main_affected = form_data.get('affected', 'H')
    cancer_type = form_data.get('cancer_type', '')
    age_diagnosis = form_data.get('age_diagnosis', '')

    # Generate IDs
    main_person_id = generate_random_id()
    father_id = generate_random_id()
    mother_id = generate_random_id()
    grandfather_father_id = generate_random_id()
    grandmother_father_id = generate_random_id()
    grandfather_mother_id = generate_random_id()
    grandmother_mother_id = generate_random_id()

    # 1. Main person (proband)
    main_person = {
        "famid": "FAM1",
        "name": main_person_id,
        "sex": main_gender,
        "status": "0",
        "father": father_id,
        "mother": mother_id,
        "age": str(main_age),
        "display_name": main_name,
        "level": 1
    }

    # Add cancer information if affected
    if main_affected == 'C' and cancer_type and age_diagnosis:
        cancer_field_map = {
            'Breast': 'breast_cancer_diagnosis_age',
            'Ovarian': 'ovarian_cancer_diagnosis_age',
            'Pancreatic': 'pancreatic_cancer_diagnosis_age',
            'Prostate': 'prostate_cancer_diagnosis_age'
        }
        cancer_field = cancer_field_map.get(cancer_type)
        if cancer_field:
            main_person[cancer_field] = age_diagnosis

    pedigree_data.append(main_person)

    # 2. Parents (Level 1) - with display names
    father_age = main_age + 30  # Increased to match sample (80 for 55-year-old)
    mother_age = main_age + 30

    father_data = {
        "famid": "FAM1",
        "name": father_id,
        "sex": "M",
        "status": "0",
        "father": grandfather_father_id,
        "mother": grandmother_father_id,
        "display_name": "پدر",
        "level": 1
    }

    mother_data = {
        "famid": "FAM1",
        "name": mother_id,
        "sex": "F",
        "status": "0",
        "father": grandfather_mother_id,
        "mother": grandmother_mother_id,
        "display_name": "مادر",
        "level": 1
    }

    pedigree_data.extend([father_data, mother_data])

    # 3. Grandparents (Level 2 - top level) - with display names
    grandparent_age = main_age + 55  # Increased to match sample (105 for 55-year-old)

    grandparents = [
        {
            "famid": "FAM1",
            "name": grandfather_father_id,
            "sex": "M",
            "status": "0",
            "display_name": "پدر بزرگ پدری",
            "level": 2,
            "top_level": True
        },
        {
            "famid": "FAM1",
            "name": grandmother_father_id,
            "sex": "F",
            "status": "0",
            "display_name": "مادر بزرگ پدری",
            "level": 2,
            "top_level": True
        },
        {
            "famid": "FAM1",
            "name": grandfather_mother_id,
            "sex": "M",
            "status": "0",
            "display_name": "پدر بزرگ مادری",
            "level": 2,
            "top_level": True
        },
        {
            "famid": "FAM1",
            "name": grandmother_mother_id,
            "sex": "F",
            "status": "0",
            "display_name": "مادر بزرگ مادری",
            "level": 2,
            "top_level": True
        }
    ]

    pedigree_data.extend(grandparents)

    # 4. Generate siblings
    brothers_count = int(form_data.get('brothers', 0))
    sisters_count = int(form_data.get('sisters', 0))

    # Generate brothers
    for i in range(brothers_count):
        brother_age = max(1, main_age - random.randint(0, 5))
        brother_data = {
            "famid": "FAM1",
            "name": generate_random_id(),
            "sex": "M",
            "status": "0",
            "father": father_id,
            "mother": mother_id,
            "display_name": f"برادر {i + 1}"
        }
        pedigree_data.append(brother_data)

    # Generate sisters
    for i in range(sisters_count):
        sister_age = max(1, main_age - random.randint(0, 5))
        sister_data = {
            "famid": "FAM1",
            "name": generate_random_id(),
            "sex": "F",
            "status": "0",
            "father": father_id,
            "mother": mother_id,
            "display_name": f"خواهر {i + 1}"
        }
        pedigree_data.append(sister_data)

    # 5. Generate spouse and children - CORRECTED STRUCTURE
    sons_count = int(form_data.get('sons', 0))
    daughters_count = int(form_data.get('daughters', 0))

    if sons_count > 0 or daughters_count > 0:
        # Generate spouse - CORRECTED: no famid, has noparents, and proper parent references
        spouse_id = generate_random_id()
        spouse_gender = 'M' if main_gender == 'F' else 'F'
        spouse_age = max(1, main_age - random.randint(0, 5))

        spouse_data = {
            "famid": "FAM1",
            "name": spouse_id,
            "sex": spouse_gender,
            "mother": mother_id,  # Spouse's mother is the main person's mother
            "father": father_id,  # Spouse's father is the main person's father
            "noparents": True,
            "display_name": "همسر"
        }
        pedigree_data.append(spouse_data)

        # Generate sons - CORRECTED: no famid, proper parent references
        for i in range(sons_count):
            son_age = max(1, main_age - 25 - random.randint(0, 5))
            son_data = {
                "famid": "FAM1",
                "name": generate_random_id(),
                "sex": "M",
                "status": "0",
                "display_name": f"پسر {i + 1}"
            }

            # Set parents: father is spouse, mother is main person (or vice versa)
            if main_gender == 'M':
                son_data["father"] = main_person_id
                son_data["mother"] = spouse_id
            else:
                son_data["father"] = spouse_id
                son_data["mother"] = main_person_id

            pedigree_data.append(son_data)

        # Generate daughters - CORRECTED: no famid, proper parent references
        for i in range(daughters_count):
            daughter_age = max(1, main_age - 25 - random.randint(0, 5))
            daughter_data = {
                "famid": "FAM1",
                "name": generate_random_id(),
                "sex": "F",
                "status": "0",
                "display_name": f"دختر {i + 1}"
            }

            # Set parents: father is spouse, mother is main person (or vice versa)
            if main_gender == 'M':
                daughter_data["father"] = main_person_id
                daughter_data["mother"] = spouse_id
            else:
                daughter_data["father"] = spouse_id
                daughter_data["mother"] = main_person_id

            pedigree_data.append(daughter_data)

    # 6. Generate other relatives (uncles, aunts, etc.)
    pedigree_data = generate_other_relatives(pedigree_data, form_data, father_id, mother_id, main_age)

    return pedigree_data


def generate_other_relatives(pedigree_data, form_data, father_id, mother_id, main_age):
    """Generate uncles, aunts, and other relatives"""

    # Father's brothers (uncles from father side)
    uncles_father_count = int(form_data.get('uncles_father', 0))
    for i in range(uncles_father_count):
        uncle_age = max(1, main_age + 25 - random.randint(0, 10))
        uncle_data = {
            "famid": "FAM1",
            "name": generate_random_id(),
            "sex": "M",
            "status": "0",
            "display_name": f"عمو {i + 1}"
        }
        # Find father's parents to set as this uncle's parents
        father_data = next((item for item in pedigree_data if item.get('name') == father_id), None)
        if father_data and 'father' in father_data and 'mother' in father_data:
            uncle_data["father"] = father_data['father']
            uncle_data["mother"] = father_data['mother']
        pedigree_data.append(uncle_data)

    # Father's sisters (aunts from father side)
    aunts_father_count = int(form_data.get('aunts_father', 0))
    for i in range(aunts_father_count):
        aunt_age = max(1, main_age + 25 - random.randint(0, 10))
        aunt_data = {
            "famid": "FAM1",
            "name": generate_random_id(),
            "sex": "F",
            "status": "0",
            "display_name": f"عمه {i + 1}"
        }
        # Find father's parents to set as this aunt's parents
        father_data = next((item for item in pedigree_data if item.get('name') == father_id), None)
        if father_data and 'father' in father_data and 'mother' in father_data:
            aunt_data["father"] = father_data['father']
            aunt_data["mother"] = father_data['mother']
        pedigree_data.append(aunt_data)

    # Mother's brothers (uncles from mother side)
    uncles_mother_count = int(form_data.get('uncles_mother', 0))
    for i in range(uncles_mother_count):
        uncle_age = max(1, main_age + 25 - random.randint(0, 10))
        uncle_data = {
            "famid": "FAM1",
            "name": generate_random_id(),
            "sex": "M",
            "status": "0",
            "display_name": f"دایی {i + 1}"
        }
        # Find mother's parents to set as this uncle's parents
        mother_data = next((item for item in pedigree_data if item.get('name') == mother_id), None)
        if mother_data and 'father' in mother_data and 'mother' in mother_data:
            uncle_data["father"] = mother_data['father']
            uncle_data["mother"] = mother_data['mother']
        pedigree_data.append(uncle_data)

    # Mother's sisters (aunts from mother side)
    aunts_mother_count = int(form_data.get('aunts_mother', 0))
    for i in range(aunts_mother_count):
        aunt_age = max(1, main_age + 25 - random.randint(0, 10))
        aunt_data = {
            "famid": "FAM1",
            "name": generate_random_id(),
            "sex": "F",
            "status": "0",
            "display_name": f"خاله {i + 1}"
        }
        # Find mother's parents to set as this aunt's parents
        mother_data = next((item for item in pedigree_data if item.get('name') == mother_id), None)
        if mother_data and 'father' in mother_data and 'mother' in mother_data:
            aunt_data["father"] = mother_data['father']
            aunt_data["mother"] = mother_data['mother']
        pedigree_data.append(aunt_data)

    return pedigree_data


def load_pedigree(request):
    """Load pedigree data by code"""
    code = request.GET.get('code', '').strip()

    if not code:
        return JsonResponse({'success': False, 'message': 'کد الزامی است'})

    try:
        pedigree = Pedigree.objects.get(code=code)
        return JsonResponse({
            'success': True,
            'pedigree_data': pedigree.pedigree_data,
            'famid': pedigree.famid
        })
    except Pedigree.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'شجره یافت نشد'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'خطا در بارگذاری: {str(e)}'})


def pedigreejs_tree_fa(request):
    """PedigreeJS view that accepts code parameter"""
    code = request.GET.get('code', '')
    try:
        if code:
            pedigree = Pedigree.objects.get(code=code)
            risk_data = pedigree.risk_data if pedigree.risk_data else {}
        else:
            risk_data = {}

        return render(request, 'pedigreejs/pedigreejs_tree_fa.html', {
            'code': code,
            'risk_data_json': json.dumps(risk_data) if risk_data else '{}'
        })
    except Pedigree.DoesNotExist:
        return render(request, 'pedigreejs/pedigreejs_tree_fa.html', {
            'code': code,
            'risk_data_json': '{}'
        })


def pedigreejs_tree_save1(request):
    """Save pedigree data from PedigreeJS editor"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            code = data.get('code', '').strip()
            pedigree_data = data.get('pedigree_data', [])

            if not code:
                return JsonResponse({'success': False, 'message': 'کد الزامی است'})

            pedigree, created = Pedigree.objects.update_or_create(
                code=code,
                defaults={
                    'famid': 'FAM1',
                    'pedigree_data': pedigree_data
                }
            )

            return JsonResponse({
                'success': True,
                'message': f'شجره با موفقیت {"ذخیره" if created else "به روز"} شد',
                'code': code
            })

        except Exception as e:
            return JsonResponse({'success': False, 'message': f'خطا در ذخیره سازی: {str(e)}'})

    return JsonResponse({'success': False, 'message': 'درخواست نامعتبر'})


def pedigreejs_tree_save(request):
    if request.method == 'POST':
        code = request.POST.get('code')
        famid = request.POST.get('famid', 'FAM1')
        pedigree_data = request.POST.get('pedigree_data')

        if code and pedigree_data:
            try:
                data = json.loads(pedigree_data)

                pedigree, created = Pedigree.objects.update_or_create(
                    code=code,
                    defaults={
                        'famid': famid,
                        'pedigree_data': data
                    }
                )

                return JsonResponse({
                    'success': True,
                    'message': 'Pedigree saved successfully!',
                    'created': created
                })
            except json.JSONDecodeError:
                return JsonResponse({
                    'success': False,
                    'message': 'Invalid JSON data'
                })
            except Exception as e:
                return JsonResponse({
                    'success': False,
                    'message': str(e)
                })

    return JsonResponse({
        'success': False,
        'message': 'Invalid request'
    })


def pedigreejs_tree_load(request):
    """Load pedigree data for PedigreeJS editor"""
    code = request.GET.get('code', '').strip()

    if not code:
        return JsonResponse({'success': False, 'message': 'کد الزامی است'})

    try:
        pedigree = Pedigree.objects.get(code=code)
        return JsonResponse({
            'success': True,
            'pedigree_data': pedigree.pedigree_data,
            'famid': pedigree.famid,
            'risk_data': pedigree.risk_data if pedigree.risk_data else {}
        })
    except Pedigree.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'شجره یافت نشد'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'خطا در بارگذاری: {str(e)}'})


def get_risk_data(request):
    """API endpoint to get risk data for a pedigree"""
    code = request.GET.get('code', '')

    if not code:
        return JsonResponse({'success': False, 'message': 'Code is required'})

    try:
        pedigree = Pedigree.objects.get(code=code)

        if not pedigree.risk_data:
            return JsonResponse({'success': False, 'message': 'No risk data available'})

        return JsonResponse({
            'success': True,
            'risk_data': pedigree.risk_data
        })

    except Pedigree.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Pedigree not found'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})


def display_cancer_risk(request, code):
    """Display cancer risk analysis for a pedigree"""
    try:
        pedigree = Pedigree.objects.get(code=code)

        if not pedigree.risk_data:
            return render(request, 'pedigreejs/risk_analysis.html', {
                'code': code,
                'error': 'No risk data available for this pedigree'
            })

        risk_data = pedigree.risk_data

        # Prepare context with formatted data
        context = {
            'code': code,
            'risk_data': risk_data,
            'has_breast_cancer_data': 'breast_cancer' in risk_data,
            'has_colorectal_cancer_data': 'colorectal_cancer' in risk_data,
        }

        return render(request, 'pedigreejs/risk_analysis.html', context)

    except Pedigree.DoesNotExist:
        return render(request, 'pedigreejs/risk_analysis.html', {
            'error': 'Pedigree not found'
        })