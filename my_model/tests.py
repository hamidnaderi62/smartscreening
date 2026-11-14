from io import BytesIO
import json
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

import requests
import numpy as np
from reportlab.lib import colors

from django.contrib.auth import get_user_model
from django.conf import settings
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase
from django.test import override_settings
from django.urls import resolve, reverse
from django.utils import timezone

from account.models import Organization, OrganizationMembership, Profile

from .assessment_catalog import ASSESSMENTS
from .forms import AssessmentSelectionForm
from .models import MyModel, ScreeningReportShortLink
from .services.calculation_inputs import (
    InvalidCalculationInput,
    validate_calculation_input,
)
from .services.assessment_calculations import calculate_selected_assessments
from .services.pdf_reports import (
    generate_screening_pdf,
    selected_assessments_for_record,
)
from .services.report_pdf import (
    DASHBOARD_CHART_CONFIG,
    PDF_EXCLUDED_ASSESSMENT_KEYS,
    REPORT_LABELS,
    _doctor_signature_block,
    _assessment_answer_rows,
    _localized_snapshot,
    _rtl_wrapped_lines,
    _shape_rtl,
    _styles,
    _trend_chart_images,
)
from .services.recommendations import get_related_resources
from .services.localization import dashboard_template, localized_reverse, normalize_language
from .services.report_access import make_report_access_token, report_short_url
from .services.questionnaire_translations import localized_answer, localized_question
from .services.screening_data import collect_screening_data
from .services.serialization import convert_numpy_to_python


class MultilingualScreeningStyleTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='screening-style-user',
            password='Safe-password-123!',
        )
        self.client.force_login(self.user)

    def test_language_routes_use_one_screening_design(self):
        expected_markers = {
            'fa': 'برنامه‌های غربالگری',
            'en': 'Screening Plans',
            'ar': 'خطط الفحص',
        }

        for language, marker in expected_markers.items():
            with self.subTest(language=language):
                response = self.client.get(f'/{language}/my_model/screenings/')

                self.assertEqual(response.status_code, 200)
                self.assertTemplateUsed(response, 'screening_list.html')
                self.assertContains(response, marker)
                self.assertContains(response, 'vendor/font-awesome/css/all.min.css')

    def test_old_screening_list_url_remains_available(self):
        response = self.client.get('/fa/my_model/screening_list')

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'screening_list.html')


class MultilingualQuestionnaireStyleTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='questionnaire-style-user',
            password='Safe-password-123!',
        )
        self.client.force_login(self.user)

    def test_language_questionnaires_use_one_template_and_preserve_form(self):
        expected_languages = {'fa': 'fa', 'en': 'en', 'ar': 'ar'}
        for language, submitted_language in expected_languages.items():
            with self.subTest(language=language):
                response = self.client.post(
                    f'/{language}/my_model/question_{language}',
                    {'selected_assessments': ['1']},
                )

                self.assertEqual(response.status_code, 200)
                self.assertTemplateUsed(response, 'my_model.html')
                self.assertContains(
                    response,
                    f'name="lang" value="{submitted_language}"',
                )
                self.assertContains(
                    response,
                    'js/questionnaire-translations.js',
                )
                self.assertContains(response, 'name="age"')

    def test_questionnaire_language_switch_uses_canonical_route(self):
        response = self.client.post(
            '/fa/my_model/question_fa',
            {'selected_assessments': ['1']},
        )

        self.assertContains(response, 'value="/en/my_model/screenings/questions/"')

        response = self.client.get('/en/my_model/screenings/questions/')

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'my_model.html')
        self.assertContains(response, 'name="lang" value="en"')


class LocalizationTests(TestCase):
    def test_dashboard_template_uses_supported_language(self):
        self.assertEqual(dashboard_template('fa'), 'dashboard.html')
        self.assertEqual(dashboard_template('en'), 'dashboard.html')
        self.assertEqual(dashboard_template('ar'), 'dashboard.html')

    def test_unknown_language_falls_back_to_default(self):
        self.assertEqual(normalize_language('fr'), 'fa')
        self.assertEqual(dashboard_template(None), 'dashboard.html')


