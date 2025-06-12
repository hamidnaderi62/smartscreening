class Stroke_RiskCalculator:

    def calculate_risk(previous_stroke,
                        waist_size,
                        cereal,
                        vegetables,
                        alcohol,
                        smoking,
                        activity,
                        blood_glucose,
                        blood_pressure,
                        history_totchol,
                        totchol,
                        family_history_stroke):

        stroke_score = 0
        if previous_stroke == 'Yes':
            stroke_score += 5

        if waist_size >= 102:
            stroke_score += 2

        if cereal == 'No':
            stroke_score += 3

        if vegetables == 'not_every_day':
            stroke_score += 2

        if alcohol == 0:
            stroke_score += 0
        elif alcohol == 1:
            stroke_score += 1
        elif alcohol == 2:
            stroke_score += 2
        elif alcohol == 3:
            stroke_score += 3
        elif alcohol >= 4:
            stroke_score += 4

        if smoking > 0:
            stroke_score += 2

        if activity < 0.5:
            stroke_score += 2

        if blood_glucose == 'Yes':
            stroke_score += 4

        if history_totchol == 'Yes':
            stroke_score += 2

        if totchol >= 280:
            stroke_score += 4
        elif totchol >= 240:
            stroke_score += 3
        elif totchol >= 200:
            stroke_score += 2

        if family_history_stroke == 'Yes':
            stroke_score += 7

        return stroke_score


