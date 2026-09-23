class Cervical_RiskCalculator:

    def calculate_risk( num_sexual_partners,
                        first_sexual_intercourse,
                        num_pregnancies,
                        smoking,
                        hormonal_contraceptives_years,
                        iud,
                        std,
                        cervical_cancer,
                        cytology,
                        cin,
                        hpv):

        if hpv == 4:
            cervical_cancer_score = 3
        elif cin > 2:
            cervical_cancer_score = 3
        elif cin > 1 and hpv > 1:
            cervical_cancer_score = 3
        elif hpv > 1:
            cervical_cancer_score = 2
        elif hpv == 1 and cytology > 2:
            cervical_cancer_score = 2
        elif cytology > 2 and num_sexual_partners > 1:
            cervical_cancer_score = 2
        elif cytology > 2 and hormonal_contraceptives_years > 1:
            cervical_cancer_score = 2
        elif cytology > 2 and std == 'Yes':
            cervical_cancer_score = 2
        elif cytology > 2 and cervical_cancer == 'Yes':
            cervical_cancer_score = 2
        #elif hpv == 1 and cytology < 3 and std == 'Yes':
        #    cervical_cancer_score = 2
        elif hpv == 1 and cytology < 3 and cervical_cancer == 'Yes':
            cervical_cancer_score = 2
        else:
            cervical_cancer_score = 1
        return cervical_cancer_score