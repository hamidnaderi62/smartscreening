"""Readable, self-contained PDF reports for completed screenings."""

import html
import io
import json
import logging
import os

import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt
from django.conf import settings
from reportlab.lib import colors
from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    HRFlowable,
    Image,
    KeepTogether,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)
from django.utils.translation import get_language
from django.utils import timezone

from .localization import (
    format_localized_date,
    format_localized_datetime,
    language_for_request,
    normalize_language,
)
from .questionnaire_translations import localized_answer, localized_question
from .screening_data import ASSESSMENT_FIELDS

try:
    import arabic_reshaper
    from bidi.algorithm import get_display
except ImportError:  # pragma: no cover - requirements.txt provides these packages.
    arabic_reshaper = None
    get_display = None

logger = logging.getLogger(__name__)

PAGE_WIDTH, PAGE_HEIGHT = A4
CONTENT_WIDTH = 180 * mm
NAVY = HexColor('#173F5F')
BLUE = HexColor('#20639B')
LIGHT_GREY = HexColor('#F5F7FA')
MUTED = HexColor('#657786')
RED = HexColor('#D64545')
AMBER = HexColor('#E9A227')
GREEN = HexColor('#2E9D68')

# Calculation outputs belong in the result summary, not among the patient's
# questionnaire answers. Keep status/recommendation out too: they are printed
# as the final, visually distinct rows of each disease section.
PDF_EXCLUDED_ASSESSMENT_KEYS = frozenset(
    {'risk_score', 'max_score', 'risk_level', 'risk_status', 'recommendation'}
    | {
        key
        for fields in ASSESSMENT_FIELDS.values()
        for field in fields
        for key, question, *_source in (field,)
        if key.endswith('_score') or 'risk (%)' in question.casefold()
    }
)


REPORT_LABELS = {
    'en': {
        'report_title': 'Comprehensive Health Screening Report',
        'report_summary': 'A clear summary of screening results, answers, recommendations, and changes over time.',
        'report_date': 'Report date', 'patient_code': 'Patient code',
        'age_gender': 'Age / gender', 'screening_date': 'Screening date',
        'assessments_included': 'Assessments included', 'value': 'Value',
        'patient_info': 'Patient and report information',
        'disclaimer': 'This report supports a conversation with a qualified healthcare professional. A risk score is not a diagnosis and should be interpreted with clinical history and examination.',
        'results': '1. Results at a glance', 'history': '2. Historical change',
        'history_intro': 'These charts use the same disease-specific series, chart types, colors, and risk scales as the comprehensive dashboard.',
        'first_history': 'This is the first available screening record for the selected assessments. Future reports will show changes here.',
        'previous': 'Previous result', 'current': 'Current result', 'change': 'Change',
        'questions': '3. Questions and answers',
        'questions_intro': 'The following sections reproduce the answers saved with this screening. “Not provided” means no answer was stored for that question.',
        'demographic': 'Demographic information', 'lifestyle': 'Lifestyle information',
        'medical': 'Medical history', 'no_answers': 'No detailed answers were stored for this assessment.',
        'recommendations': '4. Recommendations and follow-up',
        'recommendations_intro': 'These recommendations are generated from the screening result and are intended to guide follow-up discussion. They do not replace medical advice.',
        'assessment': 'Assessment', 'risk_status': 'Risk status', 'recommendation': 'Recommendation',
        'question': 'Question', 'answer': 'Answer',
        'doctor_note': 'Doctor’s note', 'clinical_comment': 'Clinical comment',
        'no_doctor_comment': 'No doctor comment has been added.', 'important': 'Important information',
        'recommendation_fallback': 'Discuss this result with a healthcare professional.',
        'important_text': 'Screening results estimate risk based on the information provided at the time of assessment. They are not a diagnosis, do not predict individual outcomes with certainty, and should be reviewed by a licensed healthcare professional. Seek urgent care for urgent or severe symptoms.',
        'not_provided': 'Not provided', 'score': 'Score', 'page': 'Page',
    },
    'fa': {
        'report_title': 'گزارش جامع غربالگری سلامت',
        'report_summary': 'خلاصه‌ای روشن از نتایج، پاسخ‌ها، توصیه‌ها و تغییرات غربالگری در طول زمان.',
        'report_date': 'تاریخ گزارش', 'patient_code': 'کد بیمار', 'age_gender': 'سن / جنسیت',
        'screening_date': 'تاریخ غربالگری', 'assessments_included': 'تعداد ارزیابی‌ها', 'value': 'مقدار',
        'patient_info': 'اطلاعات بیمار و گزارش',
        'disclaimer': 'این گزارش برای گفتگو با پزشک تهیه شده است. امتیاز خطر تشخیص قطعی نیست و باید همراه با سابقه پزشکی و معاینه تفسیر شود.',
        'results': '۱. خلاصه نتایج', 'history': '۲. تغییرات تاریخی',
        'history_intro': 'این نمودارها همان سری داده، نوع نمودار، رنگ‌ها و مقیاس‌های داشبورد جامع را استفاده می‌کنند.',
        'first_history': 'برای ارزیابی‌های انتخاب‌شده سابقه‌ای ثبت نشده است. گزارش‌های بعدی تغییرات را نشان خواهند داد.',
        'previous': 'نتیجه قبلی', 'current': 'نتیجه فعلی', 'change': 'تغییر',
        'questions': '۳. پرسش‌ها و پاسخ‌ها',
        'questions_intro': 'پاسخ‌های ذخیره‌شده این غربالگری در بخش‌های زیر نمایش داده شده‌اند. «ارائه نشده» یعنی پاسخی ذخیره نشده است.',
        'demographic': 'اطلاعات جمعیت‌شناختی', 'lifestyle': 'سبک زندگی', 'medical': 'سابقه پزشکی',
        'no_answers': 'پاسخ جزئی برای این ارزیابی ذخیره نشده است.', 'recommendations': '۴. توصیه‌ها و پیگیری',
        'recommendations_intro': 'این توصیه‌ها بر اساس نتیجه غربالگری ایجاد شده‌اند و جایگزین مشاوره پزشکی نیستند.',
        'assessment': 'ارزیابی', 'risk_status': 'وضعیت خطر', 'recommendation': 'توصیه',
        'question': 'پرسش', 'answer': 'پاسخ',
        'doctor_note': 'یادداشت پزشک', 'clinical_comment': 'توضیحات بالینی',
        'no_doctor_comment': 'یادداشت پزشکی ثبت نشده است.', 'important': 'اطلاعات مهم',
        'recommendation_fallback': 'این نتیجه را با یک متخصص مراقبت‌های سلامت بررسی کنید.',
        'important_text': 'نتایج غربالگری بر اساس اطلاعات زمان ارزیابی، خطر را تخمین می‌زنند. این نتایج تشخیص نیستند و باید توسط پزشک بررسی شوند. در صورت علائم شدید یا اورژانسی فوراً به مراکز درمانی مراجعه کنید.',
        'not_provided': 'ارائه نشده', 'score': 'امتیاز', 'page': 'صفحه',
    },
    'ar': {
        'report_title': 'تقرير الفحص الصحي الشامل',
        'report_summary': 'ملخص واضح للنتائج والإجابات والتوصيات والتغييرات مع مرور الوقت.',
        'report_date': 'تاريخ التقرير', 'patient_code': 'رمز المريض', 'age_gender': 'العمر / الجنس',
        'screening_date': 'تاريخ الفحص', 'assessments_included': 'التقييمات المشمولة', 'value': 'القيمة',
        'patient_info': 'معلومات المريض والتقرير',
        'disclaimer': 'يساعد هذا التقرير على مناقشة النتائج مع طبيب مؤهل. درجة الخطورة ليست تشخيصاً ويجب تفسيرها مع التاريخ الطبي والفحص.',
        'results': '١. ملخص النتائج', 'history': '٢. التغيّر التاريخي',
        'history_intro': 'تستخدم هذه الرسوم السلاسل وأنواع الرسوم والألوان والمقاييس نفسها الموجودة في لوحة التحكم الشاملة.',
        'first_history': 'لا يوجد سجل فحص سابق للتقييمات المحددة. ستظهر التغييرات في التقارير المستقبلية.',
        'previous': 'النتيجة السابقة', 'current': 'النتيجة الحالية', 'change': 'التغيير',
        'questions': '٣. الأسئلة والإجابات',
        'questions_intro': 'تعرض الأقسام التالية الإجابات المحفوظة لهذا الفحص. تعني «غير متوفر» عدم حفظ إجابة.',
        'demographic': 'المعلومات الديموغرافية', 'lifestyle': 'نمط الحياة', 'medical': 'التاريخ الطبي',
        'no_answers': 'لم يتم حفظ إجابات تفصيلية لهذا التقييم.', 'recommendations': '٤. التوصيات والمتابعة',
        'recommendations_intro': 'تم إنشاء هذه التوصيات من نتيجة الفحص للمساعدة في المتابعة، ولا تحل محل المشورة الطبية.',
        'assessment': 'التقييم', 'risk_status': 'حالة الخطورة', 'recommendation': 'التوصية',
        'question': 'السؤال', 'answer': 'الإجابة',
        'doctor_note': 'ملاحظة الطبيب', 'clinical_comment': 'التعليق السريري',
        'no_doctor_comment': 'لم تتم إضافة ملاحظة للطبيب.', 'important': 'معلومات مهمة',
        'recommendation_fallback': 'ناقش هذه النتيجة مع طبيب أو أخصائي رعاية صحية.',
        'important_text': 'تقدّر نتائج الفحص الخطورة بناءً على المعلومات المقدمة وقت التقييم. ليست تشخيصاً ويجب مراجعتها من طبيب مرخص. اطلب رعاية عاجلة عند وجود أعراض شديدة أو طارئة.',
        'not_provided': 'غير متوفر', 'score': 'النتيجة', 'page': 'صفحة',
    },
}


