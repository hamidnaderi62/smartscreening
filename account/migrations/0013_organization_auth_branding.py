from django.db import migrations, models
import django.core.validators


class Migration(migrations.Migration):
    dependencies = [
        ('account', '0012_profile_phone_number'),
    ]

    operations = [
        migrations.AddField(
            model_name='organization',
            name='brand_primary_color',
            field=models.CharField(
                default='#066ac9',
                help_text='Primary color used on organization login and registration pages.',
                max_length=7,
                validators=[django.core.validators.RegexValidator(
                    message='Use a six-digit hexadecimal color such as #066AC9.',
                    regex='^#[0-9A-Fa-f]{6}$',
                )],
            ),
        ),
        migrations.AddField(
            model_name='organization',
            name='brand_accent_color',
            field=models.CharField(
                default='#0cbc87',
                help_text='Accent color used for highlights and secondary actions.',
                max_length=7,
                validators=[django.core.validators.RegexValidator(
                    message='Use a six-digit hexadecimal color such as #066AC9.',
                    regex='^#[0-9A-Fa-f]{6}$',
                )],
            ),
        ),
        migrations.AddField(
            model_name='organization',
            name='brand_surface_color',
            field=models.CharField(
                default='#f5f8fb',
                help_text='Soft background color used by organization authentication pages.',
                max_length=7,
                validators=[django.core.validators.RegexValidator(
                    message='Use a six-digit hexadecimal color such as #066AC9.',
                    regex='^#[0-9A-Fa-f]{6}$',
                )],
            ),
        ),
    ]
