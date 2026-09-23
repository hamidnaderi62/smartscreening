from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


def create_memberships_from_profiles(apps, schema_editor):
    OrganizationMembership = apps.get_model('account', 'OrganizationMembership')
    Profile = apps.get_model('account', 'Profile')
    Organization = apps.get_model('account', 'Organization')

    for profile in Profile.objects.select_related('organization').filter(
        organization__isnull=False,
    ):
        role = 'admin' if profile.is_org_admin else 'member'
        if profile.organization.admin_user_id == profile.user_id:
            role = 'admin'
        OrganizationMembership.objects.update_or_create(
            user_id=profile.user_id,
            organization_id=profile.organization_id,
            defaults={'role': role, 'is_active': True},
        )

    for organization in Organization.objects.exclude(admin_user_id__isnull=True):
        OrganizationMembership.objects.update_or_create(
            user_id=organization.admin_user_id,
            organization_id=organization.pk,
            defaults={'role': 'admin', 'is_active': True},
        )


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('account', '0007_default_pouyamed_organization'),
    ]

    operations = [
        migrations.CreateModel(
            name='OrganizationMembership',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('role', models.CharField(choices=[('member', 'Member'), ('admin', 'Admin')], default='member', max_length=20)),
                ('is_active', models.BooleanField(default=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('organization', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='memberships', to='account.organization')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='organization_memberships', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'indexes': [
                    models.Index(fields=['organization', 'role', 'is_active'], name='account_org_organiz_2039cd_idx'),
                    models.Index(fields=['user', 'is_active'], name='account_org_user_id_59824e_idx'),
                ],
                'constraints': [
                    models.UniqueConstraint(fields=('user', 'organization'), name='unique_organization_membership'),
                ],
            },
        ),
        migrations.RunPython(create_memberships_from_profiles, migrations.RunPython.noop),
    ]