def _report_labels(language):
    return REPORT_LABELS[normalize_language(language)]


def _is_rtl_language(language):
    return normalize_language(language) in {'fa', 'ar'}


def _register_fonts():
    """Use the bundled font when available, with a portable fallback."""
    regular = 'Helvetica'
    bold = 'Helvetica-Bold'
    font_dir = getattr(settings, 'BASE_DIR', None)
    if font_dir:
        regular_path = os.path.join(font_dir, 'assets', 'fonts', 'vazir', 'Vazir.ttf')
        bold_path = os.path.join(font_dir, 'assets', 'fonts', 'vazir', 'Vazir-Bold.ttf')
        if os.path.exists(regular_path) and 'SmartScreeningRegular' not in pdfmetrics.getRegisteredFontNames():
            pdfmetrics.registerFont(TTFont('SmartScreeningRegular', regular_path))
        if os.path.exists(bold_path) and 'SmartScreeningBold' not in pdfmetrics.getRegisteredFontNames():
            pdfmetrics.registerFont(TTFont('SmartScreeningBold', bold_path))
        if 'SmartScreeningRegular' in pdfmetrics.getRegisteredFontNames():
            regular = 'SmartScreeningRegular'
        if 'SmartScreeningBold' in pdfmetrics.getRegisteredFontNames():
            bold = 'SmartScreeningBold'
    return regular, bold


def _text(value):
    """Convert persisted values into safe, readable PDF text."""
    if value is None or value == '':
        return 'Not provided'
    if isinstance(value, bool):
        return 'Yes' if value else 'No'
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    if isinstance(value, (dict, list, tuple)):
        return json.dumps(value, ensure_ascii=False)
    return str(value)


def _shape_rtl(value):
    """Shape and reorder Arabic/Persian text for ReportLab's LTR canvas."""
    value = str(value)
    if not any('\u0600' <= character <= '\u06ff' for character in value):
        return value
    if arabic_reshaper is None or get_display is None:
        logger.warning('Arabic/Persian PDF shaping dependencies are unavailable')
        return value
    return get_display(arabic_reshaper.reshape(value))


def _rtl_wrapped_lines(value, style=None, max_width=CONTENT_WIDTH):
    """Wrap RTL text before bidi shaping so ReportLab cannot reorder lines."""
    raw = _text(value)
    regular, _ = _register_fonts()
    font_name = getattr(style, 'fontName', regular)
    font_size = getattr(style, 'fontSize', 9)
    lines = []

    for paragraph in raw.splitlines() or ['']:
        words = paragraph.split()
        if not words:
            lines.append('')
            continue
        current = ''
        for word in words:
            candidate = f'{current} {word}'.strip()
            candidate_width = pdfmetrics.stringWidth(
                _shape_rtl(candidate), font_name, font_size,
            )
            if current and candidate_width > max_width:
                lines.append(current)
                current = word
            else:
                current = candidate
        if current:
            lines.append(current)
    return lines


def _escaped(value, style=None, max_width=CONTENT_WIDTH):
    raw = _text(value)
    if any('\u0600' <= character <= '\u06ff' for character in raw):
        return '<br/>'.join(
            html.escape(_shape_rtl(line))
            for line in _rtl_wrapped_lines(raw, style, max_width)
        )
    return html.escape(raw).replace('\n', '<br/>')


