from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('account', '0016_alter_profile_code'),
        ('doctor', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='doctorprofile',
            name='signature_image',
            field=models.ImageField(
                blank=True,
                help_text='Doctor signature shown below verified notes in screening PDFs.',
                null=True,
                upload_to='doctors/signatures/',
            ),
        ),
        migrations.AddField(
            model_name='doctorprofile',
            name='seal_image',
            field=models.ImageField(
                blank=True,
                help_text='Doctor seal shown below verified notes in screening PDFs.',
                null=True,
                upload_to='doctors/seals/',
            ),
        ),
        migrations.AddField(
            model_name='doctorprofile',
            name='is_gp',
            field=models.BooleanField(
                default=True,
                help_text='Only active, verified GP profiles are shown to patients.',
                verbose_name='General practitioner',
            ),
        ),
        migrations.AddField(
            model_name='doctorprofile',
            name='organizations',
            field=models.ManyToManyField(
                blank=True,
                help_text='Leave empty to make this doctor available in every organization.',
                related_name='doctor_profiles',
                to='account.organization',
            ),
        ),
    ]
