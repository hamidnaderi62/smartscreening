import numpy as np

class ProstateRiskCalculator:

    def calculate_risk(psa, age, ethnicity, priorbiopsy=None, dre=None, famhistory=None):

        race = 0
        ###########################
        # Matching Models
        if ethnicity == 2:
            race = 1  #'Black'
        else:
            race = 0
        ###########################

        # Create persons data set
        data = [1, np.log2(psa), age, race]

        # Is priorbiopsy known?
        a = int(priorbiopsy is not None)
        if a == 1:
            data.append(priorbiopsy)

        # Is dre known?
        b = int(dre is not None)
        if b == 1:
            data.append(dre)

        # Is famhistory known?
        c = int(famhistory is not None)
        if c == 1:
            data.append(famhistory)

        # Choose correct model
        if a == 1 and b == 1 and c == 1:
            no_low = np.array([-2.44052108, 0.13617244, 0.01780617, 0.78721039, -0.83613721, 0.04612721, 0.33233636])
            no_high = np.array([-6.36851856, 0.79996510, 0.05566536, 0.61596975, -1.27437249, 0.85780143, 0.61003848])
        elif a == 1 and b == 1 and c == 0:
            no_low = np.array([-2.29687989, 0.13785591, 0.01758914, 0.63876791, -0.86200471, 0.07193350])
            no_high = np.array([-6.06621401, 0.76053930, 0.05509847, 0.51701373, -1.38390751, 0.83442202])
        elif a == 1 and b == 0 and c == 1:
            no_low = np.array([-2.64840984, 0.13125283, 0.02044166, 0.81792881, -0.98610357, 0.31447017])
            no_high = np.array([-6.70538152, 0.77635003, 0.06542705, 0.52401464, -1.43681965, 0.55443478])
        elif a == 0 and b == 1 and c == 1:
            no_low = np.array([-2.16147411, 0.07409519, 0.01322988, 0.76131045, 0.05397516, 0.29246219])
            no_high = np.array([-5.99897055, 0.70727793, 0.04992968, 0.56485952, 0.89154384, 0.56910873])
        elif a == 1 and b == 0 and c == 0:
            no_low = np.array([-2.49050385, 0.12961272, 0.02020429, 0.67674970, -0.97275826])
            no_high = np.array([-6.41089002, 0.74110558, 0.06476911, 0.42814591, -1.50274350])
        elif a == 0 and b == 1 and c == 0:
            no_low = np.array([-2.01851079, 0.06745424, 0.01263369, 0.63938472, 0.08562844])
            no_high = np.array([-5.68203352, 0.65059244, 0.04883786, 0.49214793, 0.87421554])
        elif a == 0 and b == 0 and c == 1:
            no_low = np.array([-2.39161580, 0.06129651, 0.01600515, 0.81132928, 0.27501639])
            no_high = np.array([-6.42320154, 0.67779036, 0.06092178, 0.50429130, 0.50805684])
        else:  # a == 0 and b == 0 and c == 0
            no_low = np.array([-2.23794923, 0.05343098, 0.01553627, 0.69593716])
            no_high = np.array([-6.13292904, 0.62979529, 0.06002002, 0.43816016])

        # Predicting probabilities
        S1 = np.dot(no_low, data)
        S2 = np.dot(no_high, data)
        risk_no = 1 / (1 + np.exp(S1) + np.exp(S2)) * 100
        risk_low = np.exp(S1) / (1 + np.exp(S1) + np.exp(S2)) * 100
        risk_high = 100 - risk_no - risk_low

        # Outcome
        risk_outcome = np.array([round(risk_no), round(risk_low), round(risk_high)]).reshape(1, -1)

        # Add Dimnames to Vector
        results=({"pbcg_score_no_cancer": risk_outcome[0][0],
                  "pbcg_score_low_cancer": risk_outcome[0][1],
                  "pbcg_score_high_cancer": risk_outcome[0][2]
                                            })

        return results