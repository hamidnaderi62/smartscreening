from django.db import migrations, models

import account.validators


class Migration(migrations.Migration):
    dependencies = [
        ('account', '0009_validate_uploaded_images'),
        ('my_model', '0009_alter_mymodel_screening_data_alter_mymodel_userid_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='assessment',
            name='image_file',
            field=models.ImageField(blank=True, null=True, upload_to='images/assessmets', validators=[account.validators.validate_image_upload]),
        ),
    ]