def _p(value, style, max_width=CONTENT_WIDTH):
    return Paragraph(_escaped(value, style, max_width), style)


def _styles(language='en'):
    regular, bold = _register_fonts()
    base = getSampleStyleSheet()
    text_alignment = TA_RIGHT if _is_rtl_language(language) else 0
    return {
        'title': ParagraphStyle(
            'ReportTitle', parent=base['Title'], fontName=bold, fontSize=22,
            leading=27, textColor=NAVY, alignment=TA_CENTER, spaceAfter=4 * mm,
        ),
        'subtitle': ParagraphStyle(
            'ReportSubtitle', parent=base['Normal'], fontName=regular, fontSize=10,
            leading=14, textColor=MUTED, alignment=TA_CENTER, spaceAfter=7 * mm,
        ),
        'h1': ParagraphStyle(
            'ReportHeading1', parent=base['Heading1'], fontName=bold, fontSize=15,
            leading=19, textColor=NAVY, alignment=text_alignment,
            spaceBefore=6 * mm, spaceAfter=3 * mm,
        ),
        'h2': ParagraphStyle(
            'ReportHeading2', parent=base['Heading2'], fontName=bold, fontSize=11,
            leading=14, textColor=BLUE, alignment=text_alignment,
            spaceBefore=3 * mm, spaceAfter=2 * mm,
        ),
        'section': ParagraphStyle(
            'ReportSection', parent=base['Heading1'], fontName=bold, fontSize=13.5,
            leading=17, textColor=NAVY, alignment=text_alignment,
            spaceBefore=0, spaceAfter=0,
        ),
        'chart_title': ParagraphStyle(
            'ReportChartTitle', parent=base['Heading2'], fontName=bold, fontSize=10.5,
            leading=13, textColor=NAVY, alignment=text_alignment,
            spaceBefore=0, spaceAfter=0,
        ),
        'body': ParagraphStyle(
            'ReportBody', parent=base['BodyText'], fontName=regular, fontSize=9,
            leading=13, textColor=HexColor('#263238'), alignment=text_alignment,
            spaceAfter=2 * mm,
        ),
        'small': ParagraphStyle(
            'ReportSmall', parent=base['BodyText'], fontName=regular, fontSize=7.5,
            leading=10, textColor=MUTED, alignment=text_alignment,
        ),
        'table': ParagraphStyle(
            'ReportTable', parent=base['BodyText'], fontName=regular, fontSize=8,
            leading=10, textColor=HexColor('#263238'), alignment=text_alignment,
        ),
        'table_bold': ParagraphStyle(
            'ReportTableBold', parent=base['BodyText'], fontName=bold, fontSize=8,
            leading=10, textColor=NAVY, alignment=text_alignment,
        ),
        'table_header': ParagraphStyle(
            'ReportTableHeader', parent=base['BodyText'], fontName=bold, fontSize=8,
            leading=10, textColor=colors.white, alignment=text_alignment,
        ),
        'callout': ParagraphStyle(
            'ReportCallout', parent=base['BodyText'], fontName=regular, fontSize=9,
            leading=13, textColor=NAVY, alignment=text_alignment,
            leftIndent=3 * mm, rightIndent=3 * mm,
        ),
    }


def _section_header(title, styles, rtl=False):
    """Create a strong visual divider for each major report section."""
    heading = Paragraph(_escaped(title), styles['section'])
    accent = ''
    row = [[heading, accent]] if rtl else [[accent, heading]]
    widths = [CONTENT_WIDTH - 5 * mm, 5 * mm] if rtl else [5 * mm, CONTENT_WIDTH - 5 * mm]
    table = Table(row, colWidths=widths, rowHeights=[11 * mm], hAlign='RIGHT' if rtl else 'LEFT')
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), HexColor('#F1F6FA')),
        ('BACKGROUND', (1, 0), (1, 0), NAVY) if rtl else ('BACKGROUND', (0, 0), (0, 0), NAVY),
        ('BOX', (0, 0), (-1, -1), 0.6, HexColor('#D9E2EC')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ]))
    return table


def _table(
    rows,
    widths,
    styles,
    *,
    header=True,
    row_background=LIGHT_GREY,
    rtl=False,
    highlighted_rows=None,
):
    highlighted_rows = highlighted_rows or {}
    if rtl:
        rows = [list(reversed(row)) if len(row) > 1 else row for row in rows]
        widths = list(reversed(widths))
    prepared = []
    for row_index, row in enumerate(rows):
        highlight = highlighted_rows.get(row_index)
        cell_style = styles['table_header'] if row_index == 0 and header else styles['table']
        if highlight:
            _background, text_color = highlight
            cell_style = ParagraphStyle(
                f'ReportTableHighlight{row_index}',
                parent=cell_style,
                textColor=text_color,
                fontName=styles['table_bold'].fontName,
            )
        prepared.append([
            _p(
                value,
                cell_style,
                max_width=max(width - 10, 25),
            )
            for value, width in zip(row, widths)
        ])
    table = Table(
        prepared,
        colWidths=widths,
        repeatRows=1 if header else 0,
        hAlign='RIGHT' if rtl else 'LEFT',
    )
    commands = [
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('GRID', (0, 0), (-1, -1), 0.35, HexColor('#D9E2EC')),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]
    if header:
        commands.extend([
            ('BACKGROUND', (0, 0), (-1, 0), NAVY),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ])
    if len(rows) > 1:
        commands.append(('ROWBACKGROUNDS', (0, 1 if header else 0), (-1, -1), [colors.white, row_background]))
    for row_index, (background, _text_color) in highlighted_rows.items():
        commands.append(('BACKGROUND', (0, row_index), (-1, row_index), background))
    table.setStyle(TableStyle(commands))
    return table


def _organization_for(record):
    try:
        return record.userid.profile.organization
    except (AttributeError, ValueError):
        return None


def _logo_path(organization):
    if not organization or not organization.logo:
        return None
    try:
        path = organization.logo.path
    except (AttributeError, ValueError):
        return None
    return path if os.path.exists(path) else None


def _image_path(image_field):
    if not image_field:
        return None
    try:
        path = image_field.path
    except (AttributeError, ValueError):
        return None
    return path if os.path.exists(path) else None


