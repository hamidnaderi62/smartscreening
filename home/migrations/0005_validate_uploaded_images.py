from django.db import migrations, models

import account.validators


class Migration(migrations.Migration):
    dependencies = [
        ('account', '0009_validate_uploaded_images'),
        ('home', '0004_team_image_center1_team_image_center2_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='blog',
            name='image_file',
            field=models.ImageField(blank=True, null=True, upload_to='images/blog', validators=[account.validators.validate_image_upload]),
        ),
        migrations.AlterField(
            model_name='team',
            name='image_center1',
            field=models.ImageField(blank=True, null=True, upload_to='images/center', validators=[account.validators.validate_image_upload]),
        ),
        migrations.AlterField(
            model_name='team',
            name='image_center2',
            field=models.ImageField(blank=True, null=True, upload_to='images/center', validators=[account.validators.validate_image_upload]),
        ),
        migrations.AlterField(
            model_name='team',
            name='image_center3',
            field=models.ImageField(blank=True, null=True, upload_to='images/center', validators=[account.validators.validate_image_upload]),
        ),
        migrations.AlterField(
            model_name='team',
            name='image_file',
            field=models.ImageField(blank=True, null=True, upload_to='images/team', validators=[account.validators.validate_image_upload]),
        ),
    ]
