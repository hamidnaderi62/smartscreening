class Pancreatic_RiskCalculator:

    def calculate_risk( previous_cancer,
                        family_pancreatic_cancer,
                        smoking,
                        blood_glucose,
                        blood_group,
                        chronic_pancreatitis):

        pancreatic_cancer_score = 0
        if previous_cancer == 'Yes':
            #not accurate estimate of your risk
            pancreatic_cancer_score += 3

        if family_pancreatic_cancer == 'Yes':
            pancreatic_cancer_score += 10

        if smoking > 0:
            pancreatic_cancer_score += 3

        if blood_glucose == 'Yes':
            pancreatic_cancer_score += 3

        if blood_group in ['A','B','AB']:
            pancreatic_cancer_score += 3

        if chronic_pancreatitis == 'Yes':
            pancreatic_cancer_score += 10

        return pancreatic_cancer_score