def _page_decor(organization, regular, bold, labels, language='en'):
    language = normalize_language(language)
    rtl = _is_rtl_language(language)
    organization_title = _text(
        getattr(organization, f'title_{language}', None)
        or getattr(organization, 'title', None)
        or 'SmartScreening'
    )
    logo_path = _logo_path(organization)

    def draw(canvas, doc):
        canvas.saveState()
        content_right = PAGE_WIDTH - doc.rightMargin
        header_bottom = PAGE_HEIGHT - 21 * mm

        # Branded header panel. It stays inside the reserved top margin so it
        # never overlaps report content, including on pages with large tables.
        canvas.setFillColor(colors.white)
        canvas.setStrokeColor(HexColor('#D9E2EC'))
        canvas.setLineWidth(0.6)
        canvas.roundRect(
            doc.leftMargin, header_bottom, CONTENT_WIDTH, 15 * mm,
            2.5 * mm, fill=1, stroke=1,
        )
        canvas.setFillColor(BLUE)
        if rtl:
            canvas.roundRect(content_right - 2 * mm, header_bottom, 2 * mm, 15 * mm, 1 * mm, fill=1, stroke=0)
        else:
            canvas.roundRect(doc.leftMargin, header_bottom, 2 * mm, 15 * mm, 1 * mm, fill=1, stroke=0)
        if logo_path:
            try:
                logo_x = content_right - 25 * mm if rtl else doc.leftMargin
                canvas.drawImage(
                    logo_path, logo_x, PAGE_HEIGHT - 18 * mm,
                    width=25 * mm, height=12 * mm, preserveAspectRatio=True,
                    anchor='sw', mask='auto',
                )
            except Exception:
                logger.warning('Unable to add organization logo to PDF', exc_info=True)
        canvas.setFont(bold, 8)
        canvas.setFillColor(NAVY)
        if rtl:
            text_x = content_right - 29 * mm
            canvas.drawRightString(text_x, PAGE_HEIGHT - 11 * mm, _shape_rtl(organization_title))
            canvas.setFont(regular, 7)
            canvas.setFillColor(MUTED)
            canvas.drawRightString(text_x, PAGE_HEIGHT - 16 * mm, _shape_rtl(labels['report_title']))
        else:
            text_x = doc.leftMargin + 29 * mm
            canvas.drawString(text_x, PAGE_HEIGHT - 11 * mm, organization_title)
            canvas.setFont(regular, 7)
            canvas.setFillColor(MUTED)
            canvas.drawString(text_x, PAGE_HEIGHT - 16 * mm, labels['report_title'])

        canvas.setFillColor(HexColor('#F7F9FB'))
        canvas.setStrokeColor(HexColor('#D9E2EC'))
        canvas.setLineWidth(0.6)
        canvas.roundRect(doc.leftMargin, 5 * mm, CONTENT_WIDTH, 8 * mm, 2 * mm, fill=1, stroke=0)
        canvas.line(doc.leftMargin, 15 * mm, content_right, 15 * mm)

        # Clean footer: only product identity and page number.
        canvas.setFont(regular, 7)
        canvas.setFillColor(MUTED)
        page_number = str(canvas.getPageNumber())
        if language == 'fa':
            page_number = page_number.translate(str.maketrans('0123456789', '۰۱۲۳۴۵۶۷۸۹'))
        if rtl:
            canvas.drawRightString(content_right - 4 * mm, 9 * mm, 'SmartScreening')
            canvas.drawString(doc.leftMargin + 4 * mm, 9 * mm, _shape_rtl(f"{labels['page']} {page_number}"))
        else:
            canvas.drawString(doc.leftMargin + 4 * mm, 9 * mm, 'SmartScreening')
            canvas.drawRightString(content_right - 4 * mm, 9 * mm, f"{labels['page']} {page_number}")
        canvas.restoreState()

    return draw


def _selected_ids(record):
    selected = set()
    for value in (record.selected_assessments_id or '').split(','):
        try:
            selected.add(int(value.strip()))
        except (TypeError, ValueError):
            continue
    return selected


HISTORY_SERIES = {
    'Breast_Cancer': (
        ('5-year absolute risk', 'gail_score_abs_5'),
        ('5-year average risk', 'gail_score_ave_5'),
        ('Lifetime absolute risk', 'gail_score_abs_90'),
        ('Lifetime average risk', 'gail_score_ave_90'),
    ),
    'Colorectal_Cancer': (
        ('PREMM score', 'premm_score'),
        ('CRCPro score', 'crcpro_score'),
    ),
    'Prostate_Cancer': (
        ('High-grade cancer risk', 'pbcg_score_high_cancer'),
        ('Low-grade cancer risk', 'pbcg_score_low_cancer'),
        ('No cancer risk', 'pbcg_score_no_cancer'),
    ),
    'Diabetes': (('Diabetes risk score', 'idf_score'),),
    'Cardiovascular_Disease': (('ASCVD score', 'ascvd_score'),),
    'Cervical_Cancer': (('Cervical cancer score', 'cervical_cancer_score'),),
    'Melanoma_Cancer': (('Melanoma score', 'melanoma_cancer_score'),),
    'Osteoporosis': (('Osteoporosis score', 'osteoporosis_score'),),
    'Ovarian_Cancer': (('Ovarian cancer score', 'ovarian_cancer_score'),),
    'Stomach_Cancer': (('Stomach cancer score', 'stomach_cancer_score'),),
    'Stroke': (('Stroke score', 'stroke_score'),),
    'Pancreatic_Cancer': (('Pancreatic cancer score', 'pancreatic_cancer_score'),),
}


# Keep the PDF charts visually consistent with dashboard_comprehensive_en.html.
# The dashboard uses ApexCharts; these settings are the equivalent Matplotlib
# representation used when rendering a printable report.
DASHBOARD_CHART_CONFIG = {
    'Breast_Cancer': (
        {
            'key': 'five_year',
            'title': '5-Year Risk History',
            'type': 'line',
            'series': ('5-year absolute risk', '5-year average risk'),
            'colors': ('#77B6EA', '#545454'),
            'y_max': 10,
            'ylabel': 'Risk',
            'smooth': True,
            'data_labels': True,
        },
        {
            'key': 'lifetime',
            'title': 'Lifetime Risk History',
            'type': 'line',
            'series': ('Lifetime absolute risk', 'Lifetime average risk'),
            'colors': ('#77B6EA', '#545454'),
            'y_max': 50,
            'ylabel': 'Risk',
            'smooth': True,
            'data_labels': True,
        },
    ),
    'Colorectal_Cancer': (
        {
            'key': 'crc',
            'title': 'CRC Risk History',
            'type': 'bar',
            'series': ('PREMM score',),
            # The dashboard does not set a bar color explicitly. This is the
            # dashboard's declared data-label color and keeps the PDF stable
            # across Matplotlib/ApexCharts versions.
            'colors': ('#304758',),
            'ylabel': 'Risk (%)',
            'data_labels': True,
        },
    ),
    'Prostate_Cancer': (
        {
            'key': 'prostate',
            'title': 'Prostate Cancer Risk History',
            'type': 'bar',
            'series': ('High-grade cancer risk', 'Low-grade cancer risk', 'No cancer risk'),
            'colors': ('#FF0000', '#FFA500', '#00FF00'),
            'ylabel': 'Risk',
            'stacked': True,
            'data_labels': False,
        },
    ),
    'Diabetes': (
        {
            'key': 'diabetes',
            'title': 'IDF Score History',
            'type': 'line',
            'series': ('Diabetes risk score',),
            'colors': ('#3F51B5',),
            'y_max': 30,
            'ylabel': 'IDF Score',
            'smooth': False,
            'data_labels': False,
        },
    ),
}

