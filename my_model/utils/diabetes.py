import numpy as np
import math

class Diabetes:

    def calculate_risk(
                      gender,
                      age,
                      weight,
                      height,
                      waist_size,
                      activity,
                      vegetables,
                      blood_pressure,
                      blood_glucose,
                      relatives_diabetes,
                      ethnicity,
                      born_place,
                      smoking,
                      ):



        ###########################
        # Matching Models

        # ethnicity
        if ethnicity == 1:
            ethnicity = 1
        elif ethnicity == 11:
            ethnicity = 2
        else:
            ethnicity = 3

        # activity
        if activity >= 0.5:
            activity = 'Yes'
        else:
            activity = 'No'

        # smoking
        if smoking > 0:
            smoking = 'Yes'
        else:
            smoking = 'No'
        ###########################


        bmi = weight / ((height / 100) ** 2)
        ausdrisk_score = 0
        ausdrisk_status = ''
        idf_score = 0
        idf_status = ''
        uk_score = 0
        uk_status = ''
        ada_score = 0
        ada_status = ''
        canrisk_score = 0
        canrisk_status = ''

        # AUSDRISK
        # age
        if age < 35:
            ausdrisk_score += 0
        elif (age >= 35) and (age <= 44):
            ausdrisk_score += 2
        elif (age >= 45) and (age <= 54):
            ausdrisk_score += 4
        elif (age >= 55) and (age <= 64):
            ausdrisk_score += 6
        elif age >= 65:
            ausdrisk_score += 8

        # gender
        if gender == 'Male':
            ausdrisk_score += 3
        elif gender == 'Female':
            ausdrisk_score += 0

        # ethnicity
        if ethnicity == '1':
            ausdrisk_score += 2
        else:
            ausdrisk_score += 0

        # born_place
        if born_place == '1':
            ausdrisk_score += 2
        elif born_place == '2':
            ausdrisk_score += 0

        # relatives_diabetes
        if relatives_diabetes == 'No':
            ausdrisk_score += 0
        elif relatives_diabetes == 'Yes_1':
            ausdrisk_score += 3
        elif relatives_diabetes == 'Yes_2':
            ausdrisk_score += 3

        # blood_pressure
        if blood_pressure == 'Yes':
            ausdrisk_score += 2
        elif blood_pressure == 'No':
            ausdrisk_score += 0

        # blood_glucose
        if blood_glucose == 'Yes':
            ausdrisk_score += 6
        elif blood_glucose == 'No':
            ausdrisk_score += 0

        # smoking
        if smoking == 'Yes':
            ausdrisk_score += 2
        elif smoking == 'No':
            ausdrisk_score += 0

        # vegetables
        if vegetables == 'every_day':
            ausdrisk_score += 0
        elif vegetables == 'not_every_day':
            ausdrisk_score += 1

        # activity
        if activity == 'Yes':
            ausdrisk_score += 0
        elif activity == 'No':
            ausdrisk_score += 2

        # waist_size
        if born_place == '1' or ethnicity == '1':
            if gender == 'Male':
                if waist_size < 90:
                    ausdrisk_score += 0
                elif (waist_size >= 90) and (waist_size <= 100):
                    ausdrisk_score += 4
                elif waist_size > 100:
                    ausdrisk_score += 7
            elif gender == 'Female':
                if waist_size < 80:
                    ausdrisk_score += 0
                elif (waist_size >= 80) and (waist_size <= 90):
                    ausdrisk_score += 4
                elif waist_size >= 90:
                    ausdrisk_score += 7
        else:
            if gender == 'Male':
                if waist_size < 102:
                    ausdrisk_score += 0
                elif (waist_size >= 102) and (waist_size <= 110):
                    ausdrisk_score += 4
                elif waist_size > 110:
                    ausdrisk_score += 7
            elif gender == 'Female':
                if waist_size < 88:
                    ausdrisk_score += 0
                elif (waist_size >= 88) and (waist_size <= 100):
                    ausdrisk_score += 4
                elif waist_size >= 100:
                    ausdrisk_score += 7

        # ausdrisk_status
        if (ausdrisk_score >= 0) and (ausdrisk_score <= 5):
            ausdrisk_status = 'Low risk'
        elif (ausdrisk_score >= 6) and (ausdrisk_score <= 11):
            ausdrisk_status = 'Intermediate risk'
        elif ausdrisk_score >= 12:
            ausdrisk_status = 'High risk'

        ##############################################
        # IDF RISK
        # age
        if age <= 45:
            idf_score += 0
        elif (age > 45) and (age <= 54):
            idf_score += 2
        elif (age >= 55) and (age <= 64):
            idf_score += 3
        elif age > 64:
            idf_score += 4

        # BMI
        if bmi < 25:
            idf_score += 0
        elif (bmi >= 25) and (bmi < 30):
            idf_score += 1
        elif bmi >= 30:
            idf_score += 3

        # waist_size
        if gender == 'Male':
            if waist_size < 94:
                idf_score += 0
            elif (waist_size >= 94) and (waist_size <= 102):
                idf_score += 3
            elif waist_size > 102:
                idf_score += 4
        elif gender == 'Female':
            if waist_size < 80:
                idf_score += 0
            elif (waist_size >= 80) and (waist_size <= 88):
                idf_score += 3
            elif waist_size > 88:
                idf_score += 4

        # activity
        if activity == 'Yes':
            idf_score += 0
        elif activity == 'No':
            idf_score += 2

        # vegetables
        if vegetables == 'every_day':
            idf_score += 0
        elif vegetables == 'not_every_day':
            idf_score += 1

        # blood_pressure
        if blood_pressure == 'Yes':
            idf_score += 2
        elif blood_pressure == 'No':
            idf_score += 0

        # blood_glucose
        if blood_glucose == 'Yes':
            idf_score += 5
        elif blood_glucose == 'No':
            idf_score += 0

        # relatives_diabetes
        if relatives_diabetes == 'No':
            idf_score += 0
        elif relatives_diabetes == 'Yes_1':
            idf_score += 5
        elif relatives_diabetes == 'Yes_2':
            idf_score += 3

        # idf_status
        if (idf_score >= 0) and (idf_score <= 6):
            idf_status = 'Low Risk'
        elif (idf_score >= 7) and (idf_score <= 11):
            idf_status = 'Slightly Increased Risk'
        elif (idf_score >= 12) and (idf_score <= 14):
            idf_status = 'Average Risk'
        elif (idf_score >= 15) and (idf_score <= 20):
            idf_status = 'High Risk'
        elif idf_score > 20:
            idf_status = 'Very High Risk'

        ##############################################
        # UK RISK
        # age
        if age <= 49:
            uk_score += 0
        elif (age >= 50) and (age <= 59):
            uk_score += 5
        elif (age >= 60) and (age <= 69):
            uk_score += 9
        elif age >= 70:
            uk_score += 13

        # gender
        if gender == 'Male':
            uk_score += 1
        elif gender == 'Female':
            uk_score += 0

        # ethnicity
        if ethnicity == '2':
            uk_score += 0
        else:
            uk_score += 6

        # relatives_diabetes
        if relatives_diabetes == 'No':
            uk_score += 0
        else:
            uk_score += 5

        # waist_size
        if waist_size < 90:
            uk_score += 0
        elif (waist_size >= 90) and (waist_size < 100):
            uk_score += 4
        elif (waist_size >= 100) and (waist_size < 110):
            uk_score += 6
        elif waist_size >= 110:
            uk_score += 9

        # BMI
        if bmi < 25:
            uk_score += 0
        elif (bmi >= 25) and (bmi < 30):
            uk_score += 3
        elif (bmi >= 30) and (bmi < 35):
            uk_score += 5
        elif bmi >= 35:
            uk_score += 8

        # blood_pressure
        if blood_pressure == 'Yes':
            uk_score += 5
        elif blood_pressure == 'No':
            uk_score += 0

        # uk_status
        if (uk_score >= 0) and (uk_score <= 6):
            uk_status = 'Low'
        elif (uk_score >= 7) and (uk_score <= 15):
            uk_status = 'Medium'
        elif (uk_score >= 16) and (uk_score <= 24):
            uk_status = 'High'
        elif (uk_score >= 25) and (uk_score <= 47):
            uk_status = 'Very High'

        ##############################################
        # ADA RISK
        # age
        if age < 40:
            ada_score += 0
        elif (age >= 40) and (age <= 49):
            ada_score += 1
        elif (age >= 50) and (age <= 59):
            ada_score += 2
        elif age >= 60:
            ada_score += 3

        # gender
        if gender == 'Male':
            ada_score += 1
        elif gender == 'Female':
            ada_score += 0

        # relatives_diabetes
        if relatives_diabetes == 'No':
            ada_score += 0
        else:
            ada_score += 1

        # BMI & waist_size
        if gender == 'Male':
            if (waist_size < 94) or bmi < 25:
                ada_score += 0
            elif ((waist_size >= 94) and (waist_size < 102)) or ((bmi >= 25) and (bmi < 30)):
                ada_score += 1
            elif ((waist_size >= 102) and (waist_size <= 127)) or ((bmi >= 30) and (bmi < 40)):
                ada_score += 2
            elif (waist_size > 127) or (bmi >= 40):
                ada_score += 3
        elif gender == 'Female':
            if (waist_size < 80) or bmi < 25:
                ada_score += 0
            elif ((waist_size >= 80) and (waist_size < 89)) or ((bmi >= 25) and (bmi < 30)):
                ada_score += 1
            elif ((waist_size >= 89) and (waist_size <= 124)) or ((bmi >= 30) and (bmi < 40)):
                ada_score += 2
            elif (waist_size > 124) or (bmi >= 40):
                ada_score += 3

        # blood_pressure
        if blood_pressure == 'Yes':
            ada_score += 1
        elif blood_pressure == 'No':
            ada_score += 0

        # activity
        if activity == 'Yes':
            ada_score += 0
        elif activity == 'No':
            ada_score += 1

        ### ada_status
        if (ada_score < 4):
            ada_status = 'low risk'
        elif (ada_score >= 4) and (ada_score < 5):
            ada_status = 'high risk undiagnosed diabetes or pre-diabetes'
        elif (ada_score >= 5):
            ada_status = 'high risk undiagnosed diabetes'


        results=({"ausdrisk_score": ausdrisk_score, "ausdrisk_status": ausdrisk_status
                                            , "idf_score": idf_score, "idf_status": idf_status
                                            , "uk_score": uk_score, "uk_status": uk_status
                                            , "ada_score": ada_score, "ada_status": ada_status
                                            })
        return results