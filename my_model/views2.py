from django.http import JsonResponse,HttpResponse
import requests
import json

from django.shortcuts import render
from .models import MyModel
from .utils.diabetes import *
from .utils.breast_cancer import *
from .utils.crc import *
from .utils.pbcg import *
from .utils.ascvd import *
from .utils.cervical import *

from .utils.melanoma_cancer import *
from .utils.osteoporosis import *
from .utils.ovarian_cancer import *
from .utils.pancreatic_cancer import *
from .utils.stomach_cancer import *
from .utils.stroke import *



from .utils.importer import *
import math
from django.conf import settings


def screening_list_fa(request):
    assessments = [
        {
            "id": 1,
            "title": "Breast_Cancer",
            "title_fa": "ارزیابی ریسک سرطان سینه",
            "desc": "Breast Cancer Risk Assessment",
            "desc_fa": "ارزیابی ریسک سرطان سینه",
            "image": "heart_screening.jpg",
            "groups": ['Female'],
            "active": 1
        },
        {
            "id": 2,
            "title": "Colorectal_Cancer",
            "title_fa": "ارزیابی ریسک سرطان کلورکتال",
            "desc": "Colorectal Cancer Risk Assessment",
            "desc_fa": "ارزیابی ریسک سرطان کلورکتال",
            "image": "heart_screening.jpg",
            "groups": ['Male', 'Female'],
            "active": 0
        },
        {
            "id": 3,
            "title": "Prostate_Cancer",
            "title_fa": "ارزیابی ریسک سرطان پروستات",
            "desc": "Prostate Cancer Risk Assessment",
            "desc_fa": "ارزیابی ریسک سرطان پروستات",
            "image": "heart_screening.jpg",
            "groups": ['Male'],
            "active": 1
        },
        {
            "id": 4,
            "title": "Cervical_Cancer",
            "title_fa": "ارزیابی ریسک سرطان دهانه رحم",
            "desc": "Cervical Cancer Risk Assessment",
            "desc_fa": "ارزیابی ریسک سرطان دهانه رحم",
            "image": "heart_screening.jpg",
            "groups": ['Female'],
            "active": 1
        },
        {
            "id": 5,
            "title": "Diabetes",
            "title_fa": "ارزیابی ریسک دیابت",
            "desc": "Diabetes Risk Assessment",
            "desc_fa": "ارزیابی ریسک دیابت",
            "image": "heart_screening.jpg",
            "groups": ['Male', 'Female'],
            "active": 1
        },
        {
            "id": 6,
            "title": "Cardiovascular_Disease",
            "title_fa": "ارزیابی ریسک قلبی-عروقی",
            "desc": "Cardiovascular Disease Risk Assessment",
            "desc_fa": "ارزیابی ریسک قلبی-عروقی",
            "image": "heart_screening.jpg",
            "groups": ['Male', 'Female'],
            "active": 1
        },
        {
            "id": 7,
            "title": "Melanoma_Cancer",
            "title_fa": "ارزیابی ریسک سرطان پوست",
            "desc": "Melanoma Cancer Risk Assessment",
            "desc_fa": "ارزیابی ریسک سرطان پوست",
            "image": "heart_screening.jpg",
            "groups": ['Male', 'Female'],
            "active": 1
        },
        {
            "id": 8,
            "title": "Osteoporosis",
            "title_fa": "ارزیابی ریسک پوکی استخوان",
            "desc": "Osteoporosis Risk Assessment",
            "desc_fa": "ارزیابی ریسک پوکی استخوان",
            "image": "heart_screening.jpg",
            "groups": ['Male', 'Female'],
            "active": 1
        },
        {
            "id": 9,
            "title": "Ovarian_Cancer",
            "title_fa": "ارزیابی ریسک سرطان تخمدان",
            "desc": "Ovarian Cancer Risk Assessment",
            "desc_fa": "ارزیابی ریسک سرطان تخمدان",
            "image": "heart_screening.jpg",
            "groups": ['Female'],
            "active": 1
        },
        {
            "id": 10,
            "title": "Stomach_Cancer",
            "title_fa": "ارزیابی ریسک سرطان معده",
            "desc": "Stomach Cancer Risk Assessment",
            "desc_fa": "ارزیابی ریسک سرطان معده",
            "image": "heart_screening.jpg",
            "groups": ['Male', 'Female'],
            "active": 1
        },
        {
            "id": 11,
            "title": "Stroke",
            "title_fa": "ارزیابی ریسک سکته مغزی",
            "desc": "Stroke Risk Assessment",
            "desc_fa": "ارزیابی ریسک سکته مغزی",
            "image": "heart_screening.jpg",
            "groups": ['Male', 'Female'],
            "active": 1
        },
        {
            "id": 12,
            "title": "Stroke",
            "title_fa": "ارزیابی ریسک سرطان پانکراس",
            "desc": "Stroke Risk Assessment",
            "desc_fa": "ارزیابی ریسک سرطان پانکراس",
            "image": "heart_screening.jpg",
            "groups": ['Male', 'Female'],
            "active": 1
        },
    ]
    return render(request, 'screening_list_fa.html', {'assessments' : assessments})