class SerializationTests(TestCase):
    def test_numpy_scalars_and_keys_are_json_safe(self):
        payload = {
            np.int64(7): np.int64(12),
            'values': [np.float64(2.5), np.bool_(True)],
        }

        converted = convert_numpy_to_python(payload)

        self.assertEqual(converted, {7: 12, 'values': [2.5, True]})
        json.dumps(converted)


class ScreeningDataTests(TestCase):
    def test_snapshot_builder_groups_common_and_assessment_answers(self):
        data = {
            'age': 45,
            'born_place': 'Tehran',
            'family_ovarian_cancer': 'No',
            'ovarian_cancer_score': 3.5,
        }

        snapshot = collect_screening_data([ASSESSMENTS[8]], data)

        self.assertEqual(snapshot['demographic']['age']['answer'], 45)
        self.assertEqual(snapshot['demographic']['age']['question_key'], 'age')
        self.assertEqual(snapshot['assessments']['Ovarian_Cancer']['family_ovarian_cancer']['answer'], 'No')
        self.assertEqual(snapshot['assessments']['Ovarian_Cancer']['ovarian_score']['answer'], 3.5)

    def test_snapshot_builder_does_not_require_a_request_object(self):
        snapshot = collect_screening_data([], {'age': 40})

        self.assertEqual(snapshot['demographic']['age']['answer'], 40)
        self.assertEqual(snapshot['assessments'], {})

    def test_questions_and_predefined_answers_are_localized_for_pdf(self):
        snapshot = collect_screening_data(
            [ASSESSMENTS[8]],
            {
                'age': 45,
                'cereal': 'Yes',
                'family_ovarian_cancer': 'No',
                'ovarian_cancer_score': 3.5,
            },
        )

        for language, question, yes, no in (
            ('en', 'Age (years)', 'Yes', 'No'),
            ('fa', 'سن (سال)', 'بله', 'خیر'),
            ('ar', 'العمر (بالسنوات)', 'نعم', 'لا'),
        ):
            with self.subTest(language=language):
                localized = _localized_snapshot(
                    snapshot,
                    language,
                    [],
                    REPORT_LABELS[language],
                )
                self.assertEqual(localized['demographic']['age']['question'], question)
                self.assertEqual(localized_answer('cereal', 'Yes', language), yes)
                self.assertEqual(localized_answer('family_ovarian_cancer', 'No', language), no)

        self.assertEqual(localized_question('age', 'fa'), 'سن (سال)')

    def test_numeric_option_values_render_as_option_text_in_pdf_languages(self):
        cases = (
            (ASSESSMENTS[2], 'priorbiopsy', 'Prior negative biopsy', {
                'en': 'Prior negative biopsy',
                'fa': 'نمونه‌برداری قبلی با نتیجه منفی',
                'ar': 'خزعة سابقة بنتيجة سلبية',
            }),
            (ASSESSMENTS[6], 'moles_count', '3', {
                'en': 'Between 6 and 10 moles',
                'fa': 'بین ۶ تا ۱۰ خال',
                'ar': 'من 6 إلى 10 شامات',
            }),
            (ASSESSMENTS[9], 'fastfood', '4', {
                'en': 'More than 5 meals',
                'fa': 'بیش از ۵ وعده',
                'ar': 'أكثر من 5 وجبات',
            }),
            (ASSESSMENTS[9], 'cannedfood', '2', {
                'en': 'One serving',
                'fa': 'یک وعده',
                'ar': 'حصة واحدة',
            }),
        )
        for assessment, field, raw_value, expected_by_language in cases:
            snapshot = collect_screening_data(
                [assessment],
                {field: raw_value},
            )
            for language, expected in expected_by_language.items():
                with self.subTest(field=field, language=language):
                    localized = _localized_snapshot(
                        snapshot,
                        language,
                        [],
                        REPORT_LABELS[language],
                    )
                    self.assertEqual(
                        localized['assessments'][assessment['title']][field]['answer'],
                        expected,
                    )

    def test_pdf_localization_keeps_legacy_snapshots_readable(self):
        legacy_snapshot = {
            'demographic': {
                'age': {'question': 'Age', 'answer': 45},
            },
            'assessments': {},
        }

        localized = _localized_snapshot(
            legacy_snapshot,
            'ar',
            [],
            REPORT_LABELS['ar'],
        )

        self.assertEqual(localized['demographic']['age']['question'], 'العمر (بالسنوات)')
        self.assertEqual(localized['demographic']['age']['answer'], 45)

    def test_pdf_hides_internal_score_fields_from_question_answers(self):
        snapshot = {
            'demographic': {},
            'lifestyle': {},
            'medical': {},
            'assessments': {
                'Diabetes': {
                    'risk_score': {'question': 'Risk Score', 'answer': 8},
                    'max_score': {'question': 'Maximum Score', 'answer': 30},
                    'risk_level': {'question': 'Risk Level', 'answer': 'bg-warning'},
                    'risk_status': {'question': 'Risk Status', 'answer': 'Moderate'},
                    'recommendation': {'question': 'Doctor Recommendation', 'answer': 'Follow up'},
                    'idf_score': {'question': 'Diabetes Risk Score', 'answer': 9},
                },
            },
        }

        localized = _localized_snapshot(snapshot, 'en', [], REPORT_LABELS['en'])
        assessment_answers = localized['assessments']['Diabetes']

        self.assertTrue({'risk_score', 'max_score', 'risk_level', 'risk_status', 'recommendation', 'idf_score'} <= PDF_EXCLUDED_ASSESSMENT_KEYS)
        self.assertNotIn('risk_score', assessment_answers)
        self.assertNotIn('max_score', assessment_answers)
        self.assertNotIn('risk_level', assessment_answers)
        self.assertNotIn('risk_status', assessment_answers)
        self.assertNotIn('recommendation', assessment_answers)
        self.assertNotIn('idf_score', assessment_answers)

    def test_disease_question_table_ends_with_status_and_recommendation(self):
        labels = REPORT_LABELS['en']
        rows, highlights = _assessment_answer_rows(
            {'age': {'question': 'Age', 'answer': 45}},
            {
                'display_status': 'Moderate risk',
                'display_recommendation': 'Discuss with a clinician.',
            },
            labels,
        )

        self.assertEqual(rows[-2], [labels['risk_status'], 'Moderate risk'])
        self.assertEqual(rows[-1], [labels['recommendation'], 'Discuss with a clinician.'])
        self.assertEqual(set(highlights), {len(rows) - 2, len(rows) - 1})
        self.assertNotEqual(highlights[len(rows) - 2][0], highlights[len(rows) - 1][0])


