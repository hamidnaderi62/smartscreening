from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from account.models import Organization, OrganizationMembership, Profile


User = get_user_model()


class OrganizationDashboardTests(TestCase):
    def setUp(self):
        self.organization = Organization.objects.create(
            title='Test Organization',
            code='TEST',
            slug='test-organization',
        )
        self.admin = User.objects.create_user(
            username='org-admin',
            password='Safe-password-123!',
        )
        Profile.objects.create(
            user=self.admin,
            code='1',
            organization=self.organization,
            is_org_admin=True,
        )
        OrganizationMembership.objects.create(
            user=self.admin,
            organization=self.organization,
            role='admin',
        )

    def test_non_authenticated_user_is_redirected(self):
        response = self.client.get(reverse('cpanel:organization_dashboard_fa'))
        self.assertEqual(response.status_code, 302)

    def test_organization_admin_can_open_dashboard(self):
        self.client.force_login(self.admin)
        response = self.client.get(reverse('cpanel:organization_dashboard_fa'))
        self.assertEqual(response.status_code, 200)

    def test_organization_admin_uses_shared_pages(self):
        self.client.force_login(self.admin)
        for language in ('fa', 'en', 'ar'):
            with self.subTest(language=language):
                dashboard = self.client.get(f'/{language}/cpanel/organization/')
                users = self.client.get(f'/{language}/cpanel/organization/users/')
                reports = self.client.get(f'/{language}/cpanel/organization/reports/')

                self.assertEqual(dashboard.status_code, 200)
                self.assertEqual(users.status_code, 200)
                self.assertEqual(reports.status_code, 200)
                self.assertTemplateUsed(dashboard, 'organization_dashboard.html')
                self.assertTemplateUsed(users, 'admin_users_list.html')
                self.assertTemplateUsed(reports, 'organization_reports.html')

    def test_organization_admin_can_toggle_member_access(self):
        member = User.objects.create_user(
            username='organization-member',
            password='Safe-password-123!',
        )
        membership = OrganizationMembership.objects.create(
            user=member,
            organization=self.organization,
            role='member',
        )
        self.client.force_login(self.admin)

        response = self.client.post(
            reverse('cpanel:toggle_user_status', kwargs={'user_id': member.pk}),
        )

        self.assertRedirects(response, reverse('cpanel:admin_users_list_fa'))
        membership.refresh_from_db()
        self.assertFalse(membership.is_active)

    def test_member_status_action_is_scoped_to_admin_organization(self):
        other_organization = Organization.objects.create(
            title='Other Organization',
            code='OTHER',
            slug='other-organization',
        )
        member = User.objects.create_user(
            username='other-member',
            password='Safe-password-123!',
        )
        OrganizationMembership.objects.create(
            user=member,
            organization=other_organization,
            role='member',
        )
        self.client.force_login(self.admin)
        self.client.raise_request_exception = False

        response = self.client.post(
            reverse('cpanel:toggle_user_status', kwargs={'user_id': member.pk}),
        )

        self.assertEqual(response.status_code, 404)
