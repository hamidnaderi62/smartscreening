class Osteoporosis_RiskCalculator:

    def calculate_risk( rheumatoid_arthritis,
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
                        family_break_bone):

        osteoporosis_score = 0
        if rheumatoid_arthritis == 'Yes':
            osteoporosis_score += 3

        if have_bmd_test == 'Yes':
            osteoporosis_score += 0

        if result_bmd_test == 'Dont know':
            osteoporosis_score += 0
        elif result_bmd_test == 'Normal BMD':
            osteoporosis_score += 0
        elif result_bmd_test == 'Low BMD':
            osteoporosis_score += 2
        elif result_bmd_test == 'Osteoporosis':
            osteoporosis_score += 40

        if blood_glucose == 'Yes':
            osteoporosis_score += 2

        if chemotherapy == 'Yes':
            osteoporosis_score += 15
            #osteoporosis_score += 5

        if steroid == 'Yes':
            osteoporosis_score += 5
            #osteoporosis_score += 3

        if anticonvulsants == 'Yes':
            osteoporosis_score += 2

        if multivitamin == 'No':
            osteoporosis_score += 3

        if cereal == 'No':
            osteoporosis_score += 2

        if vegetables == 'not_every_day':
            osteoporosis_score += 2

        if dairy == 1:
            osteoporosis_score += 4
        elif dairy == 2:
            osteoporosis_score += 2

        if calcium_supplements == 'No':
            osteoporosis_score += 3

        if vitamin_d == 'No':
            osteoporosis_score += 3

        if alcohol >= 4:
            osteoporosis_score += 10
        elif alcohol >= 3:
            osteoporosis_score += 8
        elif alcohol >= 2:
            osteoporosis_score += 6
        elif alcohol >= 1:
            osteoporosis_score += 4


        if smoking > 0:
            osteoporosis_score += 2

        if activity < 0.5:
            osteoporosis_score += 3

        if family_break_bone == 'Yes':
            osteoporosis_score += 5

        return osteoporosis_score


