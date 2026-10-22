from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from my_model.models import MyModel
from my_model.services.report_pdf import _doctor_comment_text, _report_labels

from .models import DoctorProfile, DoctorReferral, DoctorSpecialization
from .services import suggest_doctors_for_assessment


User = get_user_model()


class DoctorReferralTests(TestCase):
    def setUp(self):
        self.patient = User.objects.create_user(username='patient', password='pass12345')
        self.doctor_user = User.objects.create_user(username='doctor', password='pass12345')
        self.specialization = DoctorSpecialization.objects.create(
            code='diabetes', title='Diabetes', assessment_ids=[5],
        )
        self.doctor = DoctorProfile.objects.create(
            user=self.doctor_user, display_name='Dr. Test', license_number='LIC-1',
            is_verified=True,
        )
        self.doctor.specializations.add(self.specialization)
        self.screening = MyModel.objects.create(
            userid=self.patient, code='SCR-1', selected_assessments_id='5',
            idf_score=12, idf_status='Moderate risk', screening_data={},
        )

    def test_suggestion_matches_specialty(self):
        self.assertEqual(suggest_doctors_for_assessment(5), [self.doctor])
        self.assertEqual(suggest_doctors_for_assessment(6), [])

    def test_user_can_create_referral_and_doctor_can_comment(self):
        self.client.force_login(self.patient)
        response = self.client.post(reverse('doctor:create_referral', kwargs={
            'screening_id': self.screening.pk,
            'doctor_id': self.doctor.pk,
            'assessment_id': 5,
        }), {'patient_message': 'Please review this result.'})
        self.assertEqual(response.status_code, 302)
        referral = DoctorReferral.objects.get()
        self.assertEqual(referral.patient, self.patient)

        self.client.force_login(self.doctor_user)
        response = self.client.post(reverse('doctor:save_comment', kwargs={'referral_id': referral.pk}), {
            'doctor_comment': 'Please arrange a clinical follow-up appointment.',
        })
        self.assertEqual(response.status_code, 302)
        referral.refresh_from_db()
        self.assertEqual(referral.status, DoctorReferral.STATUS_REVIEWED)
        self.assertIn('clinical follow-up', referral.doctor_comment)
        self.assertIn('Dr. Test', _doctor_comment_text(self.screening, _report_labels('en')))

    def test_doctor_cannot_open_another_doctors_referral(self):
        other_user = User.objects.create_user(username='other', password='pass12345')
        other_doctor = DoctorProfile.objects.create(
            user=other_user, display_name='Dr. Other', license_number='LIC-2', is_verified=True,
        )
        referral = DoctorReferral.objects.create(
            patient=self.patient, screening=self.screening, doctor=other_doctor,
            assessment_id=5,
        )
        self.client.force_login(self.doctor_user)
        response = self.client.get(reverse('doctor:referral_detail', kwargs={'referral_id': referral.pk}))
        self.assertEqual(response.status_code, 404)
