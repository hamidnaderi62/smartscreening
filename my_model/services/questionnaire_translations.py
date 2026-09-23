"""Shared question and answer translations used by the questionnaire and PDFs.

Screening records store the stable field name (``question_key``) and the raw
answer.  Human-readable text is resolved when a report is rendered so one
record can safely produce Persian, English, or Arabic output.
"""

from .localization import normalize_language


def _labels(en, fa, ar):
    return {'en': en, 'fa': fa, 'ar': ar}


QUESTION_LABELS = {
    'age': _labels('Age (years)', 'سن (سال)', 'العمر (بالسنوات)'),
    'weight': _labels('Weight (kg)', 'وزن (کیلوگرم)', 'الوزن (كجم)'),
    'height': _labels('Height (cm)', 'قد (سانتی‌متر)', 'الطول (سم)'),
    'waist_size': _labels('Waist circumference (cm)', 'اندازه دور کمر (سانتی‌متر)', 'محيط الخصر (سم)'),
    'education': _labels('Education level (years)', 'سطح تحصیلات (سال)', 'المستوى التعليمي (بالسنوات)'),
    'born_place': _labels('Place of birth', 'محل تولد', 'مكان الميلاد'),
    'ethnicity': _labels('Ethnicity', 'قومیت', 'العرق'),
    'blood_group': _labels('Blood group', 'گروه خونی', 'فصيلة الدم'),
    'activity': _labels('Average daily physical activity (hours/day)', 'میانگین فعالیت بدنی روزانه (ساعت در روز)', 'متوسط النشاط البدني اليومي (ساعة/اليوم)'),
    'smoking': _labels('Number of cigarette packs per year', 'تعداد بسته سیگار در سال', 'عدد علب السجائر في السنة'),
    'alcohol': _labels('Average alcohol consumption (shots/day)', 'میانگین مصرف الکل (شات در روز)', 'متوسط استهلاك الكحول (كأس/اليوم)'),
    'meat': _labels('Average daily red meat consumption (grams/day)', 'میانگین مصرف روزانه گوشت قرمز (گرم در روز)', 'متوسط استهلاك اللحوم الحمراء (غرام/اليوم)'),
    'cereal': _labels('Eat fortified breakfast cereals most days', 'بیشتر روزها غلات صبحانه غنی‌شده می‌خورید', 'تناول حبوب الإفطار المدعمة معظم الأيام'),
    'vegetables': _labels('Frequency of fruit and vegetable consumption', 'دفعات مصرف میوه و سبزیجات', 'عدد مرات تناول الفواكه والخضروات'),
    'dairy': _labels('Servings of milk or dairy products per day', 'تعداد وعده‌های شیر یا لبنیات در روز', 'عدد حصص الحليب أو منتجات الألبان يومياً'),
    'multivitamin': _labels('Regular use of multivitamins', 'مصرف منظم مولتی‌ویتامین', 'الاستخدام المنتظم للفيتامينات المتعددة'),
    'blood_pressure': _labels('Ever taken medication for high blood pressure', 'سابقه مصرف دارو برای فشار خون بالا', 'هل سبق تناول دواء لارتفاع ضغط الدم'),
    'blood_glucose': _labels('Ever told you have high blood sugar', 'سابقه اعلام قند خون بالا', 'هل سبق إخبارك بارتفاع سكر الدم'),
    'totchol': _labels('Total cholesterol level (mg/dL)', 'سطح کلسترول خون (mg/dL)', 'مستوى الكوليسترول الكلي (مجم/ديسيلتر)'),
    'previous_cancer': _labels('History of cancer', 'سابقه سرطان', 'تاريخ الإصابة بالسرطان'),
    'relatives_diabetes': _labels('Family member diagnosed with diabetes', 'ابتلای یکی از اعضای خانواده به دیابت', 'إصابة أحد أفراد العائلة بالسكري'),
    'idf_score': _labels('Diabetes Risk Score', 'امتیاز خطر دیابت', 'درجة خطر السكري'),
    'ausdrisk_score': _labels('AUSDRISK Score', 'امتیاز AUSDRISK', 'درجة AUSDRISK'),
    'uk_score': _labels('UK Diabetes Risk Score', 'امتیاز خطر دیابت انگلستان', 'درجة خطر السكري في المملكة المتحدة'),
    'ada_score': _labels('ADA Diabetes Risk Score', 'امتیاز خطر دیابت ADA', 'درجة خطر السكري حسب ADA'),
    'biopsy': _labels('Ever had a breast biopsy with benign diagnosis', 'سابقه نمونه‌برداری خوش‌خیم پستان', 'خزعة ثدي سابقة بتشخيص حميد'),
    'biopsy_num': _labels('Number of breast biopsies with benign diagnosis', 'تعداد نمونه‌برداری‌های خوش‌خیم پستان', 'عدد خزعات الثدي ذات التشخيص الحميد'),
    'hyperplasia_biopsy': _labels('Ever had a breast biopsy with atypical hyperplasia', 'سابقه نمونه‌برداری پستان با هیپرپلازی غیرطبیعی', 'خزعة ثدي سابقة مع فرط تنسج غير نمطي'),
    'menstruation_age': _labels('Age at first menstruation', 'سن اولین قاعدگی', 'العمر عند أول دورة شهرية'),
    'child_age': _labels('Age at first childbirth', 'سن هنگام تولد اولین فرزند', 'العمر عند ولادة الطفل الأول'),
    'fdr_cancer': _labels('First-degree relatives with breast cancer', 'سابقه سرطان پستان در بستگان درجه اول', 'إصابة الأقارب من الدرجة الأولى بسرطان الثدي'),
    'breastfeeding': _labels('Breastfeeding history', 'سابقه شیردهی', 'تاريخ الرضاعة الطبيعية'),
    'cbe': _labels('Clinical breast examination', 'معاینه بالینی پستان', 'الفحص السريري للثدي'),
    'bse': _labels('Breast self-examination', 'معاینه شخصی پستان', 'الفحص الذاتي للثدي'),
    'mammograms': _labels('Mammogram results', 'نتیجه ماموگرافی', 'نتائج تصوير الثدي الشعاعي'),
    'syndrome': _labels('Li-Fraumeni, Cowden, or Bannayan-Riley-Ruvalcaba syndrome', 'سندروم لی-فرامنی، کاودن یا بنایان-رایلی-رواکلابا', 'متلازمة لي-فروميني أو كاودن أو بانايان-رايلي-روفالكابا'),
    'gene_mutation': _labels('Known BRCA1 or BRCA2 gene mutation', 'جهش شناخته‌شده ژن BRCA1 یا BRCA2', 'طفرة معروفة في جين BRCA1 أو BRCA2'),
    'gail_score': _labels('Gail Model Risk Score', 'امتیاز خطر مدل گیل', 'درجة الخطورة حسب نموذج غيل'),
    'sbp': _labels('Systolic blood pressure (mm Hg)', 'فشار خون سیستولیک (mm Hg)', 'ضغط الدم الانقباضي (ملم زئبق)'),
    'hdl': _labels('HDL cholesterol level (mg/dL)', 'سطح کلسترول HDL (mg/dL)', 'مستوى كوليسترول HDL (مجم/ديسيلتر)'),
    'ascvd_score': _labels('ASCVD Risk Score (10-year)', 'امتیاز خطر ASCVD (۱۰ ساله)', 'درجة خطر ASCVD (10 سنوات)'),
    'psa': _labels('PSA blood test result (ng/mL)', 'نتیجه آزمایش PSA (ng/mL)', 'نتيجة فحص PSA (نانوغرام/مل)'),
    'famhistory': _labels('Family history of prostate cancer', 'سابقه خانوادگی سرطان پروستات', 'تاريخ عائلي لسرطان البروستاتا'),
    'dre': _labels('Digital rectal exam (DRE) result', 'نتیجه معاینه انگشتی رکتوم (DRE)', 'نتيجة الفحص الشرجي الرقمي (DRE)'),
    'priorbiopsy': _labels('Prior biopsy history', 'سابقه نمونه‌برداری قبلی', 'تاريخ الخزعة السابقة'),
    'pbcg_no_cancer': _labels('PBCG No Cancer Risk (%)', 'خطر عدم وجود سرطان طبق PBCG (٪)', 'خطر عدم وجود السرطان حسب PBCG (%)'),
    'pbcg_low_cancer': _labels('PBCG Low-Grade Cancer Risk (%)', 'خطر سرطان کم‌درجه طبق PBCG (٪)', 'خطر السرطان منخفض الدرجة حسب PBCG (%)'),
    'pbcg_high_cancer': _labels('PBCG High-Grade Cancer Risk (%)', 'خطر سرطان پر‌درجه طبق PBCG (٪)', 'خطر السرطان عالي الدرجة حسب PBCG (%)'),
    'num_sexual_partners': _labels('Number of sexual partners', 'تعداد شرکای جنسی', 'عدد الشركاء الجنسيين'),
    'first_sexual_intercourse': _labels('Age at first sexual intercourse', 'سن اولین رابطه جنسی', 'العمر عند أول علاقة جنسية'),
    'num_pregnancies': _labels('Number of pregnancies', 'تعداد بارداری‌ها', 'عدد مرات الحمل'),
    'hormonal_contraceptives_years': _labels('Years using hormonal contraceptives', 'تعداد سال مصرف داروهای ضدبارداری هورمونی', 'عدد سنوات استخدام موانع الحمل الهرمونية'),
    'iud': _labels('Years using IUD', 'تعداد سال استفاده از IUD', 'عدد سنوات استخدام اللولب'),
    'std': _labels('History of STD', 'سابقه بیماری مقاربتی', 'تاريخ الأمراض المنقولة جنسياً'),
    'cervical_cancer': _labels('Family history of cervical cancer', 'سابقه خانوادگی سرطان دهانه رحم', 'تاريخ عائلي لسرطان عنق الرحم'),
    'cytology': _labels('Cytology result', 'نتیجه سیتولوژی', 'نتيجة فحص الخلايا'),
    'cin': _labels('Pathology result (CIN grade)', 'نتیجه آسیب‌شناسی (درجه CIN)', 'نتيجة علم الأمراض (درجة CIN)'),
    'hpv': _labels('HPV test result', 'نتیجه آزمایش HPV', 'نتيجة فحص HPV'),
    'cervical_cancer_score': _labels('Cervical Cancer Risk Score', 'امتیاز خطر سرطان دهانه رحم', 'درجة خطر سرطان عنق الرحم'),
    'family_crc': _labels('Family history of colorectal cancer', 'سابقه خانوادگی سرطان روده بزرگ', 'تاريخ عائلي لسرطان القولون والمستقيم'),
    'diabetes': _labels('History of diabetes', 'سابقه دیابت', 'تاريخ الإصابة بالسكري'),
    'aspirin': _labels('Aspirin/Estrogen use', 'مصرف آسپرین/استروژن', 'استخدام الأسبرين/الإستروجين'),
    'estrogen': _labels('Estrogen use', 'مصرف استروژن', 'استخدام الإستروجين'),
    'painmed': _labels('Regular use of NSAIDs', 'مصرف منظم داروهای ضدالتهاب غیراستروئیدی', 'الاستخدام المنتظم لمضادات الالتهاب غير الستيرويدية'),
    'premm_score': _labels('PREMM Lynch Syndrome Risk Score (%)', 'امتیاز خطر سندروم لینچ PREMM (٪)', 'درجة خطر متلازمة لينش PREMM (%)'),
    'crcpro_score': _labels('CRCPro Risk Score (%)', 'امتیاز خطر CRCPro (٪)', 'درجة خطر CRCPro (%)'),
    'family_melanoma_cancer': _labels('History of skin cancer in siblings and parents', 'سابقه سرطان پوست در خواهر، برادر یا والدین', 'تاريخ سرطان الجلد لدى الأشقاء أو الوالدين'),
    'colored_hair': _labels('Naturally blonde or red hair', 'موهای طبیعی بلوند یا قرمز', 'شعر أشقر أو أحمر طبيعي'),
    'colored_eyes': _labels('Naturally blue, green, or hazel eyes', 'چشم‌های طبیعی آبی، سبز یا عسلی', 'عيون زرقاء أو خضراء أو عسلية طبيعية'),
    'fair_skin': _labels('Fair skin', 'پوست روشن', 'بشرة فاتحة'),
    'moles_count': _labels('Number of moles on arms (≥3mm)', 'تعداد خال‌های روی بازو (≥۳ میلی‌متر)', 'عدد الشامات على الذراعين (≥3 مم)'),
    'sunburns': _labels('Severe and frequent sunburns in childhood', 'آفتاب‌سوختگی شدید و مکرر در کودکی', 'حروق شمس شديدة ومتكررة في الطفولة'),
    'sunlamp': _labels('Ever used tanning bed or sunlamp', 'سابقه استفاده از تخت برنزه یا لامپ آفتاب', 'استخدام سرير تسمير أو مصباح شمسي سابقاً'),
    'immunosuppressive_drugs': _labels('Ever taken immunosuppressive drugs', 'سابقه مصرف داروهای سرکوب‌کننده ایمنی', 'استخدام أدوية مثبطة للمناعة سابقاً'),
    'melanoma_score': _labels('Melanoma Cancer Risk Score', 'امتیاز خطر ملانوما', 'درجة خطر سرطان الجلد الميلانيني'),
    'rheumatoid_arthritis': _labels('Ever told you have rheumatoid arthritis', 'سابقه ابتلا به روماتیسم مفصلی', 'هل سبق إخبارك بإصابتك بالتهاب المفاصل الروماتويدي'),
    'have_bmd_test': _labels('Ever had a bone mineral density test', 'سابقه آزمایش تراکم مواد معدنی استخوان', 'إجراء فحص كثافة المعادن في العظام سابقاً'),
    'result_bmd_test': _labels('Last BMD test result', 'نتیجه آخرین آزمایش تراکم استخوان', 'نتيجة آخر فحص لكثافة العظام'),
    'chemotherapy': _labels('Ever undergone chemotherapy for cancer', 'سابقه شیمی‌درمانی برای سرطان', 'الخضوع للعلاج الكيميائي للسرطان سابقاً'),
    'steroid': _labels('Taking steroid pills for 3+ consecutive months', 'مصرف قرص استروئیدی برای حداقل ۳ ماه متوالی', 'تناول حبوب الستيرويد لمدة 3 أشهر متتالية أو أكثر'),
    'anticonvulsants': _labels('Use of anticonvulsant medications', 'مصرف داروهای ضدتشنج', 'استخدام أدوية مضادة للتشنجات'),
    'calcium_supplements': _labels('Take calcium supplements most days', 'مصرف مکمل کلسیم در بیشتر روزها', 'تناول مكملات الكالسيوم معظم الأيام'),
    'vitamin_d': _labels('Take vitamin D supplement most days', 'مصرف مکمل ویتامین D در بیشتر روزها', 'تناول مكمل فيتامين د معظم الأيام'),
    'family_break_bone': _labels('Mother or father broke bone after age 50', 'شکستگی استخوان مادر یا پدر پس از ۵۰ سالگی', 'كسر عظم لدى الأم أو الأب بعد سن 50'),
    'osteoporosis_score': _labels('Osteoporosis Risk Score', 'امتیاز خطر پوکی استخوان', 'درجة خطر هشاشة العظام'),
    'family_breast_ovarian_prostate': _labels('Multiple family members with breast, ovarian, or prostate cancer', 'ابتلای چند عضو خانواده به سرطان پستان، تخمدان یا پروستات', 'إصابة عدة أفراد من العائلة بسرطان الثدي أو المبيض أو البروستاتا'),
    'family_ovarian_cancer': _labels('Mother or sister with ovarian cancer', 'ابتلای مادر یا خواهر به سرطان تخمدان', 'إصابة الأم أو الأخت بسرطان المبيض'),
    'talcum_powder': _labels('Regular use of talcum powder', 'مصرف منظم پودر تالک', 'الاستخدام المنتظم لمسحوق التلك'),
    'menopause': _labels('Early menopause', 'یائسگی زودرس', 'انقطاع الطمث المبكر'),
    'menopause_hormone': _labels('Duration of menopausal hormone therapy', 'مدت درمان هورمونی یائسگی', 'مدة العلاج الهرموني لانقطاع الطمث'),
    'hysterectomy': _labels('Hysterectomy (removal of uterus)', 'هیسترکتومی (برداشتن رحم)', 'استئصال الرحم'),
    'endometriosis': _labels('History of endometriosis', 'سابقه اندومتریوز', 'تاريخ بطانة الرحم المهاجرة'),
    'salpingectomy': _labels('Tubal ligation or salpingectomy', 'بستن لوله‌های رحمی یا سالپنژکتومی', 'ربط الأنابيب أو استئصال قناة فالوب'),
    'ovarian_score': _labels('Ovarian Cancer Risk Score', 'امتیاز خطر سرطان تخمدان', 'درجة خطر سرطان المبيض'),
    'family_pancreatic_cancer': _labels('Brother, sister, or parent with pancreatic cancer', 'ابتلای خواهر، برادر یا والدین به سرطان لوزالمعده', 'إصابة الأخ أو الأخت أو أحد الوالدين بسرطان البنكرياس'),
    'chronic_pancreatitis': _labels('History of chronic pancreatitis', 'سابقه پانکراتیت مزمن', 'تاريخ التهاب البنكرياس المزمن'),
    'pancreatic_score': _labels('Pancreatic Cancer Risk Score', 'امتیاز خطر سرطان لوزالمعده', 'درجة خطر سرطان البنكرياس'),
    'family_stomach_cancer': _labels('Brother, sister, or parent with stomach cancer', 'ابتلای خواهر، برادر یا والدین به سرطان معده', 'إصابة الأخ أو الأخت أو أحد الوالدين بسرطان المعدة'),
    'fastfood': _labels('Meals per week at restaurant/fast food', 'تعداد وعده‌های رستوران/فست‌فود در هفته', 'عدد وجبات المطاعم/الوجبات السريعة أسبوعياً'),
    'cannedfood': _labels('Frequency of canned/processed foods', 'دفعات مصرف غذاهای کنسروی/فرآوری‌شده', 'وتيرة تناول الأطعمة المعلبة/المصنعة'),
    'h_pylori': _labels('History of H. pylori infection', 'سابقه عفونت هلیکوباکتر پیلوری', 'تاريخ الإصابة بعدوى الملوية البوابية'),
    'stomach_score': _labels('Stomach Cancer Risk Score', 'امتیاز خطر سرطان معده', 'درجة خطر سرطان المعدة'),
    'previous_stroke': _labels('History of stroke', 'سابقه سکته مغزی', 'تاريخ السكتة الدماغية'),
    'history_totchol': _labels('Ever told total cholesterol is high', 'سابقه اعلام کلسترول بالا', 'هل سبق إخبارك بارتفاع الكوليسترول الكلي'),
    'family_history_stroke': _labels('Close family member had heart attack or stroke', 'سابقه سکته قلبی یا مغزی در بستگان نزدیک', 'إصابة قريب من العائلة بنوبة قلبية أو سكتة دماغية'),
    'stroke_score': _labels('Stroke Risk Score', 'امتیاز خطر سکته مغزی', 'درجة خطر السكتة الدماغية'),
    'v1_v2': _labels('Number of separate colorectal cancers', 'تعداد سرطان‌های جداگانه روده بزرگ', 'عدد سرطانات القولون والمستقيم المنفصلة'),
    'v3': _labels('History of endometrial cancer', 'سابقه سرطان آندومتر', 'تاريخ سرطان بطانة الرحم'),
    'v4': _labels('History of another Lynch syndrome-related cancer', 'سابقه سایر سرطان‌های مرتبط با سندروم لینچ', 'تاريخ سرطان آخر مرتبط بمتلازمة لينش'),
    'v5_AB': _labels('First-degree relatives with colorectal cancer', 'بستگان درجه اول مبتلا به سرطان روده بزرگ', 'الأقارب من الدرجة الأولى المصابون بسرطان القولون والمستقيم'),
    'v5_CD': _labels('Second-degree relatives with colorectal cancer', 'بستگان درجه دوم مبتلا به سرطان روده بزرگ', 'الأقارب من الدرجة الثانية المصابون بسرطان القولون والمستقيم'),
    'v6_AB': _labels('First-degree relatives with endometrial cancer', 'بستگان درجه اول مبتلا به سرطان آندومتر', 'الأقارب من الدرجة الأولى المصابون بسرطان بطانة الرحم'),
    'v6_CD': _labels('Second-degree relatives with endometrial cancer', 'بستگان درجه دوم مبتلا به سرطان آندومتر', 'الأقارب من الدرجة الثانية المصابون بسرطان بطانة الرحم'),
    'v7_E': _labels('Other first-degree relatives with Lynch syndrome-related cancer', 'سایر بستگان درجه اول مبتلا به سرطان مرتبط با سندروم لینچ', 'أقارب آخرون من الدرجة الأولى مصابون بسرطان مرتبط بمتلازمة لينش'),
    'v7_F': _labels('Other second-degree relatives with Lynch syndrome-related cancer', 'سایر بستگان درجه دوم مبتلا به سرطان مرتبط با سندروم لینچ', 'أقارب آخرون من الدرجة الثانية مصابون بسرطان مرتبط بمتلازمة لينش'),
    'v8_MinAge_CRC': _labels('Age at first colorectal cancer diagnosis', 'سن اولین تشخیص سرطان روده بزرگ', 'العمر عند تشخيص سرطان القولون والمستقيم الأول'),
    'v8_MinAge_CRC_FDR': _labels('Youngest first-degree relative with colorectal cancer (age)', 'سن جوان‌ترین بستگان درجه اول مبتلا به سرطان روده بزرگ', 'عمر أصغر قريب من الدرجة الأولى مصاب بسرطان القولون والمستقيم'),
    'v8_MinAge_CRC_SDR': _labels('Youngest second-degree relative with colorectal cancer (age)', 'سن جوان‌ترین بستگان درجه دوم مبتلا به سرطان روده بزرگ', 'عمر أصغر قريب من الدرجة الثانية مصاب بسرطان القولون والمستقيم'),
    'v9_MinAge_EC': _labels('Age at first endometrial cancer diagnosis', 'سن اولین تشخیص سرطان آندومتر', 'العمر عند تشخيص سرطان بطانة الرحم الأول'),
    'v9_MinAge_EC_FDR': _labels('Youngest first-degree relative with endometrial cancer (age)', 'سن جوان‌ترین بستگان درجه اول مبتلا به سرطان آندومتر', 'عمر أصغر قريب من الدرجة الأولى مصاب بسرطان بطانة الرحم'),
    'v9_MinAge_EC_SDR': _labels('Youngest second-degree relative with endometrial cancer (age)', 'سن جوان‌ترین بستگان درجه دوم مبتلا به سرطان آندومتر', 'عمر أصغر قريب من الدرجة الثانية مصاب بسرطان بطانة الرحم'),
    'risk_status': _labels('Risk status', 'وضعیت خطر', 'حالة الخطورة'),
    'recommendation': _labels('Doctor recommendation', 'توصیه پزشک', 'توصية الطبيب'),
    'risk_score': _labels('Risk score', 'امتیاز خطر', 'درجة الخطورة'),
    'max_score': _labels('Maximum score', 'حداکثر امتیاز', 'الدرجة القصوى'),
    'risk_level': _labels('Risk level', 'سطح خطر', 'مستوى الخطورة'),
}


