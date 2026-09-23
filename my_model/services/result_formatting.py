"""Format calculated scores for dashboard and screening JSON output."""


def build_result_context(selected_assessments, data):
    """Add display metadata to assessments and return the dashboard context."""
    # Build context for the results
    context = {}

    for item in selected_assessments:
        if item['title'] == 'Diabetes':
            idf_score = data.get('idf_score', 0)
            item['score'] = idf_score
            item['total_score'] = 30
            item['desc_file_fa'] = 'diabetes_fa.pdf'
            item['desc_file_en'] = 'diabetes_en.pdf'
            item['desc_file_ar'] = 'diabetes_ar.pdf'
            if 0 <= idf_score <= 6:
                item['status_en'] = 'Low Risk'
                item['status_fa'] = 'ریسک کم'
                item['status_ar'] = 'مخاطر منخفضة'
                item['color_class'] = 'bg-success'
                item[
                    'recommendation_en'] = 'Maintain healthy lifestyle: Balanced diet and 150 mins/week moderate exercise.'
                item['recommendation_fa'] = 'اصلاح سبک زندگی'
                item[
                    'recommendation_ar'] = 'الحفاظ على نمط حياة صحي: نظام غذائي متوازن و 150 دقيقة/أسبوع من التمارين المعتدلة.'
            elif 7 <= idf_score <= 11:
                item['status_en'] = 'Slightly Increased Risk'
                item['status_fa'] = 'ریسک تقریبا کم'
                item['status_ar'] = 'مخاطر متزايدة قليلاً'
                item['color_class'] = 'bg-info'
                item['recommendation_en'] = 'Lifestyle modification + annual glucose check. Consider HbA1c testing.'
                item['recommendation_fa'] = 'اصلاح سبک زندگی'
                item['recommendation_ar'] = 'تعديل نمط الحياة + فحص سنوي للجلوكوز. يُنظر في اختبار HbA1c.'
            elif 12 <= idf_score <= 14:
                item['status_en'] = 'Average Risk'
                item['status_fa'] = 'ریسک متوسط'
                item['status_ar'] = 'مخاطر متوسطة'
                item['color_class'] = 'bg-warning'
                item['recommendation_en'] = 'Medical consultation required. Monitor fasting glucose every 6 months.'
                item['recommendation_fa'] = 'بررسی و پیگیری توسط متخصص'
                item['recommendation_ar'] = 'استشارة طبية مطلوبة. مراقبة الجلوكوز الصائم كل 6 أشهر.'
            elif 15 <= idf_score <= 20:
                item['status_en'] = 'High Risk'
                item['status_fa'] = 'ریسک زیاد'
                item['status_ar'] = 'مخاطر عالية'
                item['color_class'] = 'bg-danger'
                item['recommendation_en'] = 'Urgent intervention: OGTT test + potential metformin therapy.'
                item['recommendation_fa'] = 'بررسی و پیگیری توسط متخصص'
                item['recommendation_ar'] = 'تدخل عاجل: اختبار OGTT + علاج محتمل بالميتفورمين.'
            else:
                item['status_en'] = 'Very High Risk'
                item['status_fa'] = 'ریسک خیلی زیاد'
                item['status_ar'] = 'مخاطر عالية جداً'
                item['color_class'] = 'bg-danger'
                item['recommendation_en'] = 'Immediate endocrinology referral. Start pharmacological prevention.'
                item['recommendation_fa'] = 'بررسی و پیگیری توسط متخصص'
                item['recommendation_ar'] = 'تحويل فوري إلى أخصائي الغدد الصماء. بدء الوقاية الدوائية.'

        elif item['title'] == 'Cardiovascular_Disease':
            ascvd_score = data.get('ascvd_score', 0)
            item['score'] = ascvd_score
            item['total_score'] = 30
            item['desc_file_fa'] = 'cvd_fa.pdf'
            item['desc_file_en'] = 'cvd_en.pdf'
            item['desc_file_ar'] = 'cvd_ar.pdf'
            if ascvd_score is None or ascvd_score == 0:
                item['status_en'] = 'Not supported'
                item['status_fa'] = 'بازه سنی پشتیبانی نمی شود'
                item['status_ar'] = 'غير مدعوم'
                item['color_class'] = 'bg-primary'
                item['recommendation_en'] = 'Age outside 40-79 range'
                item['recommendation_fa'] = 'محدوده سنی نامعتبر (۴۰-۷۹ سال)'
                item['recommendation_ar'] = 'العمر خارج النطاق 40-79 سنة'
            elif ascvd_score < 5:
                item['status_en'] = 'Low risk'
                item['status_fa'] = 'ریسک کم'
                item['status_ar'] = 'مخاطر منخفضة'
                item['color_class'] = 'bg-success'
                item['recommendation_en'] = 'Lifestyle prevention'
                item['recommendation_fa'] = 'اصلاح سبک زندگی'
                item['recommendation_ar'] = 'الوقاية بنمط الحياة'
            elif ascvd_score <= 7.4:
                item['status_en'] = 'Borderline risk'
                item['status_fa'] = 'ریسک کم-متوسط'
                item['status_ar'] = 'مخاطر حدية'
                item['color_class'] = 'bg-info'
                item['recommendation_en'] = 'LDL management + lifestyle'
                item['recommendation_fa'] = 'اصلاح سبک زندگی'
                item['recommendation_ar'] = 'إدارة LDL + نمط الحياة'
            elif ascvd_score < 19.9:
                item['status_en'] = 'Intermediate risk'
                item['status_fa'] = 'ریسک متوسط'
                item['status_ar'] = 'مخاطر متوسطة'
                item['color_class'] = 'bg-warning'
                item['recommendation_en'] = 'Moderate statins + risk factor control'
                item['recommendation_fa'] = 'بررسی و پیگیری توسط متخصص'
                item['recommendation_ar'] = 'ستاتينات معتدلة + التحكم في عوامل الخطر'
            else:
                item['status_en'] = 'High risk'
                item['status_fa'] = 'ریسک زیاد'
                item['status_ar'] = 'مخاطر عالية'
                item['color_class'] = 'bg-danger'
                item['recommendation_en'] = 'Aggressive lipid-lowering therapy'
                item['recommendation_fa'] = 'بررسی و پیگیری توسط متخصص'
                item['recommendation_ar'] = 'علاج مكثف لخفض الدهون'

        elif item['title'] == 'Breast_Cancer':
            mymodel_gail_score = data.get('mymodel_gail_score', 0)
            item['score'] = mymodel_gail_score
            item['total_score'] = 10
            item['desc_file_fa'] = 'breast_cancer_fa.pdf'
            item['desc_file_en'] = 'breast_cancer_en.pdf'
            item['desc_file_ar'] = 'breast_cancer_ar.pdf'
            if mymodel_gail_score >= 1.7:
                item['status_en'] = 'Intermediate Risk'
                item['status_fa'] = 'ریسک متوسط-بالا'
                item['status_ar'] = 'مخاطر متوسطة-عالية'
                item['color_class'] = 'bg-warning'
                item['recommendation_en'] = 'May need additional tests (e.g., MRI)'
                item['recommendation_fa'] = 'بررسی و پیگیری توسط متخصص'
                item['recommendation_ar'] = 'قد تحتاج إلى اختبارات إضافية (مثل التصوير بالرنين المغناطيسي)'
            else:
                item['status_en'] = 'Low Risk'
                item['status_fa'] = 'ریسک کم'
                item['status_ar'] = 'مخاطر منخفضة'
                item['color_class'] = 'bg-success'
                item['recommendation_en'] = 'Routine screening'
                item['recommendation_fa'] = 'اصلاح سبک زندگی'
                item['recommendation_ar'] = 'الفحص الروتيني'

        elif item['title'] == 'Colorectal_Cancer':
            premm_score = data.get('premm_score', 0)
            item['score'] = premm_score
            item['total_score'] = 5
            item['desc_file_fa'] = 'colon_cancer_fa.pdf'
            item['desc_file_en'] = 'colon_cancer_en.pdf'
            item['desc_file_ar'] = 'colon_cancer_ar.pdf'
            if premm_score >= 2.5:
                item['status_en'] = 'High Risk'
                item['status_fa'] = 'ریسک متوسط-بالا'
                item['status_ar'] = 'مخاطر عالية'
                item['color_class'] = 'bg-danger'
                item['recommendation_en'] = 'Referral for genetic evaluation is recommended.'
                item['recommendation_fa'] = 'بررسی و پیگیری توسط متخصص'
                item['recommendation_ar'] = 'يوصى بالتحويل للتقييم الجيني.'
            else:
                item['status_en'] = 'Low Risk'
                item['status_fa'] = 'ریسک کم'
                item['status_ar'] = 'مخاطر منخفضة'
                item['color_class'] = 'bg-success'
                item[
                    'recommendation_en'] = 'Follow average-risk guidelines (colonoscopy every 10 years starting at age 50).'
                item['recommendation_fa'] = 'اصلاح سبک زندگی'
                item[
                    'recommendation_ar'] = 'اتباع إرشادات المخاطر المتوسطة (تنظير القولون كل 10 سنوات ابتداءً من سن 50).'

        elif item['title'] == 'Cervical_Cancer':
            cervical_cancer_score = data.get('cervical_cancer_score', 1)
            item['score'] = cervical_cancer_score
            item['total_score'] = 3
            item['desc_file_fa'] = 'cervical_cancer_fa.pdf'
            item['desc_file_en'] = 'cervical_cancer_en.pdf'
            item['desc_file_ar'] = 'cervical_cancer_ar.pdf'
            if cervical_cancer_score == 3:
                item['status_en'] = 'High Risk'
                item['status_fa'] = 'ریسک زیاد'
                item['status_ar'] = 'مخاطر عالية'
                item['color_class'] = 'bg-danger'
                item['recommendation_en'] = 'Immediate colposcopy and possible biopsy required'
                item['recommendation_fa'] = 'بررسی و پیگیری توسط متخصص'
                item['recommendation_ar'] = 'تنظير المهبل فوري وخزعة محتملة مطلوبة'
            elif cervical_cancer_score == 2:
                item['status_en'] = 'Intermediate Risk'
                item['status_fa'] = 'ریسک متوسط'
                item['status_ar'] = 'مخاطر متوسطة'
                item['color_class'] = 'bg-warning'
                item['recommendation_en'] = 'Repeat testing in 6-12 months or colposcopy referral'
                item['recommendation_fa'] = 'بررسی و پیگیری توسط متخصص'
                item['recommendation_ar'] = 'إعادة الاختبار خلال 6-12 شهراً أو التحويل لتنظير المهبل'
            else:
                item['status_en'] = 'Low Risk'
                item['status_fa'] = 'ریسک کم'
                item['status_ar'] = 'مخاطر منخفضة'
                item['color_class'] = 'bg-success'
                item[
                    'recommendation_en'] = 'Follow routine screening per national guidelines (e.g., Pap every 3-5 years)'
                item['recommendation_fa'] = 'اصلاح سبک زندگی'
                item[
                    'recommendation_ar'] = 'اتباع الفحص الروتيني وفقاً للإرشادات الوطنية (مثل مسحة عنق الرحم كل 3-5 سنوات)'

        elif item['title'] == 'Prostate_Cancer':
            pbcg_score_high_cancer = data.get('pbcg_score_high_cancer', 0)
            item['score'] = pbcg_score_high_cancer
            item['total_score'] = 60
            item['desc_file_fa'] = 'prostate_cancer_fa.pdf'
            item['desc_file_en'] = 'prostate_cancer_en.pdf'
            item['desc_file_ar'] = 'prostate_cancer_ar.pdf'
            if pbcg_score_high_cancer >= 40:
                item['status_en'] = 'High risk (PBCG)'
                item['status_fa'] = 'ریسک بالا (PBCG)'
                item['status_ar'] = 'مخاطر عالية (PBCG)'
                item['recommendation_en'] = "Urgent urology referral and biopsy strongly recommended"
                item['recommendation_fa'] = "بررسی و پیگیری توسط متخصص"
                item['recommendation_ar'] = "تحويل فوري لجراحة المسالك البولية وخزعة موصى بها بشدة"
                item['color_class'] = 'bg-danger'
            elif pbcg_score_high_cancer >= 20:
                item['status_en'] = 'Intermediate risk (PBCG)'
                item['status_fa'] = 'ریسک متوسط (PBCG)'
                item['status_ar'] = 'مخاطر متوسطة (PBCG)'
                item['recommendation_en'] = "Consider prostate biopsy or multiparametric MRI"
                item['recommendation_fa'] = "بررسی و پیگیری توسط متخصص"
                item['recommendation_ar'] = "النظر في خزعة البروستاتا أو التصوير بالرنين المغناطيسي متعدد المعايير"
                item['color_class'] = 'bg-warning'
            else:
                item['status_en'] = 'Low-grade risk (PBCG)'
                item['status_fa'] = 'ریسک درجه پایین (PBCG)'
                item['status_ar'] = 'مخاطر منخفضة الدرجة (PBCG)'
                item['recommendation_en'] = "Active surveillance or MRI-targeted biopsy"
                item['recommendation_fa'] = "اصلاح سبک زندگی"
                item['recommendation_ar'] = "المراقبة النشطة أو الخزعة الموجهة بالرنين المغناطيسي"
                item['color_class'] = 'bg-info'

        elif item['title'] == 'Melanoma_Cancer':
            melanoma_cancer_score = data.get('melanoma_cancer_score', 0)
            item['score'] = melanoma_cancer_score
            item['total_score'] = 22
            item['desc_file_fa'] = 'melanoma_fa.pdf'
            item['desc_file_en'] = 'melanoma_en.pdf'
            item['desc_file_ar'] = 'melanoma_ar.pdf'
            if melanoma_cancer_score >= 15:
                item['status_en'] = 'High Risk'
                item['status_fa'] = 'ریسک زیاد'
                item['status_ar'] = 'مخاطر عالية'
                item['color_class'] = 'bg-danger'
                item['recommendation_en'] = 'Consult dermatologist immediately'
                item['recommendation_fa'] = 'بررسی و پیگیری توسط متخصص'
                item['recommendation_ar'] = 'استشارة و متابعة من قبل أخصائي'
            elif melanoma_cancer_score >= 8:
                item['status_en'] = 'Moderate Risk'
                item['status_fa'] = 'ریسک متوسط'
                item['status_ar'] = 'مخاطر متوسطة'
                item['color_class'] = 'bg-warning'
                item['recommendation_en'] = 'Regular skin checks recommended'
                item['recommendation_fa'] = 'بررسی و پیگیری توسط متخصص'
                item['recommendation_ar'] = 'استشارة و متابعة من قبل أخصائي'
            else:
                item['status_en'] = 'Low Risk'
                item['status_fa'] = 'ریسک کم'
                item['status_ar'] = 'مخاطر منخفضة'
                item['color_class'] = 'bg-success'
                item['recommendation_en'] = 'Sun protection and regular self-examination'
                item['recommendation_fa'] = 'اصلاح سبک زندگی'
                item['recommendation_ar'] = 'تحسين نمط الحياة'

        elif item['title'] == 'Osteoporosis':
            osteoporosis_score = data.get('osteoporosis_score', 0)
            item['score'] = osteoporosis_score
            item['total_score'] = 60
            item['desc_file_fa'] = 'osteoporosis_fa.pdf'
            item['desc_file_en'] = 'osteoporosis_en.pdf'
            item['desc_file_ar'] = 'osteoporosis_ar.pdf'
            if osteoporosis_score > 40:
                item['status_en'] = 'High Risk'
                item['status_fa'] = 'ریسک زیاد'
                item['status_ar'] = 'مخاطر عالية'
                item['color_class'] = 'bg-danger'
                item['recommendation_en'] = 'DEXA scan and calcium/vitamin D supplementation recommended'
                item['recommendation_fa'] = 'بررسی و پیگیری توسط متخصص'
                item['recommendation_ar'] = 'استشارة و متابعة من قبل أخصائي'
            elif osteoporosis_score > 20:
                item['status_en'] = 'Moderate Risk'
                item['status_fa'] = 'ریسک متوسط'
                item['status_ar'] = 'مخاطر متوسطة'
                item['color_class'] = 'bg-warning'
                item['recommendation_en'] = 'Lifestyle modifications and calcium intake review'
                item['recommendation_fa'] = 'بررسی و پیگیری توسط متخصص'
                item['recommendation_ar'] = 'استشارة و متابعة من قبل أخصائي'
            else:
                item['status_en'] = 'Low Risk'
                item['status_fa'] = 'ریسک کم'
                item['status_ar'] = 'مخاطر منخفضة'
                item['color_class'] = 'bg-success'
                item['recommendation_en'] = 'Maintain healthy lifestyle with adequate calcium and vitamin D'
                item['recommendation_fa'] = 'اصلاح سبک زندگی'
                item['recommendation_ar'] = 'تحسين نمط الحياة'

        if item['title'] == 'Ovarian_Cancer':
            ovarian_cancer_score = data.get('ovarian_cancer_score', 0)
            item['score'] = ovarian_cancer_score
            item['total_score'] = 38
            item['desc_file_fa'] = 'ovarian_cancer_fa.pdf'
            item['desc_file_en'] = 'ovarian_cancer_en.pdf'
            item['desc_file_ar'] = 'ovarian_cancer_ar.pdf'
            if ovarian_cancer_score >= 20:
                item['status_en'] = 'High Risk'
                item['status_fa'] = 'ریسک زیاد'
                item['status_ar'] = 'مخاطر عالية'
                item['color_class'] = 'bg-danger'
                item['recommendation_en'] = ''
                item['recommendation_fa'] = 'بررسی و پیگیری توسط متخصص'
                item['recommendation_ar'] = 'استشارة و متابعة من قبل أخصائي'
            elif ovarian_cancer_score >= 10:
                item['status_en'] = 'Moderate Risk'
                item['status_fa'] = 'ریسک متوسط'
                item['status_ar'] = 'مخاطر متوسطة'
                item['color_class'] = 'bg-warning'
                item['recommendation_en'] = ''
                item['recommendation_fa'] = 'بررسی و پیگیری توسط متخصص'
                item['recommendation_ar'] = 'استشارة و متابعة من قبل أخصائي'
            else:
                item['status_en'] = 'Low Risk'
                item['status_fa'] = 'ریسک کم'
                item['status_ar'] = 'مخاطر منخفضة'
                item['color_class'] = 'bg-success'
                item['recommendation_en'] = ''
                item['recommendation_fa'] = 'اصلاح سبک زندگی'
                item['recommendation_ar'] = 'تحسين نمط الحياة'

        if item['title'] == 'Pancreatic_Cancer':
            pancreatic_cancer_score = data.get('pancreatic_cancer_score', 0)
            item['score'] = pancreatic_cancer_score
            item['total_score'] = 36
            item['desc_file_fa'] = 'pancreatic_cancer_fa.pdf'
            item['desc_file_en'] = 'pancreatic_cancer_en.pdf'
            item['desc_file_ar'] = 'pancreatic_cancer_ar.pdf'
            if pancreatic_cancer_score >= 24:
                item['status_en'] = 'High Risk'
                item['status_fa'] = 'ریسک زیاد'
                item['status_ar'] = 'مخاطر عالية'
                item['color_class'] = 'bg-danger'
                item['recommendation_en'] = ''
                item['recommendation_fa'] = 'بررسی و پیگیری توسط متخصص'
                item['recommendation_ar'] = 'استشارة و متابعة من قبل أخصائي'
            elif pancreatic_cancer_score >= 12:
                item['status_en'] = 'Moderate Risk'
                item['status_fa'] = 'ریسک متوسط'
                item['status_ar'] = 'مخاطر متوسطة'
                item['color_class'] = 'bg-warning'
                item['recommendation_en'] = ''
                item['recommendation_fa'] = 'بررسی و پیگیری توسط متخصص'
                item['recommendation_ar'] = 'استشارة و متابعة من قبل أخصائي'
            else:
                item['status_en'] = 'Low Risk'
                item['status_fa'] = 'ریسک کم'
                item['status_ar'] = 'مخاطر منخفضة'
                item['color_class'] = 'bg-success'
                item['recommendation_en'] = ''
                item['recommendation_fa'] = 'اصلاح سبک زندگی'
                item['recommendation_ar'] = 'تحسين نمط الحياة'

        if item['title'] == 'Stomach_Cancer':
            stomach_cancer_score = data.get('stomach_cancer_score', 0)
            item['score'] = stomach_cancer_score
            item['total_score'] = 30
            item['desc_file_fa'] = 'stomach_cancer_fa.pdf'
            item['desc_file_en'] = 'stomach_cancer_en.pdf'
            item['desc_file_ar'] = 'stomach_cancer_ar.pdf'
            if stomach_cancer_score >= 20:
                item['status_en'] = 'High Risk'
                item['status_fa'] = 'ریسک زیاد'
                item['status_ar'] = 'مخاطر عالية'
                item['color_class'] = 'bg-danger'
                item['recommendation_en'] = ''
                item['recommendation_fa'] = 'بررسی و پیگیری توسط متخصص'
                item['recommendation_ar'] = 'استشارة و متابعة من قبل أخصائي'
            elif stomach_cancer_score >= 10:
                item['status_en'] = 'Moderate Risk'
                item['status_fa'] = 'ریسک متوسط'
                item['status_ar'] = 'مخاطر متوسطة'
                item['color_class'] = 'bg-warning'
                item['recommendation_en'] = ''
                item['recommendation_fa'] = 'بررسی و پیگیری توسط متخصص'
                item['recommendation_ar'] = 'استشارة و متابعة من قبل أخصائي'
            else:
                item['status_en'] = 'Low Risk'
                item['status_fa'] = 'ریسک کم'
                item['status_ar'] = 'مخاطر منخفضة'
                item['color_class'] = 'bg-success'
                item['recommendation_en'] = ''
                item['recommendation_fa'] = 'اصلاح سبک زندگی'
                item['recommendation_ar'] = 'تحسين نمط الحياة'

        if item['title'] == 'Stroke':
            stroke_score = data.get('stroke_score', 0)
            item['score'] = stroke_score
            item['total_score'] = 30
            item['desc_file_fa'] = 'stroke_fa.pdf'
            item['desc_file_en'] = 'stroke_en.pdf'
            item['desc_file_ar'] = 'stroke_ar.pdf'
            if stroke_score >= 20:
                item['status_en'] = 'High Risk'
                item['status_fa'] = 'ریسک زیاد'
                item['status_ar'] = 'مخاطر عالية'
                item['color_class'] = 'bg-danger'
                item['recommendation_en'] = ''
                item['recommendation_fa'] = 'بررسی و پیگیری توسط متخصص'
                item['recommendation_ar'] = 'استشارة و متابعة من قبل أخصائي'
            elif stroke_score >= 10:
                item['status_en'] = 'Moderate Risk'
                item['status_fa'] = 'ریسک متوسط'
                item['status_ar'] = 'مخاطر متوسطة'
                item['color_class'] = 'bg-warning'
                item['recommendation_en'] = ''
                item['recommendation_fa'] = 'بررسی و پیگیری توسط متخصص'
                item['recommendation_ar'] = 'استشارة و متابعة من قبل أخصائي'
            else:
                item['status_en'] = 'Low Risk'
                item['status_fa'] = 'ریسک کم'
                item['status_ar'] = 'مخاطر منخفضة'
                item['color_class'] = 'bg-success'
                item['recommendation_en'] = ''
                item['recommendation_fa'] = 'اصلاح سبک زندگی'
                item['recommendation_ar'] = 'تحسين نمط الحياة'

    return context
