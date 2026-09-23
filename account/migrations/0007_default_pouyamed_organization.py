from django.db import migrations


def create_default_organization(apps, schema_editor):
    Organization = apps.get_model('account', 'Organization')
    Organization.objects.get_or_create(
        slug='pouyamed',
        defaults={
            'title': 'pouyamed',
            'code': 'POUYAMED',
            'sentence': 'پلتفرم غربالگری هوشمند pouyamed',
            'is_active': True,
        },
    )


class Migration(migrations.Migration):
    dependencies = [
        ('account', '0006_organization_admin_and_profile_org_admin'),
    ]

    operations = [migrations.RunPython(create_default_organization, migrations.RunPython.noop)]
