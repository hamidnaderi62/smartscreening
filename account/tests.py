from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.test import override_settings
from django.urls import reverse

from .models import Organization, OrganizationMembership
from .validators import validate_image_upload
from my_model.services.localization import localized_reverse


User = get_user_model()


class MultilingualLoginStyleTests(TestCase):
    def test_language_routes_use_the_original_login_design(self):
        expected_pages = {
            'fa': 'ورود به حساب کاربری',
            'en': 'Smart Screening - Login',
            'ar': 'تسجيل الدخول',
        }

        for language, marker in expected_pages.items():
            with self.subTest(language=language):
                response = self.client.get(f'/{language}/account/login/')

                self.assertEqual(response.status_code, 200)
                self.assertTemplateUsed(response, 'account/login.html')
                self.assertContains(response, marker)
                self.assertContains(response, 'vendor/font-awesome/css/all.min.css')
                self.assertContains(response, 'css/style-rtl.css')

    def test_language_routes_use_one_registration_design(self):
        expected_markers = {
            'fa': 'ثبت نام',
            'en': 'Sign Up',
            'ar': 'إنشاء حساب',
        }

        for language, marker in expected_markers.items():
            with self.subTest(language=language):
                response = self.client.get(f'/{language}/account/register/')

                self.assertEqual(response.status_code, 200)
                self.assertTemplateUsed(response, 'account/register.html')
                self.assertContains(response, marker)
                self.assertContains(response, 'vendor/font-awesome/css/all.min.css')


class OrganizationRegistrationTests(TestCase):
    def setUp(self):
        self.organization = Organization.objects.create(
            title='Test Organization',
            code='TEST',
            slug='test-organization',
        )

    def test_registration_assigns_user_to_the_linked_organization(self):
        response = self.client.post(
            reverse(
                'account:org_register_fa',
                kwargs={'org_slug': self.organization.slug},
            ),
            {
                'username': 'screening-user',
                'email': 'screening@example.com',
                'password1': 'Safe-password-123!',
                'password2': 'Safe-password-123!',
            },
        )

        self.assertRedirects(
            response,
            localized_reverse(
                'account:organization_home',
                'fa',
                kwargs={'org_slug': self.organization.slug},
            ),
        )
        user = User.objects.get(username='screening-user')
        self.assertEqual(user.profile.organization, self.organization)
        self.assertTrue(
            OrganizationMembership.objects.filter(
                user=user,
                organization=self.organization,
                role='member',
                is_active=True,
            ).exists()
        )

    def test_inactive_organization_cannot_accept_registration(self):
        self.organization.is_active = False
        self.organization.save(update_fields=('is_active',))

        response = self.client.get(
            reverse(
                'account:org_register_fa',
                kwargs={'org_slug': self.organization.slug},
            ),
        )

        self.assertEqual(response.status_code, 404)

    def test_organization_pages_use_one_design_for_all_languages(self):
        for language in ('fa', 'en', 'ar'):
            with self.subTest(language=language):
                home = self.client.get(f'/{language}/account/org/{self.organization.slug}/')
                register = self.client.get(
                    f'/{language}/account/org/{self.organization.slug}/register/',
                )
                login = self.client.get(
                    f'/{language}/account/org/{self.organization.slug}/login/',
                )

                self.assertEqual(home.status_code, 200)
                self.assertEqual(register.status_code, 200)
                self.assertEqual(login.status_code, 200)
                self.assertTemplateUsed(home, 'account/organization_home.html')
                self.assertTemplateUsed(register, 'account/org_register.html')
                self.assertTemplateUsed(login, 'account/org_login.html')
                self.assertContains(register, f'<html lang=\"{language}\"', html=False)
                self.assertContains(login, 'css/style-rtl.css')

    def test_organization_auth_pages_use_localized_branding(self):
        self.organization.title_en = 'North Star Clinic'
        self.organization.sentence_en = 'A dedicated screening portal for your team.'
        self.organization.brand_primary_color = '#123456'
        self.organization.brand_accent_color = '#654321'
        self.organization.brand_surface_color = '#f0f4f8'
        self.organization.save()

        response = self.client.get(
            f'/en/account/org/{self.organization.slug}/login/',
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'North Star Clinic')
        self.assertContains(response, 'A dedicated screening portal for your team.')
        self.assertContains(response, '--org-primary: #123456;')
        self.assertContains(response, '--org-accent: #654321;')
        self.assertContains(response, 'class="btn btn-org-primary mb-0"')
        self.assertContains(response, f'/en/account/org/{self.organization.slug}/register/')

    def test_public_registration_uses_the_same_validation_path(self):
        response = self.client.post(
            reverse('account:register_en'),
            {
                'username': 'public-user',
                'email': 'public@example.com',
                'password1': 'Safe-password-123!',
                'password2': 'Safe-password-123!',
            },
        )

        self.assertRedirects(response, localized_reverse('home:home', 'en'))
        user = User.objects.get(username='public-user')
        self.assertTrue(user.check_password('Safe-password-123!'))

    @override_settings(MAX_LOGIN_ATTEMPTS=2, LOGIN_ATTEMPTS_TIMEOUT=300)
    def test_login_attempts_are_rate_limited(self):
        login_url = reverse('account:login_en')
        for _ in range(2):
            response = self.client.post(
                login_url,
                {'username': 'missing-user', 'password': 'wrong-password'},
            )
            self.assertEqual(response.status_code, 200)

        response = self.client.post(
            login_url,
            {'username': 'missing-user', 'password': 'wrong-password'},
        )
        self.assertEqual(response.status_code, 200)

    def test_invalid_image_upload_is_rejected(self):
        upload = SimpleUploadedFile(
            'not-an-image.txt',
            b'not an image',
            content_type='text/plain',
        )
        with self.assertRaises(ValidationError):
            validate_image_upload(upload)
