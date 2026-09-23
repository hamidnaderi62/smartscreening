from datetime import datetime

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from account.models import Profile
from my_model.models import MyModel
from my_model.services.localization import format_localized_date, format_localized_datetime


User = get_user_model()


class MultilingualRoutingTests(TestCase):
    def test_shared_home_route_is_available_in_all_languages(self):
        for language in ('fa', 'en', 'ar'):
            response = self.client.get(f'/{language}/')
            self.assertEqual(response.status_code, 200)
            self.assertContains(response, f'<html lang="{language}"', html=False)

    def test_language_switch_updates_url_and_profile_preference(self):
        user = User.objects.create_user(username='language-user', password='Safe-password-123!')
        Profile.objects.create(user=user, code='1')
        self.client.force_login(user)

        response = self.client.post(
            reverse('set_language'),
            {'language': 'en', 'next': '/fa/'},
        )

        self.assertRedirects(response, '/en/')
        user.profile.refresh_from_db()
        self.assertEqual(user.profile.language, 'en')


class LocalizedDateTests(TestCase):
    def test_dates_use_the_selected_calendar_and_language(self):
        value = datetime(2026, 9, 22, 19, 30)

        self.assertEqual(format_localized_date(value, 'fa'), '۱۴۰۵/۰۶/۳۱')
        self.assertEqual(format_localized_datetime(value, 'fa'), '۱۴۰۵/۰۶/۳۱ - ۱۹:۳۰')
        self.assertEqual(format_localized_date(value, 'en'), 'Sep 22, 2026')
        self.assertEqual(format_localized_date(value, 'ar'), '22 سبتمبر 2026')


class SmartHomepageTests(TestCase):
    def test_anonymous_homepage_is_a_platform_introduction(self):
        response = self.client.get('/en/')

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home.html')
        self.assertContains(response, 'Understand your health before it becomes urgent.')
        self.assertContains(response, 'smart-home.css')
        self.assertContains(response, 'smart-site-header')
        self.assertContains(response, 'smart-site-footer')
        self.assertContains(response, 'Choose your language')
        self.assertContains(response, 'smart-language-option')
        self.assertContains(response, 'name="language" value="fa"')
        self.assertContains(response, 'name="next" value="/fa/"')
        self.assertContains(response, 'name="next" value="/ar/"')
        self.assertNotContains(response, 'Available screening assessments')
        self.assertNotContains(response, 'Articles and news')

    def test_authenticated_homepage_becomes_personal_dashboard(self):
        user = get_user_model().objects.create_user(
            username='homepage-user',
            first_name='Mina',
            password='Safe-password-123!',
        )
        self.client.force_login(user)

        response = self.client.get('/en/')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Welcome, Mina')
        self.assertContains(response, 'Your latest screening')
        self.assertContains(response, 'You have not completed a screening yet.')

        MyModel.objects.create(
            userid=user,
            code='homepage-user',
            selected_assessments_id='1, 5',
        )
        response = self.client.get('/en/')
        self.assertContains(response, 'Screenings completed')
        self.assertContains(response, 'homepage-user')
        self.assertContains(response, 'View result')
