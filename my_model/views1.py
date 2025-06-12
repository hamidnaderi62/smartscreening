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

from .utils.importer import *
import math
from django.conf import settings


###############################################
# my_model_questions
###############################################
def my_model_questions(request):
    return render(request, 'my_model/my_model.html', {"score": 0})


###############################################
# my_model_questions_voice
###############################################
def my_model_questions_voice(request):
    return render(request, 'my_model/my_model_voice.html', {"score": 0})


###############################################
# my_model_questions_fa
###############################################
def my_model_questions_fa(request):
    return render(request, 'my_model/my_model_fa.html', {"score": 0})


###############################################
# calculate_my_model
###############################################
def calculate_my_model(request):
### Demographic Info
    code = request.POST.get('code')
    gender = request.POST.get('gender')
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

    print(diabetes_results)

### Breaset Cancer
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

        print(breast_cancer_results)

### CRC Cancer
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

    print(crc_results)


### Prostat Cancer (PBCG)
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


    # load history
    my_models = MyModel.objects.filter(code=code).all().order_by('-created')[:5]
    my_model_last = MyModel.objects.filter(code=code).all().order_by('-created')[:1]
    my_patients = MyModel.objects.filter(userid=request.user.id).all().order_by('-created')[:10]
    my_history = MyModel.objects.filter(code=code).all().order_by('-created')[:10]

    date_history = [my_model.created.date().strftime("%Y-%m-%d") for my_model in my_models]
    # date_history = [my_model.created.year for my_model in my_models]

    ausdrisk_score_history = [float(my_model.ausdrisk_score) for my_model in my_models]
    idf_score_history = [float(my_model.idf_score) for my_model in my_models]
    uk_score_history = [float(my_model.uk_score) for my_model in my_models]
    ada_score_history = [float(my_model.ada_score) for my_model in my_models]

    crcpro_score_history = [float(my_model.crcpro_score) for my_model in my_models]
    premm_score_history = [float(my_model.premm_score) for my_model in my_models]

    pbcg_score_no_cancer_history = [my_model.pbcg_score_no_cancer for my_model in my_models]
    pbcg_score_low_cancer_history = [my_model.pbcg_score_low_cancer for my_model in my_models]
    pbcg_score_high_cancer_history = [my_model.pbcg_score_high_cancer for my_model in my_models]

    ascvd_score_history = [float(my_model.ascvd_score) for my_model in my_models]
    ascvd_status_history = [my_model.ascvd_status for my_model in my_models]

    cervical_cancer_score_history = [my_model.cervical_cancer_score for my_model in my_models]


    # Diabetes
    diabetes_contents = {}
    diabetes_doctors = {}
    breast_cancer_contents = {}
    breast_cancer_doctors = {}
    prostate_cancer_contents = {}
    prostate_cancer_doctors = {}

    if my_model_last[0].idf_score > 15:
        param = 'دیابت'
        res_contents = requests.get(f'{settings.SMARTLIFE_BASE_URL}/filter_content_list?q={param}')
        if res_contents.content:
            diabetes_contents = res_contents.json()

    if my_model_last[0].idf_score > 15:
        speciality = 1
        res_doctors = requests.get(f'{settings.SMARTLIFE_BASE_URL}/doctor/filter_doctor_list?q={speciality}')
        if res_doctors.content:
            diabetes_doctors = res_doctors.json()


    if gender == 'Male':
        # Prostate Cancer
        print(my_model_last[0].pbcg_score_high_cancer)
        if my_model_last[0].pbcg_score_high_cancer > 10:
            param = 'سرطان پروستات'
            res_contents = requests.get(f'{settings.SMARTLIFE_BASE_URL}/filter_content_list?q={param}')
            if res_contents.content:
                prostate_cancer_contents = res_contents.json()

        if my_model_last[0].pbcg_score_high_cancer > 10:
            speciality = 6
            res_doctors = requests.get(f'{settings.SMARTLIFE_BASE_URL}/doctor/filter_doctor_list?q={speciality}')
            if res_doctors.content:
                prostate_cancer_doctors = res_doctors.json()

    elif gender == 'Female':
        # Breast Cancer
        if my_model_last[0].gail_score_abs_5 > my_model_last[0].gail_score_ave_5:
            param = 'سرطان پستان'
            print(f'{settings.SMARTLIFE_BASE_URL}/filter_content_list?q={param}')
            res_contents = requests.get(f'{settings.SMARTLIFE_BASE_URL}/filter_content_list?q={param}')
            if res_contents.content:
                breast_cancer_contents = res_contents.json()

        if my_model_last[0].gail_score_abs_5 > my_model_last[0].gail_score_ave_5:
            speciality = 2
            res_doctors = requests.get(f'{settings.SMARTLIFE_BASE_URL}/doctor/filter_doctor_list?q={speciality}')
            if res_doctors.content:
                breast_cancer_doctors = res_doctors.json()



    print(f'my_model_last: {my_model_last}')
    return render(request, 'my_model/result.html',
                  context={
                      "code": code
                      , "gender": gender
                      , "age": int(age)
                      , "my_patients": my_patients
                      , "my_history": my_history
                      , "my_model_last": my_model_last[0]
                      , "date_history": list(reversed(date_history))

                      , "ausdrisk_score_history": list(reversed(ausdrisk_score_history))
                      , "idf_score_history": list(reversed(idf_score_history))
                      , "uk_score_history": list(reversed(uk_score_history))
                      , "ada_score_history": list(reversed(ada_score_history))

                      , "crcpro_score_history": list(reversed(crcpro_score_history))
                      , "premm_score_history": list(reversed(premm_score_history))

                      , "pbcg_score_no_cancer_history": list(reversed(pbcg_score_no_cancer_history))
                      , "pbcg_score_low_cancer_history": list(reversed(pbcg_score_low_cancer_history))
                      , "pbcg_score_high_cancer_history": list(reversed(pbcg_score_high_cancer_history))

                      , "ascvd_score_history": list(reversed(ascvd_score_history))
                      , "ascvd_status_history": list(reversed(ascvd_status_history))

                      , "cervical_cancer_score_history": list(reversed(cervical_cancer_score_history))

                      , "diabetes_contents": diabetes_contents
                      , "diabetes_doctors": diabetes_doctors
                      , "prostate_cancer_contents": prostate_cancer_contents
                      , "prostate_cancer_doctors": prostate_cancer_doctors
                      , "breast_cancer_contents": breast_cancer_contents
                      , "breast_cancer_doctors": breast_cancer_doctors
                           })


