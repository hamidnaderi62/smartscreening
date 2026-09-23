from django.db import migrations, models

import account.validators


class Migration(migrations.Migration):
    dependencies = [
        ('account', '0008_organizationmembership'),
    ]

    operations = [
        migrations.AlterField(
            model_name='organization',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='organization/images', validators=[account.validators.validate_image_upload]),
        ),
        migrations.AlterField(
            model_name='organization',
            name='logo',
            field=models.ImageField(blank=True, null=True, upload_to='organization/logo', validators=[account.validators.validate_image_upload]),
        ),
        migrations.AlterField(
            model_name='profile',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='profiles/images', validators=[account.validators.validate_image_upload]),
        ),
    ]