def dashboard_fa(request):

    return render(request, 'dashboard_fa.html', {})


def dashboard_detail_fa(request):

    param = 'دیابت'
    res_related_contents = requests.get(f'{settings.SMARTLIFE_BASE_URL}/filter_content_list?q={param}')
    if res_related_contents.content:
        related_contents = res_related_contents.json()

    speciality = 1
    res_related_doctors = requests.get(f'{settings.SMARTLIFE_BASE_URL}/doctor/filter_doctor_list?q={speciality}')
    if res_related_doctors.content:
        related_doctors = res_related_doctors.json()

    context = {}
    context['related_contents'] = related_contents
    context['related_doctors'] = related_doctors
    return render(request, 'dashboard_detail_fa.html', context)



def question_fa(request):
    if request.method == 'POST':
        assessments_string = request.POST.getlist('selected_assessments')
        selected_assessments = []
        for a in assessments_string:
            try:
                selected_assessments.append(json.loads(a.replace("'", '"')))
            except json.JSONDecodeError:
                continue  # Skip invalid entries

        request.session['selected_assessments'] = selected_assessments
        return render(request, 'my_model_fa.html', {'selected_assessments': selected_assessments})

    return redirect('some_other_view')  # Handle GET requests if needed


###############################################
# calculate_my_model
###############################################
def calculate_my_model(request):

    selected_assessments = request.session.get('selected_assessments', [])
### Demographic Info
    #code = request.POST.get('code')
    #gender = request.POST.get('gender')
    code = 1000
    gender = 'Male'
    age = float(request.POST.get('age'))
    weight = float(request.POST.get('weight'))
    height = float(request.POST.get('height'))
    ethnicity = int(request.POST.get('ethnicity'))
    born_place = request.POST.get('born_place')
    education = float(request.POST.get('education'))

### Life Style
    activity = float(request.POST.get('activity'))
    smoking = float(request.POST.get('smoking'))
    alcohol = float(request.POST.get('alcohol'))

### Diabetes
    waist_size = float(request.POST.get('waist_size'))
    vegetables = request.POST.get('vegetables')
    blood_pressure = request.POST.get('blood_pressure')
    blood_glucose = request.POST.get('blood_glucose')
    relatives_diabetes = request.POST.get('relatives_diabetes')

    diabetes_results = Diabetes.calculate_risk(
                    gender,
                    age,
                    weight,
                    height,
                    waist_size,
                    activity,
                    vegetables,
                    blood_pressure,
                    blood_glucose,
                    relatives_diabetes,
                    ethnicity,
                    born_place,
                    smoking
                  )

    ausdrisk_score = diabetes_results['ausdrisk_score']
    idf_score = diabetes_results['idf_score']
    uk_score = diabetes_results['uk_score']
    ada_score = diabetes_results['ada_score']
    ausdrisk_status = diabetes_results['ausdrisk_status']
    idf_status = diabetes_results['idf_status']
    uk_status = diabetes_results['uk_status']
    ada_status = diabetes_results['ada_status']

### Breaset Cancer
    gail_score_abs_5 = 0
    gail_score_ave_5 = 0
    gail_score_abs_90 = 0
    gail_score_ave_90 = 0
    mymodel_gail_score = 0
    breast_cancer_results = {}
    if gender == 'Female':
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