###############################################
# show_result(request)
###############################################
def show_result(request):
    code = request.POST.get('patient_code')
    print(f'patient code:{code}')
    # load history
    my_models = MyModel.objects.filter(code=code).all().order_by('-created')[:5]
    my_model_last = MyModel.objects.filter(code=code).all().order_by('-created')[:1]
    my_patients = MyModel.objects.filter(userid=request.user.id).all().order_by('-created')[:10]
    my_history = MyModel.objects.filter(code=code).all().order_by('-created')[:10]

    date_history = [my_model.created.date().strftime("%Y-%m-%d") for my_model in my_models]
    # date_history = [my_model.created.year for my_model in my_models]


    ausdrisk_score_history = [float(my_model.ausdrisk_score) for my_model in my_models]
    idf_score_history = [float(my_model.idf_score) for my_model in my_models]
    uk_score_history = [float(my_model.uk_score) for my_model in my_models]
    ada_score_history = [float(my_model.ada_score) for my_model in my_models]

    crcpro_score_history = [float(my_model.crcpro_score) for my_model in my_models]
    premm_score_history = [float(my_model.premm_score) for my_model in my_models]

    pbcg_score_no_cancer_history = [my_model.pbcg_score_no_cancer for my_model in my_models]
    pbcg_score_low_cancer_history = [my_model.pbcg_score_low_cancer for my_model in my_models]
    pbcg_score_high_cancer_history = [my_model.pbcg_score_high_cancer for my_model in my_models]

    ascvd_score_history = [float(my_model.ascvd_score) for my_model in my_models]
    ascvd_status_history = [my_model.ascvd_status for my_model in my_models]

    cervical_cancer_score_history = [my_model.cervical_cancer_score for my_model in my_models]

    return render(request, 'my_model/result.html',
                  context={
                      "code": code
                      , "gender": my_model_last[0].gender
                      , "age": int(my_model_last[0].age)
                      , "my_patients": my_patients
                      , "my_history": my_history
                      , "my_model_last": my_model_last[0]
                      , "date_history": list(reversed(date_history))

                      , "ausdrisk_score_history": list(reversed(ausdrisk_score_history))
                      , "idf_score_history": list(reversed(idf_score_history))
                      , "uk_score_history": list(reversed(uk_score_history))
                      , "ada_score_history": list(reversed(ada_score_history))

                      , "crcpro_score_history": list(reversed(crcpro_score_history))
                      , "premm_score_history": list(reversed(premm_score_history))

                      , "pbcg_score_no_cancer_history": list(reversed(pbcg_score_no_cancer_history))
                      , "pbcg_score_low_cancer_history": list(reversed(pbcg_score_low_cancer_history))
                      , "pbcg_score_high_cancer_history": list(reversed(pbcg_score_high_cancer_history))

                      , "ascvd_score_history": list(reversed(ascvd_score_history))
                      , "ascvd_status_history": list(reversed(ascvd_status_history))

                      , "cervical_cancer_score_history": list(reversed(cervical_cancer_score_history))
                  })

###############################################
# save_doctor_comment
###############################################
def save_doctor_comment(request):
    my_model_id = request.POST.get('my_model_id')
    doctor_comment = request.POST.get('doctor_comment')
    MyModel.objects.filter(id=my_model_id).update(doctor_comment=doctor_comment)
    return render(request, 'my_model/my_model.html', {"score": 0})



