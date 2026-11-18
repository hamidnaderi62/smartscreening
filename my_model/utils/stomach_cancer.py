class Stomach_RiskCalculator:

    def calculate_risk( previous_cancer,
                        family_stomach_cancer,
                        fastfood,
                        cannedfood,
                        alcohol,
                        smoking,
                        h_pylori,
                        blood_group):

        stomach_cancer_score = 0
        if previous_cancer == 'Yes':
            stomach_cancer_score += 3

        if family_stomach_cancer == 'Yes':
            stomach_cancer_score += 10

        if fastfood == 4:
            stomach_cancer_score += 5
        elif fastfood == 3:
            stomach_cancer_score += 4
        elif fastfood == 2:
            stomach_cancer_score += 3

        if cannedfood == 5:
            stomach_cancer_score += 5
        elif cannedfood == 4:
            stomach_cancer_score += 3
        elif cannedfood <= 3:
            stomach_cancer_score += 1

        if alcohol > 0:
            stomach_cancer_score += 2

        if smoking > 0:
            stomach_cancer_score += 2

        if h_pylori == 'Yes':
            stomach_cancer_score += 6

        if blood_group in ['A+' , 'A-']:
            stomach_cancer_score += 2

        return stomach_cancer_score


