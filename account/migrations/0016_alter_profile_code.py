from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('account', '0015_profile_birth_date_gender'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='code',
            field=models.CharField(max_length=20),
        ),
    ]
