import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('my_model', '0010_validate_uploaded_images'),
    ]

    operations = [
        migrations.CreateModel(
            name='ScreeningReportShortLink',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('token_hash', models.CharField(max_length=64, unique=True)),
                ('language', models.CharField(default='fa', max_length=5)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('screening', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='report_short_links', to='my_model.mymodel')),
            ],
        ),
    ]
