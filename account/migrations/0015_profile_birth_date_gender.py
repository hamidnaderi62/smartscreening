from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('account', '0014_organization_followup_sms_enabled_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='birth_date',
            field=models.DateField(
                blank=True,
                help_text='Used to calculate the screening age automatically.',
                null=True,
            ),
        ),
        migrations.AddField(
            model_name='profile',
            name='gender',
            field=models.CharField(
                choices=[('Male', 'Male'), ('Female', 'Female')],
                default='Male',
                help_text='Used to show the relevant screening assessments.',
                max_length=10,
            ),
        ),
    ]