class UrlOwnershipTests(TestCase):
    def test_report_routes_are_owned_by_report_views(self):
        report_route = resolve(reverse('my_model:dashboard_fa'))
        calculation_route = resolve(reverse('my_model:calculate_my_model'))

        self.assertEqual(report_route.func.__module__, 'my_model.report_views')
        self.assertEqual(calculation_route.func.__module__, 'my_model.views')


User = get_user_model()


class AssessmentSelectionFormTests(TestCase):
    def test_selection_uses_catalog_ids(self):
        form = AssessmentSelectionForm(
            data={'selected_assessments': ['1', '10']},
            allowed_assessments=ASSESSMENTS,
        )

        self.assertTrue(form.is_valid())
        self.assertEqual(
            [assessment['id'] for assessment in form.cleaned_data['selected_assessments']],
            [1, 10],
        )

    def test_unknown_selection_is_rejected(self):
        form = AssessmentSelectionForm(
            data={'selected_assessments': ['999']},
            allowed_assessments=ASSESSMENTS,
        )

        self.assertFalse(form.is_valid())


class RecommendationServiceTests(TestCase):
    @patch('my_model.services.recommendations.requests.get')
    def test_external_recommendations_use_timeout_and_return_json(self, get):
        first_response = Mock(content=b'content')
        first_response.json.return_value = [{'title': 'Article'}]
        second_response = Mock(content=b'doctors')
        second_response.json.return_value = [{'name': 'Doctor'}]
        get.side_effect = [first_response, second_response]

        contents, doctors = get_related_resources(
            'https://example.test/api/',
            tags='cancer risk',
            speciality=1,
        )

        self.assertEqual(contents, [{'title': 'Article'}])
        self.assertEqual(doctors, [{'name': 'Doctor'}])
        self.assertEqual(get.call_args_list[0].kwargs['timeout'], 5)
        self.assertEqual(get.call_args_list[0].kwargs['params'], {'q': 'cancer risk'})

    @patch(
        'my_model.services.recommendations.requests.get',
        side_effect=requests.RequestException('network'),
    )
    def test_external_recommendations_fail_closed(self, get):
        contents, doctors = get_related_resources(
            'https://example.test/api',
            tags='cancer risk',
            speciality=1,
        )

        self.assertEqual(contents, [])
        self.assertEqual(doctors, [])