for _title in (
    'Cardiovascular_Disease',
    'Cervical_Cancer',
    'Melanoma_Cancer',
    'Osteoporosis',
    'Ovarian_Cancer',
    'Stomach_Cancer',
    'Stroke',
    'Pancreatic_Cancer',
):
    DASHBOARD_CHART_CONFIG[_title] = ({
        'key': _title.lower(),
        'title': f'{_title.replace("_", " ")} History',
        'type': 'line',
        'series': tuple(label for label, _ in HISTORY_SERIES[_title]),
        'colors': ('#77B6EA',),
        'y_max': 30,
        'ylabel': 'Risk',
        'smooth': True,
        'data_labels': True,
    },)


def _history_for_record(record, selected_assessments):
    """Return dashboard-compatible chronological series for each assessment."""
    selected_ids = {item['id'] for item in selected_assessments}
    title_by_id = {item['id']: item['title'] for item in selected_assessments}
    records = record.__class__.objects.filter(userid=record.userid).order_by('created')
    history = {
        item['title']: {label: [] for label, _ in HISTORY_SERIES.get(item['title'], ())}
        for item in selected_assessments
    }
    for historical_record in records:
        record_ids = _selected_ids(historical_record)
        for assessment_id in selected_ids.intersection(record_ids):
            title = title_by_id[assessment_id]
            for label, field_name in HISTORY_SERIES.get(title, ()):
                value = getattr(historical_record, field_name, None)
                if value is None:
                    continue
                try:
                    value = float(value)
                except (TypeError, ValueError):
                    continue
                history[title][label].append((historical_record.created, value))
    return history


def _trend(score_history, current_score):
    if len(score_history) < 2:
        return 'First recorded result', None
    previous = score_history[-2][1]
    delta = current_score - previous
    if abs(delta) < 0.0001:
        return 'No change', 0.0
    return ('Increased' if delta > 0 else 'Decreased'), delta


def _series_points(series, labels):
    """Return aligned dates and values for the requested dashboard series."""
    by_date = {}
    for label in labels:
        for created, value in series.get(label, ()):
            date_key = created.date() if hasattr(created, 'date') else created
            by_date.setdefault(date_key, {})[label] = value
    dates = sorted(by_date)
    return dates, by_date


def _add_data_labels(axis, bars, color='#304758'):
    for bar in bars:
        value = bar.get_height()
        if value is None or value == 0:
            continue
        axis.annotate(
            f'{value:g}',
            xy=(bar.get_x() + bar.get_width() / 2, bar.get_y() + value),
            xytext=(0, 3),
            textcoords='offset points',
            ha='center',
            va='bottom',
            fontsize=7,
            color=color,
        )


def _render_history_chart(title, series, spec, language='en'):
    """Render one dashboard chart specification into an in-memory PNG."""
    labels = tuple(label for label in spec['series'] if series.get(label))
    if not labels:
        return None

    dates, by_date = _series_points(series, labels)
    if not dates:
        return None

    fig, axis = plt.subplots(figsize=(8.0, 3.0), dpi=140)
    colors_for_series = spec.get('colors', ())
    chart_type = spec.get('type', 'line')
    x_positions = list(range(len(dates)))

    if chart_type == 'bar':
        width = 0.65 if len(labels) == 1 else 0.72
        if spec.get('stacked'):
            bottoms = [0.0] * len(dates)
            for index, label in enumerate(labels):
                values = [by_date[date].get(label, 0) for date in dates]
                bars = axis.bar(
                    x_positions,
                    values,
                    width=width,
                    bottom=bottoms,
                    label=label,
                    color=colors_for_series[index % len(colors_for_series)],
                    edgecolor='white',
                    linewidth=0.5,
                )
                bottoms = [bottom + value for bottom, value in zip(bottoms, values)]
                if spec.get('data_labels'):
                    _add_data_labels(axis, bars)
        else:
            values = [by_date[date].get(labels[0], 0) for date in dates]
            bars = axis.bar(
                x_positions,
                values,
                width=width,
                label=labels[0],
                color=colors_for_series[0],
                edgecolor='white',
                linewidth=0.5,
            )
            if spec.get('data_labels'):
                _add_data_labels(axis, bars)
    else:
        for index, label in enumerate(labels):
            values = [by_date[date].get(label) for date in dates]
            axis.plot(
                x_positions,
                values,
                marker='o',
                linewidth=2,
                markersize=3.5,
                label=label,
                color=colors_for_series[index % len(colors_for_series)],
            )
            if spec.get('data_labels'):
                for x_position, value in zip(x_positions, values):
                    if value is not None:
                        axis.annotate(
                            f'{value:g}',
                            (x_position, value),
                            textcoords='offset points',
                            xytext=(0, 4),
                            ha='center',
                            fontsize=6.5,
                            color=colors_for_series[index % len(colors_for_series)],
                        )

    axis.set_xticks(x_positions)
    rtl = _is_rtl_language(language)
    axis.set_xticklabels(
        [format_localized_date(date, language) for date in dates],
        rotation=35, ha='left' if rtl else 'right', fontsize=7,
    )
    axis.set_ylabel(spec.get('ylabel', 'Risk'))
    if spec.get('y_max') is not None:
        axis.set_ylim(bottom=0, top=spec['y_max'])
    else:
        axis.set_ylim(bottom=0)
    axis.grid(axis='y', alpha=0.25)
    axis.set_axisbelow(True)
    axis.legend(loc='upper right' if rtl else 'upper left', fontsize=7, frameon=False)
    for spine in ('top', 'right'):
        axis.spines[spine].set_visible(False)
    fig.tight_layout()
    image = io.BytesIO()
    fig.savefig(image, format='png', bbox_inches='tight', facecolor='white')
    plt.close(fig)
    image.seek(0)
    return image


