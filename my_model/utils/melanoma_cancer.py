class Melanoma_RiskCalculator:

    def calculate_risk( previous_cancer,
                        family_melanoma_cancer,
                        colored_hair,
                        colored_eyes,
                        fair_skin,
                        moles_count,
                        sunburns,
                        sunlamp,
                        immunosuppressive_drugs):

        melanoma_cancer_score = 0
        if previous_cancer == 'Yes':
            melanoma_cancer_score += 3

        if family_melanoma_cancer == 'Yes':
            melanoma_cancer_score += 9

        if colored_hair == 'Yes':
            melanoma_cancer_score += 2

        if colored_eyes == 'Yes':
            melanoma_cancer_score += 1

        if fair_skin == 'Yes':
            melanoma_cancer_score += 3

        if moles_count == 4:
            melanoma_cancer_score += 4
        elif moles_count == 3:
            melanoma_cancer_score += 3

        if sunburns == 'Yes':
            melanoma_cancer_score += 3

        if sunlamp == 'Yes':
            melanoma_cancer_score += 2

        if immunosuppressive_drugs == 'Yes':
            melanoma_cancer_score += 3

        return melanoma_cancer_score