class CalculationInputTests(TestCase):
    def test_missing_common_input_is_rejected_before_calculation(self):
        with self.assertRaises(InvalidCalculationInput):
            validate_calculation_input({}, [])

    def test_invalid_numeric_input_is_rejected(self):
        common_fields = {
            'age', 'weight', 'height', 'waist_size', 'ethnicity', 'born_place',
            'education', 'blood_group', 'activity', 'smoking', 'alcohol', 'meat',
            'cereal', 'vegetables', 'dairy', 'multivitamin', 'blood_pressure',
            'blood_glucose', 'totchol', 'previous_cancer',
        }
        data = {field_name: '1' for field_name in common_fields}
        data['age'] = 'not-a-number'

        with self.assertRaises(InvalidCalculationInput):
            validate_calculation_input(data, [])


class AssessmentCalculationServiceTests(TestCase):
    def setUp(self):
        self.shared_data = {
            'gender': 'Male', 'age': 45, 'weight': 70, 'height': 165,
            'waist_size': 80, 'ethnicity': 1, 'born_place': 'Tehran',
            'education': 16, 'activity': 1, 'smoking': 0, 'alcohol': 0,
            'meat': 1, 'cereal': 'Yes', 'vegetables': 'Yes', 'dairy': 1,
            'multivitamin': 'No', 'blood_pressure': 'No', 'blood_glucose': 'No',
            'totchol': 180, 'blood_group': 'O+', 'previous_cancer': 'No',
        }

    @patch('my_model.services.assessment_calculations.Diabetes.calculate_risk')
    def test_diabetes_branch_receives_shared_birth_place(self, calculate_risk):
        calculate_risk.return_value = {
            'ausdrisk_score': 1, 'idf_score': 2, 'uk_score': 3, 'ada_score': 4,
            'ausdrisk_status': 'Low', 'idf_status': 'Low',
            'uk_status': 'Low', 'ada_status': 'Low',
        }

        calculate_selected_assessments(
            {'relatives_diabetes': 'No'},
            [ASSESSMENTS[4]],
            self.shared_data,
        )

        self.assertEqual(calculate_risk.call_args.args[10], 1)
        self.assertEqual(calculate_risk.call_args.args[11], 'Tehran')

    @patch('my_model.services.assessment_calculations.Pancreatic_RiskCalculator.calculate_risk')
    def test_pancreatic_branch_receives_shared_blood_group(self, calculate_risk):
        calculate_risk.return_value = 4

        calculate_selected_assessments(
            {'family_pancreatic_cancer': 'No', 'chronic_pancreatitis': 'No'},
            [ASSESSMENTS[11]],
            self.shared_data,
        )

        self.assertEqual(calculate_risk.call_args.args[5], 'O+')