GENERIC_ANSWER_LABELS = {
    'yes': _labels('Yes', 'بله', 'نعم'),
    'no': _labels('No', 'خیر', 'لا'),
    'unknown': _labels('Unknown', 'نامشخص', 'غير معروف'),
    'dont know': _labels("Don't know", 'نمی‌دانم', 'لا أعرف'),
    'dont know.': _labels("Don't know", 'نمی‌دانم', 'لا أعرف'),
    'do not know': _labels("Don't know", 'نمی‌دانم', 'لا أعرف'),
    'none': _labels('None', 'هیچ‌کدام', 'لا يوجد'),
    'normal': _labels('Normal', 'طبیعی', 'طبيعي'),
    'abnormal': _labels('Abnormal', 'غیرطبیعی', 'غير طبيعي'),
    'not sure': _labels('Not sure', 'مطمئن نیستم', 'غير متأكد'),
    'not performed or not sure': _labels('Not performed or not sure', 'انجام نشده یا نامشخص', 'لم يُجرَ أو غير متأكد'),
    'negative': _labels('Negative', 'منفی', 'سلبي'),
    'low risk': _labels('Low risk', 'خطر پایین', 'خطورة منخفضة'),
    'other high risk': _labels('Other high risk', 'سایر خطرهای بالا', 'خطورة عالية أخرى'),
    'unknown / no test': _labels('Unknown / no test', 'نامشخص / آزمایشی انجام نشده', 'غير معروف / لم يُجرَ الفحص'),
}


