import json
from datetime import datetime
from unittest.mock import Mock, patch

import requests

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase
from django.test import override_settings
from django.urls import resolve, reverse

from account.models import Organization, OrganizationMembership, Profile

from .assessment_catalog import ASSESSMENTS
from .forms import AssessmentSelectionForm
from .models import MyModel
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
    _localized_snapshot,
    _shape_rtl,
    _trend_chart_images,
)
from .services.recommendations import get_related_resources
from .services.localization import dashboard_template, localized_reverse, normalize_language
from .services.questionnaire_translations import localized_answer, localized_question
from .services.screening_data import collect_screening_data


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


class LocalizationTests(TestCase):
    def test_dashboard_template_uses_supported_language(self):
        self.assertEqual(dashboard_template('fa'), 'dashboard.html')
        self.assertEqual(dashboard_template('en'), 'dashboard.html')
        self.assertEqual(dashboard_template('ar'), 'dashboard.html')

    def test_unknown_language_falls_back_to_default(self):
        self.assertEqual(normalize_language('fr'), 'fa')
        self.assertEqual(dashboard_template(None), 'dashboard.html')


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
                },
            },
        }

        localized = _localized_snapshot(snapshot, 'en', [], REPORT_LABELS['en'])
        assessment_answers = localized['assessments']['Diabetes']

        self.assertEqual(PDF_EXCLUDED_ASSESSMENT_KEYS, {'risk_score', 'max_score', 'risk_level'})
        self.assertNotIn('risk_score', assessment_answers)
        self.assertNotIn('max_score', assessment_answers)
        self.assertNotIn('risk_level', assessment_answers)
        self.assertIn('risk_status', assessment_answers)


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

    @override_settings(DEBUG=True)
    def test_cleanup_command_removes_screenings_but_preserves_users(self):
        with self.assertRaises(CommandError):
            call_command('clear_screening_data')

        call_command('clear_screening_data', '--confirm')
        self.assertFalse(MyModel.objects.exists())
        self.assertTrue(User.objects.filter(pk=self.user_b.pk).exists())