class PdfReportServiceTests(TestCase):
    @patch('my_model.services.report_pdf._verified_doctor_referrals')
    def test_doctor_signature_name_is_below_signature_on_white_background(
        self, referrals,
    ):
        referral = Mock()
        referral.doctor.display_name = 'Dr. Example'
        referral.doctor.signature_image = 'signature.png'
        referral.doctor.seal_image = 'seal.png'
        referrals.return_value = [referral]

        image_path = str(settings.BASE_DIR / 'assets/images/pattern/04.png')
        with patch('my_model.services.report_pdf._image_path', return_value=image_path):
            for rtl in (False, True):
                with self.subTest(rtl=rtl):
                    blocks = _doctor_signature_block(None, {}, _styles('ar' if rtl else 'en'), rtl=rtl)
                    self.assertEqual(len(blocks), 2)
                    table = blocks[0]
                    signature_column = 1 if rtl else 0
                    signature_stack = table._cellvalues[0][signature_column]
                    self.assertEqual(signature_stack._content[-1].getPlainText(), 'Dr. Example')
                    table.wrap(600, 600)
                    white_background = any(
                        command[0] == 'BACKGROUND' and command[3] == colors.white
                        for command in table._bkgrndcmds
                    )
                    self.assertTrue(white_background)

    def test_rtl_paragraphs_wrap_in_logical_word_order(self):
        text = REPORT_LABELS['fa']['important_text']
        lines = _rtl_wrapped_lines(text, _styles('fa')['body'])

        self.assertGreater(len(lines), 1)
        self.assertTrue(lines[0].startswith('نتایج غربالگری'))
        self.assertEqual(' '.join(lines).split(), text.split())

    def test_persian_and_arabic_text_is_shaped_for_reportlab(self):
        source = 'سابقه سرطان تخمدان'
        shaped = _shape_rtl(source)

        self.assertNotEqual(shaped, source)
        self.assertTrue(any(0xFE70 <= ord(character) <= 0xFEFF for character in shaped))

    def test_pdf_history_chart_config_matches_comprehensive_dashboard(self):
        breast_charts = DASHBOARD_CHART_CONFIG['Breast_Cancer']
        self.assertEqual([chart['type'] for chart in breast_charts], ['line', 'line'])
        self.assertEqual(breast_charts[0]['colors'], ('#77B6EA', '#545454'))
        self.assertEqual(DASHBOARD_CHART_CONFIG['Colorectal_Cancer'][0]['type'], 'bar')
        self.assertEqual(DASHBOARD_CHART_CONFIG['Prostate_Cancer'][0]['type'], 'bar')
        self.assertEqual(
            DASHBOARD_CHART_CONFIG['Prostate_Cancer'][0]['colors'],
            ('#FF0000', '#FFA500', '#00FF00'),
        )
        self.assertEqual(DASHBOARD_CHART_CONFIG['Diabetes'][0]['colors'], ('#3F51B5',))

    def test_pdf_history_chart_renderer_supports_dashboard_chart_types(self):
        history = {
            'Colorectal_Cancer': {
                'PREMM score': [(datetime(2025, 1, 1), 4.0), (datetime(2026, 1, 1), 6.0)],
                'CRCPro score': [],
            },
            'Prostate_Cancer': {
                'High-grade cancer risk': [(datetime(2025, 1, 1), 2.0)],
                'Low-grade cancer risk': [(datetime(2025, 1, 1), 3.0)],
                'No cancer risk': [(datetime(2025, 1, 1), 95.0)],
            },
        }

        images = _trend_chart_images(history, [ASSESSMENTS[1], ASSESSMENTS[2]])

        self.assertEqual([chart[1]['type'] for chart in images], ['bar', 'bar'])
        self.assertTrue(all(chart[2].read(8) == b'\x89PNG\r\n\x1a\n' for chart in images))

    def test_selected_assessments_include_stored_scores(self):
        user = User.objects.create_user(username='pdf-user')
        record = MyModel.objects.create(
            userid=user,
            selected_assessments_id='1, 10',
            mymodel_gail_score=2.5,
            stomach_cancer_score=8,
        )

        selected = selected_assessments_for_record(record, ASSESSMENTS)

        self.assertEqual(
            [assessment['title'] for assessment in selected],
            ['Breast_Cancer', 'Stomach_Cancer'],
        )
        self.assertEqual(selected[0]['score'], 2.5)
        self.assertEqual(selected[1]['score'], 8)
        self.assertIn('recommendation_en', selected[1])

    def test_pdf_contains_report_structure_and_history(self):
        user = User.objects.create_user(username='report-user')
        MyModel.objects.create(
            userid=user,
            code='report-user',
            selected_assessments_id='9',
            ovarian_cancer_score=8,
            screening_data={
                'demographic': {'age': {'question': 'Age', 'answer': 45}},
                'lifestyle': {},
                'medical': {},
                'assessments': {
                    'Ovarian_Cancer': {
                        'family_ovarian_cancer': {
                            'question': 'Family history', 'answer': 'No',
                        },
                    },
                },
            },
        )
        record = MyModel.objects.create(
            userid=user,
            code='report-user',
            selected_assessments_id='9',
            ovarian_cancer_score=14,
            doctor_comment='Continue follow-up with your physician.',
            screening_data={
                'demographic': {'age': {'question': 'Age', 'answer': 45}},
                'lifestyle': {},
                'medical': {},
                'assessments': {
                    'Ovarian_Cancer': {
                        'family_ovarian_cancer': {
                            'question': 'Family history', 'answer': 'No',
                        },
                    },
                },
            },
        )

        pdf_buffer, filename = generate_screening_pdf(record, ASSESSMENTS, None)

        self.assertTrue(filename.startswith('screening_report_report-user_'))
        self.assertEqual(pdf_buffer.read(5), b'%PDF-')