FIELD_ANSWER_LABELS = {
    'born_place': {
        '1': _labels('Asia, North Africa, Europe', 'آسیا، شمال آفریقا، اروپا', 'آسيا، شمال أفريقيا، أوروبا'),
        '2': _labels('Other', 'سایر', 'أخرى'),
    },
    'ethnicity': {
        '1': _labels('White', 'سفید', 'أبيض'), '2': _labels('Black', 'سیاه', 'أسود'),
        '3': _labels('Hispanic', 'هیسپانیک', 'إسباني'), '7': _labels('Chinese', 'چینی', 'صيني'),
        '8': _labels('Japanese', 'ژاپنی', 'ياباني'), '9': _labels('Filipino', 'فیلیپینی', 'فلبيني'),
        '10': _labels('Hawaiian', 'هاوایی', 'هاوايي'), '11': _labels('Other Pacific Islander', 'سایر جزایر اقیانوس آرام', 'سكان جزر المحيط الهادئ الآخرون'),
        '12': _labels('Asian', 'آسیایی', 'آسيوي'),
    },
    'dairy': {
        '1': _labels('Less than one serving', 'کمتر از یک وعده', 'أقل من حصة واحدة'),
        '2': _labels('Between 1 and 2 servings', 'بین ۱ تا ۲ وعده', 'بين حصة وحصتين'),
        '3': _labels('More than 2 servings', 'بیشتر از ۲ وعده', 'أكثر من حصتين'),
    },
    'vegetables': {
        'every_day': _labels('Every day (most days)', 'هر روز (بیشتر روزها)', 'كل يوم (معظم الأيام)'),
        'not_every_day': _labels('Not every day (most days)', 'هر روز (بیشتر روزها) مصرف نمی‌شود', 'ليس كل يوم (معظم الأيام)'),
    },
    'relatives_diabetes': {
        'No': _labels('No', 'خیر', 'لا'),
        'Yes_1': _labels('Yes (parent, sibling, or child)', 'بله (والدین، خواهر، برادر یا فرزند)', 'نعم (أحد الوالدين أو الأخ أو الأخت أو الابن)'),
        'Yes_2': _labels('Yes (grandparent, aunt, or uncle)', 'بله (پدربزرگ، مادربزرگ، عمه، خاله، عمو یا دایی)', 'نعم (جد أو جدة أو عمة أو خالة أو عم أو خال)'),
    },
    'cytology': {
        '1': _labels('Not available / no test', 'در دسترس نیست / آزمایشی انجام نشده', 'غير متوفر / لم يُجرَ الفحص'),
        '2': _labels('Normal/NILM', 'طبیعی/NILM', 'طبيعي/NILM'),
        '3': _labels('ASC-US', 'ASC-US', 'ASC-US'), '4': _labels('AGC', 'AGC', 'AGC'),
        '5': _labels('LSIL', 'LSIL', 'LSIL'), '6': _labels('ASC-H', 'ASC-H', 'ASC-H'),
        '7': _labels('HSIL', 'HSIL', 'HSIL'),
    },
    'cin': {
        '1': _labels('Normal', 'طبیعی', 'طبيعي'), '2': _labels('CIN1', 'CIN1', 'CIN1'),
        '3': _labels('CIN2', 'CIN2', 'CIN2'), '4': _labels('CIN3', 'CIN3', 'CIN3'),
        '5': _labels('AIS', 'AIS', 'AIS'),
    },
    'hpv': {
        '1': _labels('Negative', 'منفی', 'سلبي'), '2': _labels('Low risk', 'خطر پایین', 'خطورة منخفضة'),
        '3': _labels('Other high risk', 'سایر خطرهای بالا', 'خطورة عالية أخرى'), '4': _labels('HPV 16 or 18', 'HPV نوع ۱۶ یا ۱۸', 'HPV 16 أو 18'),
    },
    'result_bmd_test': {
        'Dont know': _labels("Don't know", 'نمی‌دانم', 'لا أعرف'),
        'Normal BMD': _labels('Normal BMD', 'تراکم استخوان طبیعی', 'كثافة عظام طبيعية'),
        'Low BMD': _labels('Low BMD', 'تراکم استخوان پایین', 'كثافة عظام منخفضة'),
        'Osteoporosis': _labels('Osteoporosis', 'پوکی استخوان', 'هشاشة العظام'),
    },
    'gender': {
        'Male': _labels('Male', 'مرد', 'ذكر'), 'Female': _labels('Female', 'زن', 'أنثى'),
    },
    'menopause_hormone': {
        '1': _labels('Never had hormone therapy', 'هرگز درمان هورمونی نداشته‌ام', 'لم أتلق علاجاً هرمونياً من قبل'),
        '2': _labels('Less than 5 years', 'کمتر از ۵ سال', 'أقل من 5 سنوات'),
        '3': _labels('Between 5 and 9 years', 'بین ۵ تا ۹ سال', 'بين 5 و9 سنوات'),
        '4': _labels('More than 9 years', 'بیشتر از ۹ سال', 'أكثر من 9 سنوات'),
    },
    'biopsy': {
        '0': _labels('No / unknown', 'خیر / نامشخص', 'لا / غير معروف'),
        '1': _labels('Yes', 'بله', 'نعم'),
    },
    'biopsy_num': {
        '0': _labels('None', 'هیچ‌کدام', 'لا يوجد'),
        '1': _labels('Unknown / one biopsy', 'نامشخص / یک نمونه‌برداری', 'غير معروف / خزعة واحدة'),
        '2': _labels('Two or more biopsies', 'دو نمونه‌برداری یا بیشتر', 'خزعتان أو أكثر'),
    },
    'hyperplasia_biopsy': {
        '0': _labels('No', 'خیر', 'لا'), '1': _labels('Yes', 'بله', 'نعم'),
        '99': _labels('Unknown', 'نامشخص', 'غير معروف'),
    },
    'menstruation_age': {
        '0': _labels('Unknown / older than 13 years', 'نامشخص / بیشتر از ۱۳ سال', 'غير معروف / أكبر من 13 سنة'),
        '1': _labels('Between 12 and 13 years', 'بین ۱۲ تا ۱۳ سال', 'بين 12 و13 سنة'),
        '2': _labels('Less than 12 years', 'کمتر از ۱۲ سال', 'أقل من 12 سنة'),
    },
    'child_age': {
        '0': _labels('Unknown / less than 20 years', 'نامشخص / کمتر از ۲۰ سال', 'غير معروف / أقل من 20 سنة'),
        '1': _labels('Between 20 and 24 years', 'بین ۲۰ تا ۲۴ سال', 'بين 20 و24 سنة'),
        '2': _labels('No childbirth / between 25 and 29 years', 'بدون زایمان / بین ۲۵ تا ۲۹ سال', 'لا ولادة / بين 25 و29 سنة'),
        '3': _labels('30 years and older', '۳۰ سال و بیشتر', '30 سنة أو أكثر'),
    },
    'fdr_cancer': {
        '0': _labels('None / unknown', 'هیچ‌کدام / نامشخص', 'لا يوجد / غير معروف'),
        '1': _labels('One relative', 'یک بستگان', 'قريب واحد'),
        '2': _labels('Two or more relatives', 'دو بستگان یا بیشتر', 'قريبان أو أكثر'),
    },
    'aspirin': {
        'Yes - Not Currently': _labels('Yes - not currently', 'بله - در حال حاضر مصرف نمی‌شود', 'نعم - ليس حالياً'),
    },
    'painmed': {
        'Yes, currently': _labels('Yes, currently', 'بله، در حال حاضر', 'نعم، حالياً'),
        'Yes, but not currently': _labels('Yes, but not currently', 'بله، اما در حال حاضر نه', 'نعم، ولكن ليس حالياً'),
    },
    'estrogen': {
        'Yes-currently': _labels('Yes - currently', 'بله - در حال حاضر', 'نعم - حالياً'),
        'Yes-previously': _labels('Yes - previously', 'بله - قبلاً', 'نعم - سابقاً'),
    },
}


