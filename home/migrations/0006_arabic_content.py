from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('home', '0005_validate_uploaded_images'),
    ]

    operations = [
        migrations.AddField(
            model_name='team',
            name='name_ar',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='team',
            name='position_ar',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='team',
            name='specialty_ar',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='blog',
            name='title_ar',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='blog',
            name='desc_ar',
            field=models.TextField(blank=True, null=True),
        ),
    ]