class ScreeningAuthorizationTests(TestCase):
    def setUp(self):
        self.organization_a = Organization.objects.create(
            title='Organization A', code='ORGA', slug='organization-a',
        )
        self.organization_b = Organization.objects.create(
            title='Organization B', code='ORGB', slug='organization-b',
        )
        self.admin_a = User.objects.create_user(
            username='admin-a', password='Safe-password-123!',
        )
        self.user_b = User.objects.create_user(
            username='user-b', password='Safe-password-123!',
        )
        Profile.objects.create(
            user=self.admin_a,
            code='1',
            organization=self.organization_a,
            is_org_admin=True,
        )
        OrganizationMembership.objects.create(
            user=self.admin_a,
            organization=self.organization_a,
            role='admin',
        )
        Profile.objects.create(
            user=self.user_b,
            code='2',
            organization=self.organization_b,
        )
        OrganizationMembership.objects.create(
            user=self.user_b,
            organization=self.organization_b,
            role='member',
        )
        self.screening = MyModel.objects.create(
            userid=self.user_b,
            code='2',
            selected_assessments_id='1',
            screening_data={'assessments': {}},
        )

    def test_organization_admin_cannot_view_other_organization_report(self):
        self.client.force_login(self.admin_a)
        self.client.raise_request_exception = False
        response = self.client.get(
            reverse(
                'my_model:dashboard_comprehensive_fa',
                kwargs={'code': self.screening.code},
            ),
            {'user_id': self.user_b.pk},
        )
        self.assertEqual(response.status_code, 403)

    def test_organization_admin_cannot_update_other_organization_comment(self):
        self.client.force_login(self.admin_a)
        self.client.raise_request_exception = False
        response = self.client.post(
            reverse('my_model:save_doctor_comment'),
            data=json.dumps({
                'my_model_id': self.screening.pk,
                'doctor_comment': 'unauthorized',
            }),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 403)
        self.screening.refresh_from_db()
        self.assertEqual(self.screening.doctor_comment, None)

    def test_deactivated_member_cannot_view_own_report(self):
        OrganizationMembership.objects.filter(
            user=self.user_b,
            organization=self.organization_b,
        ).update(is_active=False)
        self.client.force_login(self.user_b)
        self.client.raise_request_exception = False

        response = self.client.get(
            reverse(
                'my_model:dashboard_comprehensive_fa',
                kwargs={'code': self.screening.code},
            ),
        )

        self.assertEqual(response.status_code, 403)

    def test_anonymous_user_cannot_start_screening(self):
        response = self.client.get(reverse('my_model:screening_list_fa'))
        self.assertEqual(response.status_code, 302)

    def test_invalid_doctor_comment_payload_returns_bad_request(self):
        self.client.force_login(self.admin_a)
        response = self.client.post(
            reverse('my_model:save_doctor_comment'),
            data=json.dumps({'my_model_id': self.screening.pk}),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 400)

    def test_unauthorized_pdf_download_is_forbidden(self):
        self.client.force_login(self.admin_a)
        self.client.raise_request_exception = False
        response = self.client.get(
            reverse(
                'my_model:download_pdf_report',
                kwargs={'model_id': self.screening.pk},
            ),
        )
        self.assertEqual(response.status_code, 403)

    @patch('my_model.views.generate_screening_pdf')
    def test_signed_report_link_allows_anonymous_pdf_access(self, generate_pdf):
        generate_pdf.return_value = (BytesIO(b'%PDF-test'), 'screening.pdf')
        token = make_report_access_token(self.screening, 'en')
        self.client.logout()

        response = self.client.get(
            reverse('my_model:pdf_report_access', kwargs={'token': token}),
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        generate_pdf.assert_called_once()

    def test_tampered_signed_report_link_is_not_found(self):
        response = self.client.get(
            reverse('my_model:pdf_report_access', kwargs={'token': 'tampered-token'}),
        )

        self.assertEqual(response.status_code, 404)

    @patch('my_model.views.generate_screening_pdf')
    def test_short_report_link_is_compact_and_allows_anonymous_pdf_access(self, generate_pdf):
        generate_pdf.return_value = (BytesIO(b'%PDF-test'), 'screening.pdf')
        path = report_short_url(self.screening, 'en')
        self.client.logout()

        response = self.client.get(path)

        self.assertTrue(path.startswith('/r/'))
        self.assertLess(len(path), 25)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        self.assertEqual(generate_pdf.call_args.args[2].LANGUAGE_CODE, 'en')
        link = ScreeningReportShortLink.objects.get(screening=self.screening)
        self.assertEqual(len(link.token_hash), 64)

    @override_settings(REPORT_ACCESS_TOKEN_MAX_AGE=10)
    def test_expired_short_report_link_is_not_found(self):
        path = report_short_url(self.screening, 'fa')
        ScreeningReportShortLink.objects.filter(screening=self.screening).update(
            created=timezone.now() - timedelta(seconds=11),
        )

        response = self.client.get(path)

        self.assertEqual(response.status_code, 404)

    def test_missing_pdf_record_is_not_found(self):
        self.client.force_login(self.admin_a)
        self.client.raise_request_exception = False
        response = self.client.get(
            reverse(
                'my_model:download_pdf_report',
                kwargs={'model_id': 999999},
            ),
        )
        self.assertEqual(response.status_code, 404)

    def test_unknown_assessment_id_returns_not_found(self):
        self.client.force_login(self.admin_a)
        response = self.client.get(
            reverse(
                'my_model:dashboard_detail_fa',
                kwargs={'assessment_id': 999},
            ),
        )
        self.assertEqual(response.status_code, 404)

    def test_comprehensive_report_matches_exact_assessment_ids(self):
        MyModel.objects.create(
            userid=self.admin_a,
            code='1',
            selected_assessments_id='10',
            stomach_cancer_score=4,
            screening_data={'assessments': {}},
        )
        self.client.force_login(self.admin_a)
        response = self.client.get(
            reverse(
                'my_model:dashboard_comprehensive_fa',
                kwargs={'code': '1'},
            ),
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dashboard_comprehensive.html')
        self.assertNotIn('gail_score_abs_5_history', response.context)
        self.assertEqual(response.context['stomach_cancer_score_history'], [4.0])

    @patch(
        'my_model.report_views.get_related_resources',
        return_value=([], []),
    )
    def test_arabic_detail_report_uses_shared_score_history(self, get_related_resources):
        MyModel.objects.create(
            userid=self.admin_a,
            code='1',
            selected_assessments_id='1',
            gail_score_abs_5=0,
        )
        self.client.force_login(self.admin_a)
        response = self.client.get(
            reverse(
                'my_model:dashboard_detail_ar',
                kwargs={'assessment_id': 1},
            ),
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dashboard_detail.html')
        self.assertContains(response, 'خطر الإصابة بسرطان الثدي لمدة 5 سنوات')
        self.assertEqual(response.context['gail_score_abs_5_history'], [0.0])
        get_related_resources.assert_called_once()

    def test_calculation_endpoint_only_accepts_post(self):
        self.client.force_login(self.admin_a)
        response = self.client.get(reverse('my_model:calculate_my_model'))
        self.assertEqual(response.status_code, 405)

    def test_invalid_calculation_input_returns_to_questions(self):
        self.client.force_login(self.admin_a)
        response = self.client.post(
            reverse('my_model:calculate_my_model'),
            {'lang': 'en'},
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, localized_reverse('my_model:question', 'en'))

    @patch(
        'my_model.services.assessment_calculations.Ovarian_RiskCalculator.calculate_risk',
        return_value=7,
    )
    def test_ovarian_calculation_loads_shared_inputs_independently(self, calculate_risk):
        self.client.force_login(self.admin_a)
        session = self.client.session
        session['selected_assessments'] = [ASSESSMENTS[8]]
        session.save()

        response = self.client.post(
            reverse('my_model:calculate_my_model'),
            {
                'lang': 'fa',
                'age': '45', 'weight': '70', 'height': '165', 'waist_size': '80',
                'ethnicity': '1', 'born_place': 'Tehran', 'education': '16',
                'blood_group': 'O', 'activity': '1', 'smoking': '0', 'alcohol': '0',
                'meat': '1', 'cereal': 'Yes', 'vegetables': 'Yes', 'dairy': '1',
                'multivitamin': 'No', 'blood_pressure': 'No', 'blood_glucose': 'No',
                'totchol': '180', 'previous_cancer': 'No',
                'family_breast_ovarian_prostate': 'No', 'family_ovarian_cancer': 'No',
                'gene_mutation': 'No', 'talcum_powder': 'No',
                'hormonal_contraceptives_years': '0', 'num_pregnancies': '2',
                'breastfeeding': 'Yes', 'menopause': 'No', 'menopause_hormone': '0',
                'hysterectomy': 'No', 'endometriosis': 'No', 'salpingectomy': 'No',
            },
        )

        self.assertEqual(response.status_code, 200)
        calculate_risk.assert_called_once()
        self.assertTrue(
            MyModel.objects.filter(
                userid=self.admin_a,
                selected_assessments_id='9',
                ovarian_cancer_score=7,
            ).exists()
        )

    def test_numpy_calculator_results_are_json_safe_during_calculation(self):
        self.client.force_login(self.admin_a)
        session = self.client.session
        session['selected_assessments'] = [ASSESSMENTS[2]]
        session.save()

        response = self.client.post(
            reverse('my_model:calculate_my_model'),
            {
                'lang': 'fa',
                'age': '55', 'weight': '80', 'height': '175', 'waist_size': '90',
                'ethnicity': '1', 'born_place': 'Tehran', 'education': '16',
                'blood_group': 'O+', 'activity': '1', 'smoking': '0', 'alcohol': '0',
                'meat': '1', 'cereal': 'Yes', 'vegetables': 'every_day', 'dairy': '1',
                'multivitamin': 'No', 'blood_pressure': 'No', 'blood_glucose': 'No',
                'totchol': '180', 'previous_cancer': 'No',
                'psa': '3', 'famhistory': 'No', 'dre': 'Normal',
                'priorbiopsy': 'No',
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            MyModel.objects.filter(
                userid=self.admin_a,
                selected_assessments_id='3',
            ).exists()
        )

    @override_settings(DEBUG=True)
    def test_cleanup_command_removes_screenings_but_preserves_users(self):
        with self.assertRaises(CommandError):
            call_command('clear_screening_data')

        call_command('clear_screening_data', '--confirm')
        self.assertFalse(MyModel.objects.exists())
        self.assertTrue(User.objects.filter(pk=self.user_b.pk).exists())
