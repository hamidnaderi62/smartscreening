import numpy as np
import math
from .breast_cancer_utils.gail3 import *

class BreastCancer:

    def get_age_category(age):
        if age >= 50:
            return 1
        return 0

    def calculate_risk(
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
                    ):

        ###########################
        # Matching Models

        # alcohol
        if alcohol > 0:
            alcohol = 'Yes'
        else:
            alcohol = 'No'
        ###########################

        gail_score_abs_5 = 0
        gail_score_ave_5 = 0
        gail_score_abs_90 = 0
        gail_score_ave_90 = 0
        mymodel_score = 0

        rhyp = np.float64(1.0)
        if hyperplasia_biopsy == 1:  # YES
            rhyp = np.float64(1.82)
        elif hyperplasia_biopsy == 0:  # NO
            rhyp = np.float64(0.93)
        elif hyperplasia_biopsy == 99:  # Unknown
            rhyp = np.float64(1.0)

        gailMod = GailRiskCalculator()
        gailMod.Initialize()
        gail_score_abs_5 = gailMod.CalculateRisk(1,  # riskIndex int    [1 = Abs, 2 = Ave]
                                                 age,  # CurrentAge int    [t1]
                                                 age + 5,  # ProjectionAge int    [t2]
                                                 BreastCancer.get_age_category(age),  # AgeIndicator int    [i0]
                                                 biopsy_num,  # NumberOfBiopsy int    [i2]
                                                 menstruation_age,  # MenarcheAge int    [i1]
                                                 child_age,  # FirstLiveBirthAge int    [i3]
                                                 biopsy,  # EverHaveBiopsy int    [iever]
                                                 fdr_cancer,  # FirstDegRelatives int    [i4]
                                                 hyperplasia_biopsy,  # int    [ihyp]  HyperPlasia
                                                 rhyp,  # double [rhyp]  RHyperPlasia
                                                 ethnicity  # irace int    [race]
                                                 )

        gail_score_ave_5 = gailMod.CalculateRisk(2,  # riskIndex int    [1 = Abs, 2 = Ave]
                                                 age,  # CurrentAge int    [t1]
                                                 age + 5,  # ProjectionAge int    [t2]
                                                 BreastCancer.get_age_category(age),  # AgeIndicator int    [i0]
                                                 biopsy_num,  # NumberOfBiopsy int    [i2]
                                                 menstruation_age,  # MenarcheAge int    [i1]
                                                 child_age,  # FirstLiveBirthAge int    [i3]
                                                 biopsy,  # EverHaveBiopsy int    [iever]
                                                 fdr_cancer,  # FirstDegRelatives int    [i4]
                                                 hyperplasia_biopsy,  # int    [ihyp]  HyperPlasia
                                                 rhyp,  # double [rhyp]  RHyperPlasia
                                                 ethnicity  # irace int    [race]
                                                 )

        gail_score_abs_90 = gailMod.CalculateRisk(1,  # riskIndex int    [1 = Abs, 2 = Ave]
                                                  age,  # CurrentAge int    [t1]
                                                  90,  # ProjectionAge int    [t2]
                                                  BreastCancer.get_age_category(age),  # AgeIndicator int    [i0]
                                                  biopsy_num,  # NumberOfBiopsy int    [i2]
                                                  menstruation_age,  # MenarcheAge int    [i1]
                                                  child_age,  # FirstLiveBirthAge int    [i3]
                                                  biopsy,  # EverHaveBiopsy int    [iever]
                                                  fdr_cancer,  # FirstDegRelatives int    [i4]
                                                  hyperplasia_biopsy,  # int    [ihyp]  HyperPlasia
                                                  rhyp,  # double [rhyp]  RHyperPlasia
                                                  ethnicity  # irace int    [race]
                                                  )

        gail_score_ave_90 = gailMod.CalculateRisk(2,  # riskIndex int    [1 = Abs, 2 = Ave]
                                                  age,  # CurrentAge int    [t1]
                                                  90,  # ProjectionAge int    [t2]
                                                  BreastCancer.get_age_category(age),  # AgeIndicator int    [i0]
                                                  biopsy_num,  # NumberOfBiopsy int    [i2]
                                                  menstruation_age,  # MenarcheAge int    [i1]
                                                  child_age,  # FirstLiveBirthAge int    [i3]
                                                  biopsy,  # EverHaveBiopsy int    [iever]
                                                  fdr_cancer,  # FirstDegRelatives int    [i4]
                                                  hyperplasia_biopsy,  # int    [ihyp]  HyperPlasia
                                                  rhyp,  # double [rhyp]  RHyperPlasia
                                                  ethnicity  # irace int    [race]
                                                  )

        gail_score_abs_5 = round(gail_score_abs_5 * 100, 1)
        gail_score_ave_5 = round(gail_score_ave_5 * 100, 1)
        gail_score_abs_90 = round(gail_score_abs_90 * 100, 1)
        gail_score_ave_90 = round(gail_score_ave_90 * 100, 1)

        alcohol_factor = 1
        breastfeeding_factor = 1
        cbe_factor = 1
        bse_factor = 1
        mammograms_factor = 1
        syndrome_factor = 1
        gene_mutation_fdr = 'No'

        if alcohol == 'YES':
            alcohol_factor = 1.05

        if breastfeeding == 'No':
            breastfeeding_factor = 1.05

        if cbe == 'YES':
            cbe_factor = 1.1

        if bse == 'YES':
            bse_factor = 1.1

        if mammograms == 'YES':
            mammograms_factor = 1.1

        if syndrome == 'YES':
            syndrome_factor = 1.01

        if gene_mutation == 'Yes' and (fdr_cancer == 1 or fdr_cancer == 2):
            gene_mutation_fdr = 'Yes'

        mymodel_gail_score = round(gail_score_abs_5 * alcohol_factor * breastfeeding_factor * cbe_factor * bse_factor * mammograms_factor * syndrome_factor, 1)

        breast_gail_threshold = 1

        results=({"gail_score_abs_5": gail_score_abs_5,
                   "gail_score_ave_5": gail_score_ave_5,
                   "gail_score_abs_90": gail_score_abs_90,
                   "gail_score_ave_90": gail_score_ave_90,
                   "mymodel_gail_score": mymodel_gail_score,
                   "gene_mutation_fdr": gene_mutation_fdr,
                   "breast_gail_threshold": breast_gail_threshold
                   })

        return results