_COUNT_LABELS = {
    '0': _labels('None', 'هیچ‌کدام', 'لا يوجد'),
    '1': _labels('One', 'یک مورد', 'واحد'),
    '2': _labels('Two or more', 'دو مورد یا بیشتر', 'اثنان أو أكثر'),
}
for _count_key in ('v1_v2', 'v5_AB', 'v5_CD', 'v6_AB', 'v6_CD'):
    FIELD_ANSWER_LABELS[_count_key] = _COUNT_LABELS

for _binary_key in ('v3', 'v4', 'v7_E', 'v7_F'):
    FIELD_ANSWER_LABELS[_binary_key] = {
        '0': _labels('No', 'خیر', 'لا'),
        '1': _labels('Yes', 'بله', 'نعم'),
    }


def _value_key(value):
    return str(value).strip()


def localized_question(key, language='en', fallback=None):
    language = normalize_language(language)
    labels = QUESTION_LABELS.get(key)
    if labels:
        return labels.get(language) or labels['en']
    return fallback or key.replace('_', ' ').capitalize()


def localized_answer(key, value, language='en', not_provided='Not provided'):
    language = normalize_language(language)
    if value is None or value == '':
        return not_provided
    if isinstance(value, bool):
        value = 'Yes' if value else 'No'

    raw_key = _value_key(value)
    field_labels = FIELD_ANSWER_LABELS.get(key, {})
    labels = field_labels.get(raw_key)
    if labels is None:
        labels = field_labels.get(raw_key.lower())
    if labels is None:
        labels = GENERIC_ANSWER_LABELS.get(raw_key.lower())
    if labels is None and raw_key.lower().startswith('yes_'):
        labels = GENERIC_ANSWER_LABELS['yes']
    return (labels.get(language) or labels['en']) if labels else value
