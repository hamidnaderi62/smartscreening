from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('account', '0010_language_preferences'),
    ]

    operations = [
        migrations.AddField(
            model_name='organization',
            name='title_ar',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='organization',
            name='title_en',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='organization',
            name='sentence_ar',
            field=models.CharField(blank=True, max_length=2000, null=True),
        ),
        migrations.AddField(
            model_name='organization',
            name='sentence_en',
            field=models.CharField(blank=True, max_length=2000, null=True),
        ),
    ]
