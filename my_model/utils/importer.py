from django.http import JsonResponse,HttpResponse
from ..models import MyModel
from ..utils.breast_cancer import *
from ..utils.cervical import *
import pandas as pd
from pathlib import Path
import os

###############################################
# calculate_breast_csv
###############################################

def calculate_breast_csv(request):
    file_name= 'my_model_breast.csv'
    data_dir = Path(__file__).parent
    file_address = os.path.join(data_dir, 'data/', file_name)
    print(f'file_address: {file_address}')

    col_names = ['code'
                ,'age'
                ,'ethnicity'
                ,'biopsy'
                ,'biopsy_num'
                ,'hyperplasia_biopsy'
                ,'menstruation_age'
                ,'child_age'
                ,'fdr_cancer'
                ,'alcohol'
                ,'breastfeeding'
                ,'cbe'
                ,'bse'
                ,'mammograms'
                ,'syndrome'
                ,'gene_mutation']
    df = pd.read_csv(file_address, sep=',', names=col_names, header=None, skiprows=1)

    for index,row in df[:50].iterrows():
        print(f'row: {index}')
        code = row['code']
        age = float(row['age'])
        ethnicity = int(row['ethnicity'])
        biopsy = int(row['biopsy'])
        biopsy_num = int(row['biopsy_num'])
        hyperplasia_biopsy = int(row['hyperplasia_biopsy'])
        menstruation_age = int(row['menstruation_age'])
        child_age = int(row['child_age'])
        fdr_cancer = int(row['fdr_cancer'])
        alcohol =row['alcohol']
        breastfeeding = row['breastfeeding']
        cbe = row['cbe']
        bse = row['bse']
        mammograms = row['mammograms']
        syndrome = row['syndrome']
        gene_mutation = row['gene_mutation']
        gender = 'Female'

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

        MyModel.objects.create(userid=request.user,
                               code=code,
                               importer='breast1',
                               gender=gender,
                               age=age,
                               ethnicity=ethnicity,
                               # LifeStyle
                               alcohol=alcohol,
                               # Diabetes
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
                               # Prostate (PBCG)
                               # Cardiovascular (ASCVD)
                               # my_cervical
                               )
        return HttpResponse("finish")

###############################################
# calculate_cervical_csv
###############################################
def calculate_cervical_csv(request):
    file_name= 'my_model_cervical.csv'
    data_dir = Path(__file__).parent.parent
    file_address = os.path.join(data_dir, 'data/', file_name)

    col_names = ['code'
                ,'age'
                ,'num_sexual_partners'
                ,'first_sexual_intercourse'
                ,'num_pregnancies'
                ,'smoking'
                ,'hormonal_contraceptives_years'
                ,'iud'
                ,'std'
                ,'cervical_cancer'
                ,'cytology'
                ,'cin'
                ,'hpv']
    df = pd.read_csv(file_address, sep=',', names=col_names, header=None, skiprows=1)

    cervical_cancer_grades = {
        1: 'Low risk (Follow up based on your health care provider and national guidline, e.g., USPSTF (174), ACS (177), and ACOG (175))',
        2: 'Follow up by health care provider and likely ask you to come back for additional testing to make sure that there are not more serious (high-grade) changes.)',
        3: 'High risk (Follow up by gynaecologist are needed. Your health care provider will recommend follow-up steps you need to take)',
    }

    for index,row in df.iterrows():
        print(f'row: {index}')
        code = row['code']
        age = float(row['age'])
        num_sexual_partners = float(row['num_sexual_partners'])
        first_sexual_intercourse = float(row['first_sexual_intercourse'])
        num_pregnancies = float(row['num_pregnancies'])
        smoking = float(row['smoking'])
        hormonal_contraceptives_years = float(row['hormonal_contraceptives_years'])
        iud = float(row['iud'])
        std = row['std']
        cervical_cancer = row['cervical_cancer']
        cytology = float(row['cytology'])
        cin = float(row['cin'])
        hpv = float(row['hpv'])
        gender = 'Female'

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

        cervical_cancer_grade = cervical_cancer_grades.get(cervical_cancer_score)
        MyModel.objects.create(userid=request.user,
                           code=code,
                           importer= 'cervical1',
                           gender=gender,
                           age=age,
                           # LifeStyle
                           smoking=smoking,
                           # Diabetes
                           # Breast Cancer
                           # CRC
                           # Prostate (PBCG)
                           # Cardiovascular (ASCVD)
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
        return HttpResponse("finish")

    ###############################################
# show_csv
###############################################
def show_csv(request):
    my_list = MyModel.objects.filter(code= '110000').all().order_by('-created')[:5]
    print(my_list[0].mymodel_gail_score)
    res = {
        'cervical_cancer_score': my_list[0].cervical_cancer_score
        }
    return JsonResponse(res)

###############################################
# export_to_csv
###############################################
import csv

def export_to_csv(request):
    # Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="breast_data.csv"'

    writer = csv.writer(response)
    # writer.writerow(['Column1', 'Column2', 'Column3'])  # Write your headers

    queryset = MyModel.objects.filter(importer='cervical1').all().order_by('created')
    for obj in queryset:
        writer.writerow([obj.code, obj.importer, obj.cervical_cancer_score, obj.cervical_cancer_grade])  # Write your data

    return response