from django.db import migrations, models


def copy_existing_birth_years(apps, schema_editor):
    Profile = apps.get_model('account', 'Profile')
    profiles = Profile.objects.exclude(birth_date__isnull=True).only('pk', 'birth_date')
    for profile in profiles.iterator():
        profile.birth_year = profile.birth_date.year
        profile.birth_year_calendar = 'gregorian'
        profile.save(update_fields=('birth_year', 'birth_year_calendar'))


class Migration(migrations.Migration):
    dependencies = [
        ('account', '0016_alter_profile_code'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='birth_year',
            field=models.PositiveSmallIntegerField(
                blank=True,
                help_text='Year of birth in the calendar selected during registration.',
                null=True,
            ),
        ),
        migrations.AddField(
            model_name='profile',
            name='birth_year_calendar',
            field=models.CharField(
                choices=[('gregorian', 'Gregorian'), ('jalali', 'Jalali')],
                default='gregorian',
                help_text='Calendar used for the stored birth year.',
                max_length=10,
            ),
        ),
        migrations.RunPython(copy_existing_birth_years, migrations.RunPython.noop),
        migrations.RemoveField(
            model_name='profile',
            name='birth_date',
        ),
    ]