def _trend_chart_images(history, selected_assessments, language='en'):
    """Create dashboard-compatible chart images for each selected assessment."""
    images = []
    for item in selected_assessments:
        series = history.get(item['title'], {})
        for spec in DASHBOARD_CHART_CONFIG.get(item['title'], ()):
            image = _render_history_chart(item['title'], series, spec, language)
            if image is not None:
                images.append((item['title'], spec, image))
    return images


def _chart_panel(title, chart_spec, trend_image, styles, rtl=False):
    """Place a chart title and its image inside one contained report card."""
    chart_title = chart_spec.get('title') or f'{title.replace("_", " ")} history'
    heading = Paragraph(_escaped(chart_title), styles['chart_title'])
    accent = ''
    heading_row = [[heading, accent]] if rtl else [[accent, heading]]
    heading_widths = [CONTENT_WIDTH - 15 * mm, 5 * mm] if rtl else [5 * mm, CONTENT_WIDTH - 15 * mm]
    heading_table = Table(
        heading_row,
        colWidths=heading_widths,
        rowHeights=[9 * mm],
        hAlign='RIGHT' if rtl else 'LEFT',
    )
    heading_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), HexColor('#EEF5FB')),
        ('BACKGROUND', (1, 0), (1, 0), BLUE) if rtl else ('BACKGROUND', (0, 0), (0, 0), BLUE),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 7),
        ('RIGHTPADDING', (0, 0), (-1, -1), 7),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
    ]))
    chart = Image(trend_image, width=168 * mm, height=63 * mm)
    panel = Table([[heading_table], [chart]], colWidths=[CONTENT_WIDTH], hAlign='RIGHT' if rtl else 'LEFT')
    panel.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.white),
        ('BOX', (0, 0), (-1, -1), 0.7, HexColor('#C9D8E5')),
        ('LINEBELOW', (0, 0), (-1, 0), 0.5, HexColor('#D9E2EC')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]))
    # Keep the heading and chart image together. Without this wrapper a
    # Table is allowed to split between its rows at a page boundary.
    return KeepTogether([panel])


def _risk_color(item):
    band = _risk_band(item)
    if band == 'high':
        return RED
    if band == 'moderate':
        return AMBER
    if band == 'low':
        return GREEN
    return BLUE


def _risk_band(item):
    """Return a language-independent risk band from localized status values."""
    status_values = ' '.join(
        str(item.get(key) or '')
        for key in ('display_status', 'status_en', 'status_fa', 'status_ar')
    ).casefold()

    # Check the middle band first because phrases such as
    # "moderate-high"/"متوسط-بالا" also contain a high-risk word.
    if any(word in status_values for word in (
        'moderate', 'average', 'intermediate', 'borderline',
        'متوسط', 'میانگین', 'متوسط', 'متوسطة', 'حدية',
    )):
        return 'moderate'
    if any(word in status_values for word in (
        'high', 'very high', 'زیاد', 'خیلی زیاد', 'بالا',
        'عالية', 'عالي', 'مرتفع',
    )):
        return 'high'
    if any(word in status_values for word in (
        'low', 'کم', 'پایین', 'منخفض', 'منخفضة',
    )):
        return 'low'
    return 'unknown'


def _risk_tint(item):
    band = _risk_band(item)
    if band == 'high':
        return HexColor('#FFF1F1')
    if band == 'moderate':
        return HexColor('#FFF8E8')
    if band == 'low':
        return HexColor('#EDF9F2')
    return HexColor('#EEF5FB')


def _assessment_image_path(item):
    image_name = item.get('image')
    base_dir = getattr(settings, 'BASE_DIR', None)
    if not image_name or not base_dir:
        return None
    path = os.path.join(base_dir, 'assets', 'images', 'assessments', image_name)
    return path if os.path.exists(path) else None


def _assessment_card(item, styles, labels, rtl=False):
    """Build the same visual language used by the web dashboard cards."""
    color = _risk_color(item)
    image_path = _assessment_image_path(item)
    image = Image(image_path, width=22 * mm, height=22 * mm) if image_path else _p('•', styles['h2'])
    title = item.get('display_title') or item.get('title_en') or item.get('title', '').replace('_', ' ')
    status = item.get('display_status') or item.get('status_en') or labels['not_provided']
    recommendation = item.get('display_recommendation') or item.get('recommendation_en') or labels['recommendation_fallback']
    color_value = color.hexval() if hasattr(color, 'hexval') else '#20639B'
    progress = Table([['']], colWidths=[142 * mm], rowHeights=[3 * mm])
    progress.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), color),
        ('BOX', (0, 0), (-1, -1), 0, color),
    ]))
    title_paragraph = Paragraph(_escaped(title), styles['h2'])
    status_paragraph = Paragraph(
        f'<font color="{color_value}"><b>{_escaped(status)}</b></font>',
        styles['table'],
    )
    # Shape the complete RTL sentence in one pass. Shaping the label and the
    # recommendation separately reverses their order around the colon.
    recommendation_text = f"{labels['recommendation']}: {recommendation}"
    recommendation_paragraph = Paragraph(
        f'<b>{_escaped(recommendation_text)}</b>',
        styles['table'],
    )
    details_rows = [
        [status_paragraph, title_paragraph] if rtl else [title_paragraph, status_paragraph],
        [progress, ''],
        [recommendation_paragraph, ''],
    ]
    details = Table(
        details_rows,
        colWidths=[37 * mm, 105 * mm] if rtl else [105 * mm, 37 * mm],
    )
    details.setStyle(TableStyle([
        ('SPAN', (0, 1), (1, 1)),
        ('SPAN', (0, 2), (1, 2)),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
    ]))
    card = Table(
        [[details, image]] if rtl else [[image, details]],
        colWidths=[152 * mm, 28 * mm] if rtl else [28 * mm, 152 * mm],
    )
    card.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), LIGHT_GREY),
        ('BOX', (0, 0), (-1, -1), 0.6, HexColor('#D9E2EC')),
        ('BACKGROUND', (1, 0), (1, 0), _risk_tint(item)) if not rtl else ('BACKGROUND', (0, 0), (0, 0), _risk_tint(item)),
        ('LINEBEFORE', (0, 0), (0, -1), 3, color) if rtl else ('LINEAFTER', (-1, 0), (-1, -1), 3, color),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    return card


def _primary_points(history, title, chart_spec=None):
    series = history.get(title, {})
    if chart_spec:
        for label in chart_spec.get('series', ()):
            if series.get(label):
                return series[label]
    return next(iter(series.values()), [])