### CRC Cancer
    premm_score = 0
    family_crc = request.POST.get('family_crc')
    multivitamin = request.POST.get('multivitamin')
    meat = float(request.POST.get('meat'))
    diabetes = request.POST.get('diabetes')
    # male
    aspirin = request.POST.get('aspirin')
    # female
    estrogen = request.POST.get('estrogen')
    painmed = request.POST.get('painmed')

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


### Prostat Cancer (PBCG)
    pbcg_score_no_cancer = 0
    pbcg_score_low_cancer = 0
    pbcg_score_high_cancer = 0
    pbcg_results = {}
    if gender == 'Male':
        psa = float(request.POST.get('psa'))
        famhistory = request.POST.get('famhistory')
        dre = request.POST.get('dre')
        priorbiopsy = request.POST.get('priorbiopsy')

        famhistory_value = 0
        dre_value = 0
        priorbiopsy_value = 0

        if famhistory == 'Yes':
            famhistory_value = 1
        else:
            famhistory_value = 0

        if dre == 'Abnormal':
            dre_value = 1
        else:
            dre_value = 0

        if priorbiopsy == 'Prior negative biopsy':
            priorbiopsy_value = 1
        else:
            priorbiopsy_value = 0

        pbcg_results = ProstateRiskCalculator.calculate_risk(psa,
                                                           age,
                                                           int(ethnicity),
                                                           priorbiopsy_value,
                                                           dre_value,
                                                           famhistory_value
                                                           )

        pbcg_score_no_cancer = pbcg_results['pbcg_score_no_cancer']
        pbcg_score_low_cancer = pbcg_results['pbcg_score_low_cancer']
        pbcg_score_high_cancer = pbcg_results['pbcg_score_high_cancer']

    ### Cardiovascular (ASCVD)
    sbp = float(request.POST.get('sbp'))
    hdl = float(request.POST.get('hdl'))
    totchol = float(request.POST.get('totchol'))
    ascvd_status = ''

    ascvd_score = ASCVD_RiskCalculator.ascvd_10y_accaha(ethnicity,
                                                        gender,
                                                        age,
                                                        totchol,
                                                        hdl,
                                                        sbp,
                                                        blood_pressure,
                                                        smoking,
                                                        blood_glucose)
    if ascvd_score is None:
        ascvd_score = 0
        ascvd_status = "Not supported"
    elif ascvd_score < 5:
        ascvd_status = "Low risk"
    elif (ascvd_score >= 5) and (ascvd_score <= 7.4):
        ascvd_status = "Borderline risk"
    elif (ascvd_score >= 7.5) and (ascvd_score < 19.9):
        ascvd_status = "Intermediate risk"
    elif ascvd_score >= 20:
        ascvd_status = "High risk"


    ### my_cervical
    cervical_cancer_score = 1
    if gender == 'Female':
        num_sexual_partners = float(request.POST.get('num_sexual_partners'))
        first_sexual_intercourse = float(request.POST.get('first_sexual_intercourse'))
        num_pregnancies = float(request.POST.get('num_pregnancies'))
        smoking = float(request.POST.get('smoking'))
        hormonal_contraceptives_years = float(request.POST.get('hormonal_contraceptives_years'))
        iud = float(request.POST.get('iud'))
        std = request.POST.get('std')
        cervical_cancer = request.POST.get('cervical_cancer')
        cytology = float(request.POST.get('cytology'))
        cin = float(request.POST.get('cin'))
        hpv = float(request.POST.get('hpv'))

        cervical_cancer_score = Cervical_RiskCalculator.calculate_risk(num_sexual_partners,
                                                                        first_sexual_intercourse,
                                                                        num_pregnancies,
                                                                        smoking,
                                                                        hormonal_contraceptives_years,
                                                                        iud,
                                                                        std,
                                                                        cervical_cancer,
                                                                        cytology,
                                                                        cin,
                                                                        hpv)

        cervical_cancer_grades = {
            1: 'Low risk (Follow up based on your health care provider and national guidline, e.g., USPSTF (174), ACS (177), and ACOG (175))',
            2: 'Follow up by health care provider and likely ask you to come back for additional testing to make sure that there are not more serious (high-grade) changes.)',
            3: 'High risk (Follow up by gynaecologist are needed. Your health care provider will recommend follow-up steps you need to take)',
        }
        cervical_cancer_grade = cervical_cancer_grades.get(cervical_cancer_score)

        ###  Melanoma Cancer
        melanoma_cancer_score = 0
        family_melanoma_cancer = request.POST.get('family_melanoma_cancer')
        colored_hair = request.POST.get('colored_hair')
        colored_eyes = request.POST.get('colored_eyes')
        fair_skin = request.POST.get('fair_skin')
        moles_count = float(request.POST.get('moles_count'))
        sunburns = request.POST.get('sunburns')
        sunlamp = request.POST.get('sunlamp')
        immunosuppressive_drugs = request.POST.get('immunosuppressive_drugs')

        melanoma_cancer_score = Melanoma_RiskCalculator.calculate_risk(previous_cancer,
                                                                        family_melanoma_cancer,
                                                                        colored_hair,
                                                                        colored_eyes,
                                                                        fair_skin,
                                                                        moles_count,
                                                                        sunburns,
                                                                        sunlamp,
                                                                        immunosuppressive_drugs)


        ###  Osteoporosis Cancer
        osteoporosis_score = 0
        rheumatoid_arthritis = request.POST.get('rheumatoid_arthritis')
        have_bmd_test = request.POST.get('have_bmd_test')
        result_bmd_test = request.POST.get('result_bmd_test')
        chemotherapy = request.POST.get('chemotherapy')
        steroid = request.POST.get('steroid')
        anticonvulsants = request.POST.get('anticonvulsants')
        dairy = float(request.POST.get('dairy'))
        calcium_supplements = request.POST.get('calcium_supplements')
        vitamin_d = request.POST.get('vitamin_d')
        family_break_bone = request.POST.get('family_break_bone')

        osteoporosis_score = Osteoporosis_RiskCalculator.calculate_risk(rheumatoid_arthritis,
                                                                        have_bmd_test,
                                                                        result_bmd_test,
                                                                        blood_glucose,
                                                                        chemotherapy,
                                                                        steroid,
                                                                        anticonvulsants,
                                                                        multivitamin,
                                                                        cereal,
                                                                        vegetables,
                                                                        dairy,
                                                                        calcium_supplements,
                                                                        vitamin_d,
                                                                        alcohol,
                                                                        smoking,
                                                                        activity,
                                                                        family_break_bone)

        ###############################################
    if gender == 'Male':
        print(gender)
        MyModel.objects.create(userid=request.user,
                               code=code,
                               gender=gender,
                               age=age,
                               weight=weight,
                               height=height,
                               ethnicity=ethnicity,
                               born_place=born_place,
                               education=education,

                               # LifeStyle
                               activity=activity,
                               smoking=smoking,
                               alcohol=alcohol,
                               meat=meat,

                               # Diabetes
                               waist_size=waist_size,
                               vegetables=vegetables,
                               blood_pressure=blood_pressure,
                               blood_glucose=blood_glucose,
                               relatives_diabetes=relatives_diabetes,
                               ausdrisk_score=ausdrisk_score,
                               idf_score=idf_score,
                               uk_score=uk_score,
                               ada_score=ada_score,
                               ausdrisk_status=ausdrisk_status,
                               idf_status=idf_status,
                               uk_status=uk_status,
                               ada_status=ada_status,

                               # Breast Cancer

                               # CRC
                               family_crc=family_crc,
                               multivitamin=multivitamin,
                               diabetes=diabetes,
                               aspirin=aspirin,
                               estrogen=estrogen,
                               painmed=painmed,
                               crcpro_score=crcpro_score,

                               crc_history=crc_history,
                               crc2_history=crc2_history,
                               ec_history=ec_history,
                               ls_history=ls_history,
                               crc_fdr=crc_fdr,
                               crc_sdr=crc_sdr,
                               ec_fdr=ec_fdr,
                               ec_sdr=ec_sdr,
                               ls_fdr=ls_fdr,
                               ls_sdr=ls_sdr,
                               min_age_crc=min_age_crc,
                               min_age_crc_fdr=min_age_crc_fdr,
                               min_age_crc_sdr=min_age_crc_sdr,
                               min_age_ec=min_age_ec,
                               min_age_ec_fdr=min_age_ec_fdr,
                               min_age_ec_sdr=min_age_ec_sdr,
                               premm_score=premm_score,

                               # Prostate (PBCG)
                               psa=psa,
                               famhistory=famhistory,
                               dre=dre,
                               priorbiopsy=priorbiopsy,
                               pbcg_score_no_cancer=pbcg_score_no_cancer,
                               pbcg_score_low_cancer=pbcg_score_low_cancer,
                               pbcg_score_high_cancer=pbcg_score_high_cancer,

                               # Cardiovascular (ASCVD)
                               sbp=sbp,
                               hdl=hdl,
                               totchol=totchol,
                               ascvd_score=ascvd_score,
                               ascvd_status=ascvd_status)

    elif gender == 'Female':
            MyModel.objects.create(userid=request.user,
                                   code=code,
                                   gender=gender,
                                   age=age,
                                   weight=weight,
                                   height=height,
                                   ethnicity=ethnicity,
                                   born_place=born_place,
                                   education=education,

                                   # LifeStyle
                                   activity=activity,
                                   smoking=smoking,
                                   alcohol=alcohol,
                                   meat=meat,

                                   # Diabetes
                                   waist_size=waist_size,
                                   vegetables=vegetables,
                                   blood_pressure=blood_pressure,
                                   blood_glucose=blood_glucose,
                                   relatives_diabetes=relatives_diabetes,
                                   ausdrisk_score=ausdrisk_score,
                                   idf_score=idf_score,
                                   uk_score=uk_score,
                                   ada_score=ada_score,
                                   ausdrisk_status=ausdrisk_status,
                                   idf_status=idf_status,
                                   uk_status=uk_status,
                                   ada_status=ada_status,

                                   # Breast Cancer
                                   biopsy=biopsy,
                                   biopsy_num=biopsy_num,
                                   hyperplasia_biopsy=hyperplasia_biopsy,
                                   menstruation_age=menstruation_age,
                                   child_age=child_age,
                                   fdr_cancer=fdr_cancer,
                                   breastfeeding=breastfeeding,
                                   cbe=cbe,
                                   bse=bse,
                                   mammograms=mammograms,
                                   syndrome=syndrome,
                                   gene_mutation=gene_mutation,
                                   gene_mutation_fdr=gene_mutation_fdr,
                                   gail_score_abs_5=gail_score_abs_5,
                                   gail_score_ave_5=gail_score_ave_5,
                                   gail_score_abs_90=gail_score_abs_90,
                                   gail_score_ave_90=gail_score_ave_90,
                                   mymodel_gail_score=mymodel_gail_score,

                                   # CRC
                                   family_crc=family_crc,
                                   multivitamin=multivitamin,
                                   diabetes=diabetes,
                                   aspirin=aspirin,
                                   estrogen=estrogen,
                                   painmed=painmed,
                                   crcpro_score=crcpro_score,

                                   crc_history=crc_history,
                                   crc2_history=crc2_history,
                                   ec_history=ec_history,
                                   ls_history=ls_history,
                                   crc_fdr=crc_fdr,
                                   crc_sdr=crc_sdr,
                                   ec_fdr=ec_fdr,
                                   ec_sdr=ec_sdr,
                                   ls_fdr=ls_fdr,
                                   ls_sdr=ls_sdr,
                                   min_age_crc=min_age_crc,
                                   min_age_crc_fdr=min_age_crc_fdr,
                                   min_age_crc_sdr=min_age_crc_sdr,
                                   min_age_ec=min_age_ec,
                                   min_age_ec_fdr=min_age_ec_fdr,
                                   min_age_ec_sdr=min_age_ec_sdr,
                                   premm_score=premm_score,

                                   # Prostate (PBCG)

                                   # Cardiovascular (ASCVD)
                                   sbp=sbp,
                                   hdl=hdl,
                                   totchol=totchol,
                                   ascvd_score=ascvd_score,
                                   ascvd_status=ascvd_status,

                                   # my_cervical
                                   num_sexual_partners=num_sexual_partners,
                                   first_sexual_intercourse=first_sexual_intercourse,
                                   num_pregnancies=num_pregnancies,
                                   hormonal_contraceptives_years=hormonal_contraceptives_years,
                                   iud=iud,
                                   std=std,
                                   cervical_cancer=cervical_cancer,
                                   cytology=cytology,
                                   cin=cin,
                                   hpv=hpv,
                                   cervical_cancer_score=cervical_cancer_score,
                                   cervical_cancer_grade=cervical_cancer_grade
                                   )

    context = {}

    # Class				Color
    # bg-primary		Blue
    # bg-success		Green
    # bg-danger			Red
    # bg-warning		Yellow/Orange
    # bg-info			LightBlue
    # bg-secondary		Gray



    for item in selected_assessments:
        if item['title'] == 'Diabetes':
            if 0 <= idf_score <= 6:
                item['score'] = idf_score
                item['status'] = 'Low Risk'
                item['status_fa'] = 'ریسک کم'
                item['color_class'] = 'bg-success'
                item['recommendation'] = 'Maintain healthy lifestyle: Balanced diet and 150 mins/week moderate exercise.'
                item['recommendation_fa'] = 'سبک زندگی سالم: رژیم متعادل و ۱۵۰ دقیقه ورزش متوسط در هفته.'

            elif 7 <= idf_score <= 11:
                item['score'] = idf_score
                item['status'] = 'Slightly Increased Risk'
                item['status_fa'] = 'ریسک تقریبا کم'
                item['color_class'] = 'bg-info'
                item['recommendation'] = 'Lifestyle modification + annual glucose check. Consider HbA1c testing.'
                item['recommendation_fa'] = 'اصلاح سبک زندگی + آزمایش سالانه قند خون. تست HbA1c توصیه می‌شود.'

            elif 12 <= idf_score <= 14:
                item['score'] = idf_score
                item['status'] = 'Average Risk'
                item['status_fa'] = 'ریسک متوسط'
                item['color_class'] = 'bg-warning'
                item['recommendation'] = 'Medical consultation required. Monitor fasting glucose every 6 months.'
                item['recommendation_fa'] = 'مشاوره پزشکی ضروری است. کنترل قند ناشتا هر ۶ ماه.'

            elif 15 <= idf_score <= 20:
                item['score'] = idf_score
                item['status'] = 'High Risk'
                item['status_fa'] = 'ریسک زیاد'
                item['color_class'] = 'bg-danger'
                item['recommendation'] = 'Urgent intervention: OGTT test + potential metformin therapy.'
                item['recommendation_fa'] = 'اقدام فوری: تست تحمل گلوکز (OGTT) + احتمال شروع متفورمین.'

            elif idf_score > 20:
                item['score'] = idf_score
                item['status'] = 'Very High Risk'
                item['status_fa'] = 'ریسک خیلی زیاد'
                item['color_class'] = 'bg-danger'
                item['recommendation'] = 'Immediate endocrinology referral. Start pharmacological prevention.'
                item['recommendation_fa'] = 'مراجعه فوری به متخصص غدد. شروع پیشگیری دارویی.'

        if item['title'] == 'Cardiovascular_Disease':
            if ascvd_score is None:
                item['score'] = ascvd_score # 0
                item['status'] = 'Not supported'
                item['status_fa'] = 'بازه سنی پشتیبانی نمی شود'
                item['color_class'] = 'bg-primary'
                item['recommendation'] = 'Age outside 40-79 range'
                item['recommendation_fa'] = 'محدوده سنی نامعتبر (۴۰-۷۹ سال)'
            elif ascvd_score < 5:
                item['score'] = ascvd_score
                item['status'] = 'Low risk'
                item['status_fa'] = 'ریسک کم'
                item['color_class'] = 'bg-success'
                item['recommendation'] = 'Lifestyle prevention'
                item['recommendation_fa'] = 'پیشگیری با سبک زندگی سالم'
            elif (ascvd_score >= 5) and (ascvd_score <= 7.4):
                item['score'] = ascvd_score
                item['status'] = 'Borderline risk'
                item['status_fa'] = 'ریسک کم-متوسط'
                item['color_class'] = 'bg-info'
                item['recommendation'] = 'LDL management + lifestyle'
                item['recommendation_fa'] = 'کنترل LDL + تغییر سبک زندگی'
            elif (ascvd_score >= 7.5) and (ascvd_score < 19.9):
                item['score'] = ascvd_score
                item['status'] = 'Intermediate risk'
                item['status_fa'] = 'ریسک متوسط'
                item['color_class'] = 'bg-warning'
                item['recommendation'] = 'Moderate statins + risk factor control'
                item['recommendation_fa'] = 'استاتین متوسط + کنترل فاکتورهای خطر'
            elif ascvd_score >= 20:
                item['score'] = ascvd_score
                item['status'] = 'High risk'
                item['status_fa'] = 'ریسک زیاد'
                item['color_class'] = 'bg-danger'
                item['recommendation'] = 'Aggressive lipid-lowering therapy'
                item['recommendation_fa'] = 'درمان تهاجمی کاهش چربی خون'

        if item['title'] == 'Breast_Cancer':
            if gail_score_abs_5 >= 5.0 or gail_score_abs_90 >= 30:
                item['score'] = mymodel_gail_score
                item['status'] = 'High Risk'
                item['status_fa'] = 'ریسک زیاد'
                item['color_class'] = 'bg-danger'
                item['recommendation'] = 'Medical advice, medicine'
                item['recommendation_fa'] = 'مشاوره پزشکی، پیشگیری دارویی'
            elif gail_score_abs_5 >= 3.0 or gail_score_abs_90 >= 25:
                item['score'] = mymodel_gail_score
                item['status'] = 'Intermediate Risk'
                item['status_fa'] = 'ریسک متوسط-بالا'
                item['color_class'] = 'bg-warning'
                item['recommendation'] = 'May need additional tests (e.g., MRI)'
                item['recommendation_fa'] = 'بررسی‌های تکمیلی (MRI)'
            elif gail_score_abs_5 >= 1.67 or gail_score_abs_90 >= 20:
                item['score'] = mymodel_gail_score
                item['status'] = 'Average Risk'
                item['status_fa'] = 'ریسک متوسط'
                item['color_class'] = 'bg-info'
                item['recommendation'] = 'Follow standard mammogram'
                item['recommendation_fa'] = 'پیگیری منظم ماموگرافی'
            else:
                item['score'] = mymodel_gail_score
                item['status'] = 'Low Risk'
                item['status_fa'] = 'ریسک کم'
                item['color_class'] = 'bg-success'
                item['recommendation'] = 'Routine screening'
                item['recommendation_fa'] = 'غربالگری معمول'

        if item['title'] == 'Colorectal_Cancer':
            if premm_score >= 25:
                item['score'] = premm_score
                item['status'] = 'High Risk'
                item['status_fa'] = 'ریسک زیاد'
                item['color_class'] = 'bg-danger'
                item['recommendation'] = 'Annual colonoscopy + Consider prophylactic colectomy if mutations are confirmed.'
                item['recommendation_fa'] = 'کولونوسکوپی سالانه + جراحی پیشگیرانه (کولکتومی) در صورت تایید جهش ها'
            elif premm_score >= 10:
                item['score'] = premm_score
                item['status'] = 'Intermediate Risk'
                item['status_fa'] = 'ریسک متوسط-بالا'
                item['color_class'] = 'bg-warning'
                item['recommendation'] = 'Genetic testing for Lynch Syndrome + colonoscopy every 1-2 years.'
                item['recommendation_fa'] = 'آزمایش ژنتیک برای بررسی جهش‌های سندرم لینچ + کولونوسکوپی هر ۱-۲ سال.'
            elif premm_score >= 2.5:
                item['score'] = premm_score
                item['status'] = 'Moderate Risk'
                item['status_fa'] = 'ریسک متوسط'
                item['color_class'] = 'bg-info'
                item['recommendation'] = 'Begin screening earlier (e.g., age 45) and repeat every 5 years.'
                item['recommendation_fa'] = 'شروع کولونوسکوپی در سن پایین‌تر (مثلاً ۴۵ سالگی) و تکرار هر ۵ سال.'
            else:
                item['score'] = premm_score
                item['status'] = 'Low Risk'
                item['status_fa'] = 'ریسک کم'
                item['color_class'] = 'bg-success'
                item['recommendation'] = 'Follow average-risk guidelines (colonoscopy every 10 years starting at age 50).'
                item['recommendation_fa'] = 'کولونوسکوپی هر ۱۰ سال از سن ۵۰ سالگی (طبق دستورالعمل‌های معمول).'

        if item['title'] == 'Cervical_Cancer':
            if cervical_cancer_score  == 3:
                item['score'] = cervical_cancer_score
                item['status'] = 'High Risk'
                item['status_fa'] = 'ریسک زیاد'
                item['color_class'] = 'bg-danger'
                item['recommendation'] = 'Immediate colposcopy and possible biopsy required'
                item['recommendation_fa'] = 'کولپوسکوپی فوری و احتمالاً بیوپسی ضروری است'
            elif cervical_cancer_score  == 2:
                item['score'] = cervical_cancer_score
                item['status'] = 'Intermediate Risk'
                item['status_fa'] = 'ریسک متوسط-بالا'
                item['color_class'] = 'bg-warning'
                item['recommendation'] = 'Repeat testing in 6-12 months or colposcopy referral'
                item['recommendation_fa'] = 'تکرار تست در ۶-۱۲ ماه یا ارجاع به کولپوسکوپی'
            elif cervical_cancer_score == 1:
                item['score'] = cervical_cancer_score
                item['status'] = 'Low Risk'
                item['status_fa'] = 'ریسک کم'
                item['color_class'] = 'bg-success'
                item['recommendation'] = 'Follow routine screening per national guidelines (e.g., Pap every 3-5 years)'
                item['recommendation_fa'] = 'پیگیری غربالگری معمول (مطابق دستورالعمل ملی، مثلاً پاپ اسمیر هر ۳-۵ سال)'

        if item['title'] == 'Prostate_Cancer':
            if pbcg_score_high_cancer >= 0.10:
                item['score'] = pbcg_score_high_cancer
                item['status'] = 'High risk (PBCG)'
                item['status_fa'] = 'ریسک بالا (PBCG)'
                item['recommendation'] = "Urgent urology referral and biopsy strongly recommended"
                item['recommendation_fa'] = "ارجاع فوری به اورولوژی و بیوپسی اکیداً توصیه می‌شود"
                item['color_class'] = 'bg-danger'
            elif pbcg_score_high_cancer >= 0.05:
                item['score'] = pbcg_score_high_cancer
                item['status'] = 'Intermediate risk (PBCG)'
                item['status_fa'] = 'ریسک متوسط (PBCG)'
                item['recommendation'] = "Consider prostate biopsy or multiparametric MRI"
                item['recommendation_fa'] = "بیوپسی پروستات یا ام‌آرآی چندپارامتری را در نظر بگیرید"
                item['color_class'] = 'bg-warning'
            elif pbcg_score_low_cancer >= 0.20:
                item['score'] = pbcg_score_high_cancer
                item['status'] = 'Low-grade risk (PBCG)'
                item['status_fa'] = 'ریسک درجه پایین (PBCG)'
                item['recommendation'] = "Active surveillance or MRI-targeted biopsy"
                item['recommendation_fa'] = "پایش فعال یا بیوپسی هدفمند با ام‌آرآی"
                item['color_class'] = 'bg-info'
            elif pbcg_score_no_cancer < 0.50:
                item['score'] = pbcg_score_high_cancer
                item['status'] = 'Suspicious (PBCG)'
                item['status_fa'] = 'مشکوک (PBCG)'
                item['recommendation'] = "Repeat PSA or consider advanced imaging"
                item['recommendation_fa'] = "تکرار آزمایش PSA یا تصویربرداری پیشرفته را در نظر بگیرید"
                item['color_class'] = 'bg-primary'
            else:
                item['score'] = pbcg_score_high_cancer
                item['status'] = 'Very low risk (PBCG)'
                item['status_fa'] = 'ریسک بسیار کم (PBCG)'
                item['recommendation'] = "Continue routine screening as per guidelines"
                item['recommendation_fa'] = "غربالگری معمول را طبق دستورالعمل ادامه دهید"
                item['color_class'] = 'bg-success'

    print(selected_assessments)


    context['selected_assessments'] = selected_assessments
    context['code'] = code
    context['gender'] = gender
    context['age'] = int(age)

    return render(request, 'dashboard_fa.html', context)
