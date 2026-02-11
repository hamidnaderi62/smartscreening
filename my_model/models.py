from django.db import models
from django.contrib.auth.models import User


class AssessmentGroup(models.Model):
    name = models.CharField(max_length=200)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Assessment(models.Model):
    assessment_id = models.IntegerField(unique=True)
    title = models.CharField(max_length=200, null=True, blank=True)
    title_fa = models.CharField(max_length=200, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    description_fa = models.TextField(null=True, blank=True)
    image_file = models.ImageField(upload_to='images/assessmets',null=True, blank=True)
    groups = models.ManyToManyField(AssessmentGroup)
    active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title



class MyModel(models.Model):
    # Demographic Info
    userid = models.ForeignKey(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=100, null=True, blank=True)
    importer = models.CharField(max_length=100, null=True, blank=True)
    gender = models.CharField(max_length=10, null=True, blank=True)
    age = models.FloatField(max_length=10, null=True, blank=True)
    weight = models.FloatField(max_length=10, null=True, blank=True)
    height = models.FloatField(max_length=10, null=True, blank=True)
    waist_size = models.FloatField(max_length=10, null=True, blank=True)
    ethnicity = models.CharField(max_length=20, null=True, blank=True)
    born_place = models.CharField(max_length=20, null=True, blank=True)
    education = models.FloatField(max_length=10, null=True, blank=True)
    blood_group = models.CharField(max_length=20, null=True, blank=True)



    # LifeStyle
    activity = models.FloatField(max_length=10, null=True, blank=True)
    smoking = models.FloatField(max_length=10, null=True, blank=True)
    alcohol = models.FloatField(max_length=10, null=True, blank=True)
    meat = models.FloatField(max_length=10, null=True, blank=True)
    cereal = models.CharField(max_length=10, null=True, blank=True)
    vegetables = models.CharField(max_length=20, null=True, blank=True)
    dairy = models.FloatField(null=True, blank=True)
    multivitamin = models.CharField(max_length=10, null=True, blank=True)

    # Medical
    blood_pressure = models.CharField(max_length=20, null=True, blank=True)
    blood_glucose = models.CharField(max_length=20, null=True, blank=True)
    totchol = models.FloatField(null=True, blank=True)  # Total cholesterol (mg/dL)
    previous_cancer = models.CharField(max_length=10, null=True, blank=True)



    # Diabetes
    # waist_size = models.FloatField(max_length=10, null=True, blank=True)
    # vegetables = models.CharField(max_length=20, null=True, blank=True)
    # blood_pressure = models.CharField(max_length=20, null=True, blank=True)
    # blood_glucose = models.CharField(max_length=20, null=True, blank=True)
    relatives_diabetes = models.CharField(max_length=20, null=True, blank=True)
    ausdrisk_score = models.FloatField(max_length=100, null=True, blank=True)
    idf_score = models.FloatField(max_length=100, null=True, blank=True)
    uk_score = models.FloatField(max_length=100, null=True, blank=True)
    ada_score = models.FloatField(max_length=100, null=True, blank=True)
    canrisk_score = models.FloatField(max_length=100, null=True, blank=True)
    ausdrisk_status = models.CharField(max_length=500, null=True, blank=True)
    idf_status = models.CharField(max_length=500, null=True, blank=True)
    uk_status = models.CharField(max_length=500, null=True, blank=True)
    ada_status = models.CharField(max_length=500, null=True, blank=True)
    canrisk_status = models.CharField(max_length=500, null=True, blank=True)

    # Breast Cancer
    biopsy = models.IntegerField(null=True, blank=True)
    biopsy_num = models.IntegerField(null=True, blank=True)
    hyperplasia_biopsy = models.IntegerField(null=True, blank=True)
    menstruation_age = models.IntegerField(null=True, blank=True)
    child_age = models.IntegerField(null=True, blank=True)
    fdr_cancer = models.IntegerField(null=True, blank=True)
    breastfeeding = models.CharField(max_length=20, null=True, blank=True)
    cbe = models.CharField(max_length=20, null=True, blank=True)
    bse = models.CharField(max_length=20, null=True, blank=True)
    mammograms = models.CharField(max_length=20, null=True, blank=True)
    syndrome = models.CharField(max_length=20, null=True, blank=True)
    gene_mutation = models.CharField(max_length=20, null=True, blank=True)
    gene_mutation_fdr = models.CharField(max_length=20, null=True, blank=True)
    gail_score_abs_5 = models.FloatField(null=True, blank=True)
    gail_score_ave_5 = models.FloatField(null=True, blank=True)
    gail_score_abs_90 = models.FloatField(null=True, blank=True)
    gail_score_ave_90 = models.FloatField(null=True, blank=True)
    mymodel_gail_score = models.FloatField(null=True, blank=True)

    # CRC
    family_crc = models.CharField(max_length=10, null=True, blank=True)
    # multivitamin = models.CharField(max_length=10, null=True, blank=True)
    diabetes = models.CharField(max_length=10, null=True, blank=True)
    aspirin = models.CharField(max_length=100, null=True, blank=True)
    estrogen = models.CharField(max_length=100, null=True, blank=True)
    painmed = models.CharField(max_length=100, null=True, blank=True)
    crcpro_score = models.FloatField(max_length=100, null=True, blank=True)

    crc_history = models.CharField(max_length=10, null=True, blank=True)
    crc2_history = models.CharField(max_length=10, null=True, blank=True)
    ec_history = models.CharField(max_length=10, null=True, blank=True)
    ls_history = models.CharField(max_length=10, null=True, blank=True)
    crc_fdr = models.CharField(max_length=10, null=True, blank=True)
    crc_sdr = models.CharField(max_length=10, null=True, blank=True)
    ec_fdr = models.CharField(max_length=10, null=True, blank=True)
    ec_sdr = models.CharField(max_length=10, null=True, blank=True)
    ls_fdr = models.CharField(max_length=10, null=True, blank=True)
    ls_sdr = models.CharField(max_length=10, null=True, blank=True)
    min_age_crc = models.CharField(max_length=10, null=True, blank=True)
    min_age_crc_fdr = models.CharField(max_length=10, null=True, blank=True)
    min_age_crc_sdr = models.CharField(max_length=10, null=True, blank=True)
    min_age_ec = models.CharField(max_length=10, null=True, blank=True)
    min_age_ec_fdr = models.CharField(max_length=10, null=True, blank=True)
    min_age_ec_sdr = models.CharField(max_length=10, null=True, blank=True)
    premm_score = models.FloatField(max_length=100, null=True, blank=True)

    # Prostate (PBCG)
    psa = models.FloatField(null=True, blank=True)    # PSA(ng/ml) [2-50]
    famhistory = models.CharField(max_length=50, null=True, blank=True)    # Family History of Prostate Cancer
    dre = models.CharField(max_length=50, null=True, blank=True)    # Digital rectal examination
    priorbiopsy = models.CharField(max_length=50, null=True, blank=True)  # Prior biopsy
    pbcg_score_no_cancer = models.FloatField(null=True, blank=True)
    pbcg_score_low_cancer = models.FloatField(null=True, blank=True)
    pbcg_score_high_cancer = models.FloatField(null=True, blank=True)

    # ASCVD
    sbp = models.FloatField(null=True, blank=True)    # Systolic blood pressure (mm Hg)
    hdl = models.FloatField(null=True, blank=True)  # HDL cholesterol (mg/dL)
    # totchol = models.FloatField(null=True, blank=True)  # Total cholesterol (mg/dL)
    # bp_med = models.FloatField(null=True, blank=True)  # Patient is on a blood pressure medication (1=Yes, 0=No) [blood_pressure]
    # smoker = models.FloatField(null=True, blank=True)  # Current smoker (1=Yes, 0=No) [smoking > 0]
    # diabetes = models.FloatField(null=True, blank=True)  # Diabetes (1=Yes, 0=No) [blood_glucose]
    # lipid_med = models.FloatField(null=True, blank=True)  # Lipid medication (1=Yes, 0=No)
    # fh_heartattack  = models.FloatField(null=True, blank=True)  # Heart attack status (1=Yes, 0=No)
    # cac  = models.FloatField(null=True, blank=True)  # Coronary artery calcification
    ascvd_score = models.FloatField(null=True, blank=True)
    ascvd_status = models.CharField(max_length=500, null=True, blank=True)


    # my_cervical
    # age = models.FloatField(null=True, blank=True)
    num_sexual_partners = models.FloatField(null=True, blank=True)
    first_sexual_intercourse = models.FloatField(null=True, blank=True)
    num_pregnancies = models.FloatField(null=True, blank=True)
    # smoking = models.FloatField(null=True, blank=True)
    hormonal_contraceptives_years = models.FloatField(null=True, blank=True)
    iud = models.FloatField(null=True, blank=True)  # Intrauterine Device
    std = models.CharField(max_length=50, null=True, blank=True)
    cervical_cancer = models.CharField(max_length=50, null=True, blank=True)
    cytology = models.FloatField(null=True, blank=True)
    cin = models.FloatField(null=True, blank=True)
    hpv = models.FloatField(null=True, blank=True)
    cervical_cancer_score = models.FloatField(null=True, blank=True)
    cervical_cancer_grade = models.CharField(max_length=1000, null=True, blank=True)



    ### Melanoma Cancer
    # previous_cancer = models.CharField(max_length=10, null=True, blank=True)
    family_melanoma_cancer = models.CharField(max_length=10, null=True, blank=True)
    colored_hair = models.CharField(max_length=10, null=True, blank=True)
    colored_eyes = models.CharField(max_length=10, null=True, blank=True)
    fair_skin = models.CharField(max_length=10, null=True, blank=True)
    moles_count = models.FloatField(null=True, blank=True)
    sunburns = models.CharField(max_length=10, null=True, blank=True)
    sunlamp = models.CharField(max_length=10, null=True, blank=True)
    immunosuppressive_drugs = models.CharField(max_length=10, null=True, blank=True)
    melanoma_cancer_score = models.FloatField(null=True, blank=True)

    ### Osteoporosis
    rheumatoid_arthritis = models.CharField(max_length=10, null=True, blank=True)
    have_bmd_test = models.CharField(max_length=10, null=True, blank=True)
    result_bmd_test = models.CharField(max_length=50, null=True, blank=True)
    # blood_glucose
    chemotherapy = models.CharField(max_length=10, null=True, blank=True)
    steroid = models.CharField(max_length=10, null=True, blank=True)
    anticonvulsants = models.CharField(max_length=10, null=True, blank=True)
    # multivitamin
    # cereal = models.CharField(max_length=10, null=True, blank=True)
    # vegetables
    # dairy = models.FloatField(null=True, blank=True)
    calcium_supplements = models.CharField(max_length=10, null=True, blank=True)
    vitamin_d = models.CharField(max_length=10, null=True, blank=True)
    # alcohol
    # smoking
    # activity
    family_break_bone = models.CharField(max_length=50, null=True, blank=True)
    osteoporosis_score = models.FloatField(null=True, blank=True)

    ### Ovarian Cancer
    # previous_cancer
    family_breast_ovarian_prostate = models.CharField(max_length=10, null=True, blank=True)
    family_ovarian_cancer = models.CharField(max_length=10, null=True, blank=True)
    # gene_mutation
    talcum_powder = models.CharField(max_length=10, null=True, blank=True)
    # hormonal_contraceptives_years = models.FloatField(null=True, blank=True)
    # num_pregnancies
    menopause = models.CharField(max_length=10, null=True, blank=True)
    menopause_hormone = models.FloatField(null=True, blank=True)
    # breastfeeding
    hysterectomy = models.CharField(max_length=10, null=True, blank=True)
    endometriosis = models.CharField(max_length=10, null=True, blank=True)
    salpingectomy = models.CharField(max_length=10, null=True, blank=True)
    ovarian_cancer_score = models.FloatField(null=True, blank=True)

    ### Pancreatic Cancer
    # previous_cancer
    family_pancreatic_cancer = models.CharField(max_length=10, null=True, blank=True)
    # smoking
    # blood_glucose
    # blood_group = models.CharField(max_length=20, null=True, blank=True)
    chronic_pancreatitis = models.CharField(max_length=10, null=True, blank=True)
    pancreatic_cancer_score = models.FloatField(null=True, blank=True)

    ### Stomach Cancer
    # previous_cancer
    family_stomach_cancer = models.CharField(max_length=10, null=True, blank=True)
    fastfood = models.FloatField(null=True, blank=True)
    cannedfood = models.FloatField(null=True, blank=True)
    # alcohol
    # smoking
    h_pylori = models.CharField(max_length=20, null=True, blank=True)
    # blood_group
    stomach_cancer_score = models.FloatField(null=True, blank=True)

    ### Stroke
    previous_stroke = models.CharField(max_length=10, null=True, blank=True)
    # waist_size
    # cereal
    # vegetables
    # alcohol
    # smoking
    # activity
    # blood_glucose
    # blood_pressure
    history_totchol = models.CharField(max_length=10, null=True, blank=True)
    # totchol
    family_history_stroke = models.CharField(max_length=10, null=True, blank=True)
    stroke_score = models.FloatField(null=True, blank=True)

    selected_assessments_id = models.CharField(max_length=1000, null=True, blank=True)
    doctor_comment = models.TextField(null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.code}"


