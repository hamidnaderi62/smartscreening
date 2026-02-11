import numpy as np
import math


class CRC:

    def calculate_risk(
                    gender,
                    age,
                    ethnicity,
                    smoking,
                    alcohol,
                    weight,
                    height,
                    education,
                    family_crc,
                    multivitamin,
                    meat,
                    diabetes,
                    activity,  # male
                    aspirin,  # male
                    estrogen,  # female
                    painmed,  # female

                    v1_v2,
                    v3,
                    v4,
                    v5_AB,
                    v5_CD,
                    v6_AB,
                    v6_CD,
                    v7_E,
                    v7_F,
                    v8_MinAge_CRC,
                    v8_MinAge_CRC_FDR,
                    v8_MinAge_CRC_SDR,
                    v9_MinAge_EC,
                    v9_MinAge_EC_FDR,
                    v9_MinAge_EC_SDR
                      ):

        ###########################
        # Matching Models
        if ethnicity == 1:
            ethnicity = 'White'
        elif ethnicity == 8:
            ethnicity = 'Japanese'
        elif ethnicity == 10:
            ethnicity = 'Hawaiian'
        else:
            ethnicity = 'Latino'
        ###########################


        crcpro_score = 0
        premm_score = 0

        if (gender == 'Female'):
            lp = -5.9026635 + \
                 0.090012542 * age + \
                 4.4217156e-05 * max(age - 47, 0) ** 3 + \
                 9.2119076e-05 * max(age - 60, 0) ** 3 + \
                 -4.7901919e-05 * max(age - 72, 0) ** 3 + \
                 -0.24100367 * (ethnicity == "Hawaiian") + \
                 0.014010715 * (ethnicity == "Japanese") + \
                 -0.39669678 * (ethnicity == "Latino") + \
                 -0.34056094 * (ethnicity == "White") + \
                 0.07443905 * education + \
                 -0.00062546554 * max(education - 7, 0) ** 3 + \
                 0.0017200302 * max(education - 14, 0) ** 3 + \
                 -0.0010945647 * max(education - 18, 0) ** 3 + \
                 -0.24500762 * (estrogen == "Yes-currently") + \
                 -0.044320489 * (estrogen == "Yes-previously") + \
                 0.23328937 * (diabetes == "Yes") + \
                 0.062703176 * smoking + \
                 -0.002446026 * max(smoking, 0) ** 3 + \
                 0.003038396 * max(smoking - 1.25, 0) ** 3 + \
                 -0.00059134632 * max(smoking - 6.375, 0) ** 3 + \
                 -1.023614e-06 * max(smoking - 27.5125, 0) ** 3 + \
                 0.31589053 * (family_crc == "Yes") + \
                 -0.1665365 * (multivitamin == "Yes") + \
                 0.0075233925 * weight / (height ** 2) + \
                 6.7918662e-05 * max(weight / (height ** 2) - 20.371336, 0) ** 3 + \
                 -0.00011039091 * max(weight / (height ** 2) - 25.508027, 0) ** 3 + \
                 4.2472244e-05 * max(weight / (height ** 2) - 33.722266, 0) ** 3 + \
                 -0.046383323 * (painmed == "Yes, but not currently") + \
                 -0.236997 * (painmed == "Yes, currently") + \
                 -0.08856241 * alcohol + \
                 0.62375456 * max(alcohol, 0) ** 3 + \
                 -0.7191129 * max(alcohol - 0.10740682, 0) ** 3 + \
                 0.095358349 * max(alcohol - 0.8099724, 0) ** 3
            crcpro_score = math.floor(100 - 100 * 0.9901043 ** math.exp(lp))
        else:
            lp = -6.6419738 + \
                 0.091669179 * age + \
                 -3.7411814e-05 * max(age - 47, 0) ** 3 + \
                 7.794128e-05 * max(age - 60, 0) ** 3 + \
                 -4.0529466e-05 * max(age - 72, 0) ** 3 + \
                 0.16092241 * (ethnicity == "Hawaiian") + \
                 0.25353936 * (ethnicity == "Japanese") + \
                 -0.13659953 * (ethnicity == "Latino") + \
                 -0.16728044 * (ethnicity == "White") + \
                 0.00022581331 * smoking + \
                 1.1341047e-05 * max(smoking, 0) ** 3 + \
                 -1.3522018e-05 * max(smoking - 6.375, 0) ** 3 + \
                 2.1809706e-06 * max(smoking - 39.525, 0) ** 3 + \
                 0.28379769 * alcohol + \
                 -0.21424251 * max(alcohol, 0) ** 3 + \
                 0.22570057 * max(alcohol - 0.14457189, 0) ** 3 + \
                 -0.011458065 * max(alcohol - 2.8477722, 0) ** 3 + \
                 0.018020786 * weight / (height ** 2) + \
                 9.4715899e-05 * max(weight / (height ** 2) - 22.047175, 0) ** 3 + \
                 -0.00015791645 * max(weight / (height ** 2) - 25.941735, 0) ** 3 + \
                 6.3200548e-05 * max(weight / (height ** 2) - 31.778341, 0) ** 3 + \
                 0.072052428 * education + \
                 -0.00060634342 * max(education - 7, 0) ** 3 + \
                 0.0016674444 * max(education - 14, 0) ** 3 + \
                 -0.001061101 * max(education - 18, 0) ** 3 + \
                 -0.032284161 * (aspirin == "Yes - Not Currently") + \
                 -0.20960315 * (aspirin == "Yes") + \
                 0.24250922 * (family_crc == "Yes") + \
                 -0.19175375 * (multivitamin == "Yes") + \
                 0.073141733 * meat + \
                 -0.0043503766 * max(meat - 0.59081962, 0) ** 3 + \
                 0.0065250851 * max(meat - 2.0822052, 0) ** 3 + \
                 -0.0021747085 * max(meat - 5.0656345, 0) ** 3 + \
                 0.11020556 * (diabetes == "Yes") + \
                 -0.090669913 * activity + \
                 0.0093816671 * max(activity - 0.10714286, 0) ** 3 + \
                 -0.011850527 * max(activity - 0.82142857, 0) ** 3 + \
                 0.0024688598 * max(activity - 3.5357143, 0) ** 3
            crcpro_score = math.floor(100 - 100 * 0.9846654 ** math.exp(lp))

        crcpro_score = round(crcpro_score, 2)

        #################################################
        # PREMM5
        #################################################
        # v0 = Sex of patient; v0 = 1 if male, 0 if female
        # v0 = int(request.POST.get('v0'))
        v0 = 1 if gender == 'Male' else 0

        # v1 = patient has presence of one CRC
        # v1 = int(request.POST.get('v1'))

        # v2 = patient has presence of two or more CRCs
        # v2 = int(request.POST.get('v2'))

        # v1 = patient has presence of one CRC
        # v2 = patient has presence of two or more CRCs
        v1 = 0
        v2 = 0
        v1_v2 = int(v1_v2)
        if v1_v2 == 0:
            v1 = 0
            v2 = 0
        elif v1_v2 == 1:
            v1 = 1
            v2 = 0
        elif v1_v2 == 2:
            v1 = 0
            v2 = 1

        # v3 = Patient has presence of EC
        v3 = int(v3)

        # v4 = Patient has presence of other LS(Lynch syndrome)-related cancer
        v4 = int(v4)

        # v5 = Presence of CRC in FDR and/or SDR
        # v5 = 1 * presence of CRC in 1 FDR (A) + 2 * presence of CRC in 2 or more FDR (B) + 0.5 * presence of CRC in 1 SDR (C) + 1 * presence of CRC in 2 or more SDR (D)
        # Note: Possible values for A through D: 0 and 1; 0 = absent, 1 = present
        # A and B are mutually exclusive; if A is 1, then B must be 0.
        # C and D are mutually exclusive; if C is 1, then D must be 0.
        v5_ab = int(v5_AB)
        v5_cd = int(v5_CD)
        # v5 = 1 * v5_a + 2 * v5_b + 0.5 * v5_c + 1 * v5_d
        v5 = v5_ab + 0.5 * v5_cd

        # v6 =  Presence of EC in FDR and/or SDR
        # v6 = 1 * presence of EC in 1 FDR (A) + 2 * presence of EC in 2 or more FDR (B) + 0.5 * presence of EC in 1 SDR (C) + 1 * presence of EC in 2 or more SDR (D)
        # Note: Possible values for A through D: 0 and 1; 0 = absent, 1 = present
        # A and B are mutually exclusive; if A is 1, then B must be 0.
        # C and D are mutually exclusive; if C is 1, then D must be 0.
        v6_ab = int(v6_AB)
        v6_cd = int(v6_CD)
        # v6 = 1 * v6_a + 2 * v6_b + 0.5 * v6_c + 1 * v6_d
        v6 = v6_ab + 0.5 * v6_cd

        # v7 =  Presence of other LS-related cancer in FDR or SDR
        # v7 = 1 * presence of other LS related cancer in FDR (E) + 0.5 * presence of other LS related cancer in SDR (F)
        # Note: Possible values for E and F: 0 and 1; 0 = absent, 1 = present.
        # E and F are not mutually exclusive
        v7_e = int(v7_E)
        v7_f = int(v7_F)
        v7 = 1 * v7_e + 0.5 * v7_f

        # V8/V9 = Ages at diagnosis refers to the youngest age at diagnosis (in years) for the patient and/or relatives with diagnosis.
        # If a patient or relative had a given diagnosis but the age at diagnosis was unknown, then the age at diagnosis should be estimated.
        # NOTE:
        # 1. If no age is entered, the model defaults to age at diagnosis of 45 years. This will happen in the following cases:
        # a) If the patient and/or relatives are unaffected, the model defaults to age at diagnosis of 45 years, and
        # b) If no age is entered for an affected proband and/or relative, the model defaults to age at diagnosis of 45 years
        # 2. The following age limits (upper and lower) must be applied, when necessary, before the composite V8 and V9 variables, described
        # earlier in this table, are created. If the reported ages for the patient, FDRs, and/or SDRs are less than or greater than the following age
        # limits, the ages must be corrected to the values shown in Appendix Table A2
        # v8 = (minimum age of CRC in the proband - 45) + (minimum age of CRC in a FDR - 45) + (minimum age of CRC in an SDR - 45)

        v8_min_age_crc = int(v8_MinAge_CRC)
        v8_min_age_crc_fdr = int(v8_MinAge_CRC_FDR)
        v8_min_age_crc_sdr = int(v8_MinAge_CRC_SDR)

        if v1_v2 == 0:
            v8_min_age_crc = 45

        if v5_ab == 0:
            v8_min_age_crc_fdr = 45

        if v5_cd == 0:
            v8_min_age_crc_sdr = 45

        min_age_crc = 27
        min_age_crc_fdr = 28
        min_age_crc_sdr = 30

        max_age_crc = 77
        max_age_crc_fdr = 81
        max_age_crc_sdr = 85

        # Check Min
        if v8_min_age_crc < min_age_crc:
            v8_min_age_crc = min_age_crc

        if v8_min_age_crc_fdr < min_age_crc_fdr:
            v8_min_age_crc_fdr = min_age_crc_fdr

        if v8_min_age_crc_sdr < min_age_crc_sdr:
            v8_min_age_crc_sdr = min_age_crc_sdr

        # Check Max
        if v8_min_age_crc > max_age_crc:
            v8_min_age_crc = max_age_crc

        if v8_min_age_crc_fdr > max_age_crc_fdr:
            v8_min_age_crc_fdr = max_age_crc_fdr

        if v8_min_age_crc_sdr > max_age_crc_sdr:
            v8_min_age_crc_sdr = max_age_crc_sdr

        v8 = (v8_min_age_crc - 45) + (v8_min_age_crc_fdr - 45) + (v8_min_age_crc_sdr - 45)

        # v9 = (minimum age of EC in the proband - 45) + (minimum age of EC in a FDR - 45) + (minimum age of EC in an SDR - 45)
        v9_min_age_ec = int(v9_MinAge_EC)
        v9_min_age_ec_fdr = int(v9_MinAge_EC_FDR)
        v9_min_age_ec_sdr = int(v9_MinAge_EC_SDR)

        if v3 == 0:
            v9_min_age_ec = 45

        if v6_ab == 0:
            v9_min_age_ec_fdr = 45

        if v6_cd == 0:
            v9_min_age_ec_sdr = 45

        min_age_ec = 31
        min_age_ec_fdr = 28
        min_age_ec_sdr = 34

        max_age_ec = 67
        max_age_ec_fdr = 69
        max_age_ec_sdr = 70

        # Check Min
        if v9_min_age_ec < min_age_ec:
            v9_min_age_ec = min_age_ec

        if v9_min_age_ec_fdr < min_age_ec_fdr:
            v9_min_age_ec_fdr = min_age_ec_fdr

        if v9_min_age_ec_sdr < min_age_ec_sdr:
            v9_min_age_ec_sdr = min_age_ec_sdr

        # Check Max
        if v9_min_age_ec > max_age_ec:
            v9_min_age_ec = max_age_ec

        if v9_min_age_ec_fdr > max_age_ec_fdr:
            v9_min_age_ec_fdr = max_age_ec_fdr

        if v9_min_age_ec_sdr > max_age_ec_sdr:
            v9_min_age_ec_sdr = max_age_ec_sdr

        v9 = (v9_min_age_ec - 45) + (v9_min_age_ec_fdr - 45) + (v9_min_age_ec_sdr - 45)

        # v10 = Current age, in years, of proband:
        # Minimum, 22
        # Maximum, 83
        # v10 = int(request.POST.get('v10'))
        v10 = age

        # Predicted probability of a mutation in MLH1: p(MLH1)
        # Predicted probability of a mutation in MSH2 or EPCAM: p(MSH2/EPCAM)
        # Predicted probability of a mutation in MSH6: p(MSH6)
        # Predicted probability of a mutation in PMS2: p(PMS2)
        # Predicted probability of no mutation: p(none)

        lp_pms2 = -4.913 + (0.294 * v0) + (0.989 * v1) + (-0.354 * v2) + (0.739 * v3) + (0.395 * v4) + (
                    -0.002 * v5) + (
                          -0.426 * v6) + (-0.105 * v7) + (-0.0086 * v8) + (0.0008 * v9) + (-0.0074 * v10)

        lp_msh6 = -4.675 + (0.816 * v0) + (1.265 * v1) + (-53.205 * v2) + (1.759 * v3) + (0.538 * v4) + (
                    0.545 * v5) + (
                          0.923 * v6) + (0.313 * v7) + (-0.0095 * v8) + (0.0344 * v9) + (-0.0363 * v10)

        lp_msh2_epcam = -4.427 + (0.937 * v0) + (1.799 * v1) + (2.593 * v2) + (1.924 * v3) + (1.585 * v4) + (
                    1.337 * v5) + (
                                0.670 * v6) + (0.607 * v7) + (-0.0441 * v8) + (0.0002 * v9) + (-0.0482 * v10)

        lp_mlh1 = -5.325 + (0.904 * v0) + (2.586 * v1) + (3.183 * v2) + (1.621 * v3) + (1.276 * v4) + (
                    1.560 * v5) + (
                          0.804 * v6) + (0.397 * v7) + (-0.0557 * v8) + (0.0115 * v9) + (-0.0476 * v10)

        p_pms2 = math.exp(lp_pms2) / (
                (1 + math.exp(lp_mlh1)) + math.exp(lp_msh2_epcam) + math.exp(lp_msh6) + math.exp(lp_pms2))

        p_msh6 = math.exp(lp_msh6) / (
                (1 + math.exp(lp_mlh1)) + math.exp(lp_msh2_epcam) + math.exp(lp_msh6) + math.exp(lp_pms2))

        p_msh2_epcam = math.exp(lp_msh2_epcam) / (
                (1 + math.exp(lp_mlh1)) + math.exp(lp_msh2_epcam) + math.exp(lp_msh6) + math.exp(lp_pms2))

        p_mlh1 = math.exp(lp_mlh1) / (
                (1 + math.exp(lp_mlh1)) + math.exp(lp_msh2_epcam) + math.exp(lp_msh6) + math.exp(lp_pms2))

        p_none = 1 - (p_mlh1 + p_msh2_epcam + p_msh6 + p_pms2)

        # Predicted probability of any mismatch repair gene mutation: p(any) = predicted probability of MLH1 mutation + predicted probability of MSH2/EPCAM mutation + predicted probability of MSH6 mutation + predicted probability of PMS2 mutation
        p_any = p_mlh1 + p_msh2_epcam + p_msh6 + p_pms2

        # gender = v0
        crc_history = v1
        crc2_history = v2
        ec_history = v3
        ls_history = v4
        crc_fdr = v5_ab
        crc_sdr = v5_cd
        ec_fdr = v6_ab
        ec_sdr = v6_cd
        ls_fdr = v7_e
        ls_sdr = v7_f
        min_age_crc = v8_min_age_crc
        min_age_crc_fdr = v8_min_age_crc_fdr
        min_age_crc_sdr = v8_min_age_crc_sdr
        min_age_ec = v9_min_age_ec
        min_age_ec_fdr = v9_min_age_ec_fdr
        min_age_ec_sdr = v9_min_age_ec_sdr
        # age = v10
        premm_score = round(p_any * 100, 1)

        crcpro_threshold = 1
        premm_threshold = 2.5


        results = ({
        "crc_history" : crc_history,
        "crc2_history" : crc2_history,
        "ec_history" : ec_history,
        "ls_history" : ls_history,
        "crc_fdr" : crc_fdr,
        "crc_sdr" : crc_sdr,
        "ec_fdr" : ec_fdr,
        "ec_sdr" : ec_sdr,
        "ls_fdr" : ls_fdr,
        "ls_sdr" : ls_sdr,
        "min_age_crc" : min_age_crc,
        "min_age_crc_fdr" : min_age_crc_fdr,
        "min_age_crc_sdr" : min_age_crc_sdr,
        "min_age_ec" : min_age_ec,
        "min_age_ec_fdr" : min_age_ec_fdr,
        "min_age_ec_sdr" : min_age_ec_sdr,
        "crcpro_score": crcpro_score,
        "crcpro_threshold": crcpro_threshold,
        "premm_score": premm_score,
        "premm_threshold": premm_threshold})


        print(f"crcpro_score:{crcpro_score}")
        print(f"crcpro_threshold:{crcpro_threshold}")
        print(f"premm_score:{premm_score}")
        print(f"premm_threshold:{premm_threshold}")

        return results