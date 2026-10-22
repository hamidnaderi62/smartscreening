from unittest.mock import Mock, patch

from django.contrib.auth.models import User
from django.test import TestCase, override_settings

from account.models import Organization, Profile
from my_model.models import MyModel

from .models import FollowUpPlan, FollowUpProgram, FollowUpReminder, FollowUpStep, ScreeningReportDelivery
from .services import KavenegarClient, schedule_follow_up_for_screening, schedule_report_sms_for_screening, send_report_sms


class FollowUpSchedulingTests(TestCase):
    def setUp(self):
        self.organization = Organization.objects.create(
            title='Follow-up Organization',
            code='FUPORG',
            slug='follow-up-organization',
        )
        self.user = User.objects.create_user(
            username='followup-user',
            email='followup@example.com',
            password='Strong-password-123',
        )
        Profile.objects.create(
            user=self.user, code='followup-user', phone_number='09121234567',
            organization=self.organization,
        )
        self.screening = MyModel.objects.create(
            userid=self.user,
            code='SCR-1',
            selected_assessments_id='5',
            idf_score=8,
        )

    def test_matching_program_creates_report_delivery_and_step_reminders(self):
        program = FollowUpProgram.objects.create(
            assessment_id=5,
            title='پیگیری دیابت',
            title_en='Diabetes follow-up',
            trigger_statuses='Slightly Increased Risk',
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

        delivery = schedule_report_sms_for_screening(self.screening, language='en')
        plans = schedule_follow_up_for_screening(self.screening, language='en')

        self.assertEqual(len(plans), 1)
        plan = FollowUpPlan.objects.get(screening=self.screening, program=program)
        self.assertEqual(plan.result_status, 'Slightly Increased Risk')
        self.assertEqual(plan.language, 'en')
        self.assertEqual(
            set(FollowUpReminder.objects.filter(plan=plan).values_list('kind', flat=True)),
            {'step'},
        )

    def test_new_organization_sms_settings_are_enabled(self):
        self.assertTrue(self.organization.followup_sms_enabled)
        self.assertTrue(self.organization.pdf_report_sms_enabled)

    def test_disabled_followup_sms_does_not_create_reminders(self):
        self.organization.followup_sms_enabled = False
        self.organization.save(update_fields=('followup_sms_enabled',))
        program = FollowUpProgram.objects.create(
            assessment_id=5,
            title='پیگیری دیابت',
            title_en='Diabetes follow-up',
            trigger_statuses='Slightly Increased Risk',
        )
        FollowUpStep.objects.create(
            program=program, order=1, delay_days=30,
            title='پیگیری آزمایش', title_en='Repeat glucose check',
            message='پیام پیگیری', message_en='Repeat glucose check.',
        )

        schedule_follow_up_for_screening(self.screening, language='en')

        self.assertTrue(FollowUpPlan.objects.exists())
        self.assertFalse(FollowUpReminder.objects.exists())

    def test_disabled_pdf_sms_keeps_followup_steps_enabled(self):
        self.organization.pdf_report_sms_enabled = False
        self.organization.save(update_fields=('pdf_report_sms_enabled',))
        self.assertIsNone(schedule_report_sms_for_screening(self.screening, language='en'))
        self.assertFalse(ScreeningReportDelivery.objects.exists())
        program = FollowUpProgram.objects.create(
            assessment_id=5,
            title='پیگیری دیابت',
            title_en='Diabetes follow-up',
            trigger_statuses='Slightly Increased Risk',
        )
        FollowUpStep.objects.create(
            program=program, order=1, delay_days=30,
            title='پیگیری آزمایش', title_en='Repeat glucose check',
            message='پیام پیگیری', message_en='Repeat glucose check.',
        )

        schedule_follow_up_for_screening(self.screening, language='en')

        self.assertEqual(
            set(FollowUpReminder.objects.values_list('kind', flat=True)),
            {'step'},
        )

    def test_different_risk_programs_can_target_the_same_disease(self):
        low_program = FollowUpProgram.objects.create(
            assessment_id=5, title='ریسک کم', title_en='Low-risk plan',
            trigger_statuses='Low Risk',
        )
        increased_program = FollowUpProgram.objects.create(
            assessment_id=5, title='ریسک افزایش یافته', title_en='Increased-risk plan',
            trigger_statuses='Slightly Increased Risk',
        )

        plans = schedule_follow_up_for_screening(self.screening, language='en')

        self.assertEqual(len(plans), 1)
        self.assertEqual(plans[0].program_id, increased_program.pk)
        self.assertFalse(FollowUpPlan.objects.filter(program=low_program).exists())

    @override_settings(SMARTSCREENING_PUBLIC_URL='https://example.com')
    @patch('followup.services.KavenegarClient.send')
    def test_report_delivery_sends_signed_pdf_link(self, send):
        send.return_value = {'message_id': '9', 'status': 1}
        delivery = schedule_report_sms_for_screening(self.screening, language='en')

        send_report_sms(delivery)

        delivery.refresh_from_db()
        self.assertEqual(delivery.status, 'sent')
        self.assertIn('/en/my_model/reports/pdf/access/', delivery.message)
        send.assert_called_once()

    @patch('followup.services.KavenegarClient.send')
    def test_disabling_sms_cancels_a_queued_reminder_before_delivery(self, send):
        program = FollowUpProgram.objects.create(
            assessment_id=5,
            title='پیگیری دیابت',
            title_en='Diabetes follow-up',
            trigger_statuses='Slightly Increased Risk',
        )
        FollowUpStep.objects.create(
            program=program, order=1, delay_days=30,
            title='پیگیری آزمایش', title_en='Repeat glucose check',
            message='پیام پیگیری', message_en='Repeat glucose check.',
        )
        schedule_follow_up_for_screening(self.screening, language='en')
        reminder = FollowUpReminder.objects.get(kind='step')
        self.organization.followup_sms_enabled = False
        self.organization.save(update_fields=('followup_sms_enabled',))

        from .services import send_follow_up_reminder
        send_follow_up_reminder(reminder)

        reminder.refresh_from_db()
        self.assertEqual(reminder.status, 'cancelled')
        send.assert_not_called()

    def test_program_that_does_not_match_result_is_ignored(self):
        FollowUpProgram.objects.create(
            assessment_id=5,
            title='High-risk only',
            trigger_statuses='High Risk',
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
