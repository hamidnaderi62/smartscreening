from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('account', '0011_organization_translations'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='phone_number',
            field=models.CharField(
                blank=True,
                help_text='Mobile number used for follow-up SMS notifications.',
                max_length=20,
            ),
        ),
    ]
