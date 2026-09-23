from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('account', '0009_validate_uploaded_images'),
    ]

    operations = [
        migrations.AddField(
            model_name='organization',
            name='default_language',
            field=models.CharField(
                choices=[('fa', 'Persian'), ('en', 'English'), ('ar', 'Arabic')],
                default='fa',
                max_length=5,
            ),
        ),
        migrations.AddField(
            model_name='profile',
            name='language',
            field=models.CharField(
                choices=[('fa', 'Persian'), ('en', 'English'), ('ar', 'Arabic')],
                default='fa',
                max_length=5,
            ),
        ),
    ]
