class Ovarian_RiskCalculator:

    def calculate_risk(previous_cancer,
                        family_breast_ovarian_prostate,
                        family_ovarian_cancer,
                        gene_mutation,
                        talcum_powder,
                        hormonal_contraceptives_years,
                        num_pregnancies,
                        menopause,
                        menopause_hormone,
                        breastfeeding,
                        hysterectomy,
                        endometriosis,
                        salpingectomy):

        ovarian_cancer_score = 0
        if previous_cancer == 'Yes':
            ovarian_cancer_score += 3

        if family_breast_ovarian_prostate == 'Yes':
            ovarian_cancer_score += 7

        if family_ovarian_cancer == 'Yes':
            ovarian_cancer_score += 6

        if gene_mutation == 'Yes':
            ovarian_cancer_score += 4

        if talcum_powder == 'Yes':
            ovarian_cancer_score += 2

        # ????????
        if hormonal_contraceptives_years > 0:
            ovarian_cancer_score += 1

        if num_pregnancies == 0:
            ovarian_cancer_score += 2
        elif num_pregnancies == 1:
            ovarian_cancer_score += 1

        if menopause == 'Yes':
            ovarian_cancer_score += 3

        if menopause_hormone == 4:
            ovarian_cancer_score += 3
        elif menopause_hormone == 3:
            ovarian_cancer_score += 1

        if breastfeeding == 'No':
            ovarian_cancer_score += 2

        if hysterectomy == 'Yes':
            ovarian_cancer_score += 2

        if endometriosis == 'Yes':
            ovarian_cancer_score += 2

        if salpingectomy == 'Yes':
            ovarian_cancer_score += 4

        return ovarian_cancer_score