def _common_snapshot(snapshot, record):
    if snapshot:
        return snapshot
    return {
        'demographic': {
            'age': {'question_key': 'age', 'question': 'Age (years)', 'answer': record.age},
            'weight': {'question_key': 'weight', 'question': 'Weight (kg)', 'answer': record.weight},
            'height': {'question_key': 'height', 'question': 'Height (cm)', 'answer': record.height},
            'waist_size': {'question_key': 'waist_size', 'question': 'Waist circumference (cm)', 'answer': record.waist_size},
            'education': {'question_key': 'education', 'question': 'Education level (years)', 'answer': record.education},
            'born_place': {'question_key': 'born_place', 'question': 'Place of birth', 'answer': record.born_place},
            'ethnicity': {'question_key': 'ethnicity', 'question': 'Ethnicity', 'answer': record.ethnicity},
            'blood_group': {'question_key': 'blood_group', 'question': 'Blood group', 'answer': record.blood_group},
        },
        'lifestyle': {},
        'medical': {},
        'assessments': {},
    }


def _localized_snapshot(snapshot, language, selected_assessments, labels):
    """Translate persisted question keys and predefined answer values.

    ``screening_data`` records created before question_key was introduced are
    supported by using the dictionary key as a fallback.  Free-text values
    are returned unchanged by localized_answer.
    """
    assessment_map = {
        item.get('title'): item
        for item in selected_assessments
        if item.get('title')
    }
    def localize_entry(key, entry, assessment_title=None):
        if not isinstance(entry, dict) or 'answer' not in entry:
            return entry
        question_key = entry.get('question_key') or key
        question = localized_question(
            question_key,
            language,
            fallback=entry.get('question'),
        )
        answer = localized_answer(
            question_key,
            entry.get('answer'),
            language,
            not_provided=labels['not_provided'],
        )

        # Status and recommendation are calculated catalog values.  Use the
        # already localized assessment metadata instead of trying to
        # translate arbitrary clinical recommendation text here.
        if assessment_title and key in {'risk_status', 'recommendation'}:
            assessment = assessment_map.get(assessment_title, {})
            if key == 'risk_status':
                answer = assessment.get('display_status') or assessment.get('status_en') or answer
            else:
                answer = assessment.get('display_recommendation') or assessment.get('recommendation_en') or answer

        return {
            **entry,
            'question_key': question_key,
            'question': question,
            'answer': answer,
        }

    localized = {}
    for section_name, section in (snapshot or {}).items():
        if not isinstance(section, dict):
            localized[section_name] = section
            continue
        if section_name == 'assessments':
            localized[section_name] = {
                assessment_title: {
                    key: localize_entry(key, entry, assessment_title)
                    for key, entry in assessment_section.items()
                    if key not in PDF_EXCLUDED_ASSESSMENT_KEYS
                }
                for assessment_title, assessment_section in section.items()
                if isinstance(assessment_section, dict)
            }
            continue
        localized[section_name] = {
            key: localize_entry(key, entry)
            for key, entry in section.items()
        }
    return localized


def _answer_rows(section, labels):
    rows = [[labels['question'], labels['answer']]]
    for entry in section.values():
        if not isinstance(entry, dict) or 'question' not in entry:
            continue
        rows.append([entry.get('question'), entry.get('answer')])
    return rows


def _assessment_answer_rows(section, item, labels):
    """Append localized result status and recommendation to a disease's answers."""
    rows = _answer_rows(section, labels)
    if len(rows) == 1:
        rows.append([labels['no_answers'], ''])

    rows.extend([
        [
            labels['risk_status'],
            item.get('display_status') or item.get('status_en') or labels['not_provided'],
        ],
        [
            labels['recommendation'],
            item.get('display_recommendation') or item.get('recommendation_en') or labels['recommendation_fallback'],
        ],
    ])
    status_row = len(rows) - 2
    recommendation_row = len(rows) - 1
    highlights = {
        status_row: (_risk_tint(item), _risk_color(item)),
        recommendation_row: (HexColor('#EAF3FA'), NAVY),
    }
    return rows, highlights


def _doctor_comment_text(record, labels):
    """Combine legacy and referral comments for the printable report."""
    comments = []
    if getattr(record, "doctor_comment", ""):
        comments.append(record.doctor_comment)
    try:
        referrals = record.doctor_referrals.select_related("doctor").exclude(doctor_comment="")
        for referral in referrals:
            comments.append(f"{referral.doctor.display_name}: {referral.doctor_comment}")
    except AttributeError:
        logger.exception("Unable to load doctor referral comments for screening %s", record.pk)
    return "\n".join(comments) or labels["no_doctor_comment"]


def _verified_doctor_referrals(record):
    """Return reviewed referrals from verified doctors for report signing."""
    try:
        return list(
            record.doctor_referrals.select_related('doctor')
            .filter(status='reviewed', doctor__is_verified=True)
            .exclude(doctor_comment='')
            .order_by('doctor__display_name', 'created')
        )
    except AttributeError:
        logger.exception("Unable to load verified doctor referrals for screening %s", record.pk)
        return []


def _doctor_signature_block(record, labels, styles, rtl=False):
    """Build white signature/seal panels directly below verified doctor notes."""
    blocks = []
    name_style = ParagraphStyle(
        'DoctorSignatureName',
        parent=styles['body'],
        alignment=TA_CENTER,
        fontSize=9,
        leading=11,
        spaceBefore=1 * mm,
    )
    for referral in _verified_doctor_referrals(record):
        doctor = referral.doctor
        signature_path = _image_path(getattr(doctor, 'signature_image', None))
        seal_path = _image_path(getattr(doctor, 'seal_image', None))
        if not signature_path and not seal_path:
            continue

        signature_image = (
            Image(signature_path, width=42 * mm, height=18 * mm, kind='proportional')
            if signature_path else Spacer(1, 18 * mm)
        )
        signature_image.hAlign = 'CENTER'
        signature_content = KeepTogether([
            signature_image,
            HRFlowable(width=48 * mm, thickness=0.55, color=HexColor('#8293A3'),
                       hAlign='CENTER', spaceBefore=1 * mm, spaceAfter=1 * mm),
            Paragraph(_escaped(doctor.display_name, name_style), name_style),
        ])
        seal_image = (
            Image(seal_path, width=25 * mm, height=25 * mm, kind='proportional')
            if seal_path else Spacer(1, 25 * mm)
        )
        seal_image.hAlign = 'CENTER'
        signature_width = CONTENT_WIDTH - 42 * mm
        seal_width = 42 * mm
        cells = [signature_content, seal_image]
        widths = [signature_width, seal_width]
        if rtl:
            cells.reverse()
            widths.reverse()
        table = Table(
            [cells],
            colWidths=widths,
            hAlign='RIGHT' if rtl else 'LEFT',
        )
        table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BACKGROUND', (0, 0), (-1, -1), colors.white),
            ('BOX', (0, 0), (-1, -1), 0.45, HexColor('#D9E2EC')),
            ('LINEABOVE', (0, 0), (-1, 0), 0.8, HexColor('#D9E2EC')),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 7),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 7),
        ]))
        blocks.extend([table, Spacer(1, 1.5 * mm)])
    return blocks


