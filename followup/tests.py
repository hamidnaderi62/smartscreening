from unittest.mock import Mock, patch

from django.contrib.auth.models import User
from django.test import TestCase, override_settings

from account.models import Profile
from my_model.models import MyModel

from .models import FollowUpPlan, FollowUpProgram, FollowUpReminder, FollowUpStep
from .services import KavenegarClient, schedule_follow_up_for_screening


class FollowUpSchedulingTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='followup-user',
            email='followup@example.com',
            password='Strong-password-123',
        )
        Profile.objects.create(user=self.user, code='followup-user', phone_number='09121234567')
        self.screening = MyModel.objects.create(
            userid=self.user,
            code='SCR-1',
            selected_assessments_id='5',
            idf_score=8,
        )

    def test_matching_program_creates_pdf_and_step_reminders(self):
        program = FollowUpProgram.objects.create(
            assessment_id=5,
            title='پیگیری دیابت',
            title_en='Diabetes follow-up',
            trigger_statuses='Slightly Increased Risk',
            send_pdf_sms=True,
        )
        FollowUpStep.objects.create(
            program=program,
            order=1,
            delay_days=30,
            title='پیگیری آزمایش',
            title_en='Repeat glucose check',
            message='Please repeat your glucose check.',
            message_en='Please repeat your glucose check.',
        )

        plans = schedule_follow_up_for_screening(self.screening, language='en')

        self.assertEqual(len(plans), 1)
        plan = FollowUpPlan.objects.get(screening=self.screening, program=program)
        self.assertEqual(plan.result_status, 'Slightly Increased Risk')
        self.assertEqual(plan.language, 'en')
        self.assertEqual(
            set(FollowUpReminder.objects.filter(plan=plan).values_list('kind', flat=True)),
            {'pdf', 'step'},
        )

    def test_program_that_does_not_match_result_is_ignored(self):
        FollowUpProgram.objects.create(
            assessment_id=5,
            title='High-risk only',
            trigger_statuses='High Risk',
            send_pdf_sms=True,
        )

        schedule_follow_up_for_screening(self.screening, language='en')

        self.assertFalse(FollowUpPlan.objects.exists())


@override_settings(
    KAVENEGAR_API_KEY='test-key',
    KAVENEGAR_SENDER='10001234',
)
class KavenegarClientTests(TestCase):
    @patch('followup.services.requests.post')
    def test_send_parses_successful_provider_response(self, post):
        response = Mock()
        response.json.return_value = {
            'return': {'status': 200, 'message': 'تایید شد'},
            'entries': [{'messageid': 123, 'status': 1, 'statustext': 'ارسال شد'}],
        }
        post.return_value = response

        result = KavenegarClient().send('+989121234567', 'Test message', localid=7)

        self.assertEqual(result['message_id'], '123')
        self.assertEqual(result['status'], 1)
        post.assert_called_once()
        self.assertIn('/v1/test-key/sms/send.json', post.call_args.args[0])