def generate_pdf_report(record, selected_assessments, request=None):
    """Create a complete, branded report for one screening record."""
    language = language_for_request(request) if request else get_language()
    language = normalize_language(language)
    rtl = _is_rtl_language(language)
    labels = _report_labels(language)
    styles = _styles(language)
    organization = _organization_for(record)
    snapshot = _localized_snapshot(
        _common_snapshot(record.get_screening_data(), record),
        language,
        selected_assessments,
        labels,
    )
    history = _history_for_record(record, selected_assessments)
    trend_images = _trend_chart_images(history, selected_assessments, language)

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=15 * mm,
        leftMargin=15 * mm,
        topMargin=25 * mm,
        bottomMargin=20 * mm,
        title=labels['report_title'],
        author='SmartScreening',
    )
    regular, bold = _register_fonts()
    story = []

    organization_title = (
        getattr(organization, f'title_{normalize_language(language)}', None)
        or getattr(organization, 'title', None)
        or 'SmartScreening'
    )
    story.extend([
        Spacer(1, 4 * mm),
        Paragraph(_escaped(labels['report_title']), styles['title']),
        Paragraph(_escaped(organization_title), styles['subtitle']),
        Paragraph(
            _escaped(labels['report_summary']),
            styles['subtitle'],
        ),
    ])

    patient_rows = [
        [labels['report_date'], format_localized_datetime(timezone.now(), language)],
        [labels['patient_code'], record.code or labels['not_provided']],
        [labels['age_gender'], f"{_text(record.age)} / {localized_answer('gender', record.gender, language, labels['not_provided'])}"],
        [labels['screening_date'], format_localized_datetime(record.created, language)],
        [labels['assessments_included'], len(selected_assessments)],
    ]
    story.append(_table(
        [[labels['patient_info'], labels['value']], *patient_rows],
        [60 * mm, 120 * mm],
        styles,
        rtl=rtl,
    ))
    story.append(Spacer(1, 4 * mm))
    story.append(Paragraph(
        _escaped(labels['disclaimer']),
        styles['callout'],
    ))

    story.append(_section_header(labels['results'], styles, rtl=rtl))
    story.append(Spacer(1, 3 * mm))
    for item in selected_assessments:
        story.append(_assessment_card(item, styles, labels, rtl=rtl))
        story.append(Spacer(1, 3 * mm))

    if trend_images:
        story.append(_section_header(labels['history'], styles, rtl=rtl))
        story.append(Spacer(1, 3 * mm))
        story.append(Paragraph(
            _escaped(labels['history_intro']),
            styles['body'],
        ))
        for title, chart_spec, trend_image in trend_images:
            story.append(_chart_panel(title, chart_spec, trend_image, styles, rtl=rtl))
            item = next((item for item in selected_assessments if item['title'] == title), None)
            points = _primary_points(history, title, chart_spec)
            current = points[-1][1] if points else (float(item.get('score') or 0) if item else 0)
            label, delta = _trend(points, current)
            previous = points[-2][1] if len(points) > 1 else None
            change = label if delta is None else f'{label} ({delta:+.2f})'
            story.append(_table([
                [labels['previous'], labels['current'], labels['change']],
                [_text(previous), _text(current), change],
            ], [60 * mm, 60 * mm, 60 * mm], styles, rtl=rtl))
            story.append(Spacer(1, 3 * mm))
    else:
        story.append(_section_header(labels['history'], styles, rtl=rtl))
        story.append(Spacer(1, 3 * mm))
        story.append(Paragraph(
            _escaped(labels['first_history']),
            styles['body'],
        ))

    story.append(PageBreak())
    story.append(_section_header(labels['questions'], styles, rtl=rtl))
    story.append(Spacer(1, 3 * mm))
    story.append(Paragraph(
        _escaped(labels['questions_intro']),
        styles['body'],
    ))
    section_titles = {
        'demographic': labels['demographic'],
        'lifestyle': labels['lifestyle'],
        'medical': labels['medical'],
    }
    for section_name, section_title in section_titles.items():
        story.append(Paragraph(_escaped(section_title), styles['h2']))
        rows = _answer_rows(snapshot.get(section_name, {}), labels)
        if len(rows) > 1:
            story.append(_table(rows, [85 * mm, 95 * mm], styles, rtl=rtl))

    for item in selected_assessments:
        title = item.get('display_title') or item.get('title_en') or item.get('title', '').replace('_', ' ')
        story.append(Paragraph(_escaped(title), styles['h2']))
        assessment_rows, result_row_highlights = _assessment_answer_rows(
            snapshot.get('assessments', {}).get(item.get('title'), {}),
            item,
            labels,
        )
        story.append(_table(
            assessment_rows,
            [85 * mm, 95 * mm],
            styles,
            rtl=rtl,
            highlighted_rows=result_row_highlights,
        ))
        story.append(Spacer(1, 2 * mm))

    story.append(PageBreak())
    doctor_note_block = [
        Paragraph(_escaped(labels['doctor_note']), styles['h2']),
        _table(
            [[labels["clinical_comment"]], [_doctor_comment_text(record, labels)]],
            [CONTENT_WIDTH], styles, header=True,
            rtl=rtl,
        ),
    ]
    signature_blocks = _doctor_signature_block(record, labels, styles, rtl=rtl)
    if signature_blocks:
        doctor_note_block.append(Spacer(1, 1.5 * mm))
        doctor_note_block.extend(signature_blocks)
    story.append(KeepTogether(doctor_note_block))
    story.append(Spacer(1, 7 * mm))
    story.append(Paragraph(_escaped(labels['important']), styles['h2']))
    story.append(Paragraph(
        _escaped(labels['important_text']),
        styles['body'],
    ))

    page_decor = _page_decor(organization, regular, bold, labels, language)
    doc.build(story, onFirstPage=page_decor, onLaterPages=page_decor)
    buffer.seek(0)
    return buffer
