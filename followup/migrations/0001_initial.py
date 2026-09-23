import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


ASSESSMENT_CHOICES = [
    (1, 'Breast Cancer Risk Assessment'),
    (2, 'Colorectal Cancer Risk Assessment'),
    (3, 'Prostate Cancer Risk Assessment'),
    (4, 'Cervical Cancer Risk Assessment'),
    (5, 'Diabetes Risk Assessment'),
    (6, 'Cardiovascular Disease Risk Assessment'),
    (7, 'Melanoma Cancer Risk Assessment'),
    (8, 'Osteoporosis Risk Assessment'),
    (9, 'Ovarian Cancer Risk Assessment'),
    (10, 'Stomach Cancer Risk Assessment'),
    (11, 'Stroke Risk Assessment'),
    (12, 'Pancreatic Cancer Risk Assessment'),
]


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ('my_model', '0010_validate_uploaded_images'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='FollowUpProgram',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('assessment_id', models.PositiveSmallIntegerField(choices=ASSESSMENT_CHOICES, unique=True)),
                ('title', models.CharField(help_text='Default/Farsi title.', max_length=200)),
                ('title_en', models.CharField(blank=True, max_length=200)),
                ('title_ar', models.CharField(blank=True, max_length=200)),
                ('description', models.TextField(blank=True, help_text='Default/Farsi description.')),
                ('description_en', models.TextField(blank=True)),
                ('description_ar', models.TextField(blank=True)),
                ('trigger_statuses', models.CharField(blank=True, help_text='Comma-separated English result statuses. Leave blank to apply to every result.', max_length=500)),
                ('send_pdf_sms', models.BooleanField(default=False, verbose_name='Send PDF report by SMS')),
                ('pdf_sms_delay_days', models.PositiveIntegerField(default=0, verbose_name='PDF SMS delay (days)')),
                ('is_active', models.BooleanField(default=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
            ],
            options={'ordering': ('assessment_id',)},
        ),
        migrations.CreateModel(
            name='FollowUpPlan',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('result_status', models.CharField(blank=True, max_length=120)),
                ('language', models.CharField(default='fa', max_length=5)),
                ('status', models.CharField(choices=[('active', 'Active'), ('completed', 'Completed'), ('cancelled', 'Cancelled')], default='active', max_length=20)),
                ('started_at', models.DateTimeField(auto_now_add=True)),
                ('next_reminder_at', models.DateTimeField(blank=True, null=True)),
                ('completed_at', models.DateTimeField(blank=True, null=True)),
                ('program', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='plans', to='followup.followupprogram')),
                ('screening', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='follow_up_plans', to='my_model.mymodel')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='follow_up_plans', to=settings.AUTH_USER_MODEL)),
            ],
            options={'ordering': ('status', 'next_reminder_at', '-started_at')},
        ),
        migrations.CreateModel(
            name='FollowUpStep',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order', models.PositiveIntegerField(default=1)),
                ('delay_days', models.PositiveIntegerField(default=30, help_text='Days after the screening date when this reminder becomes due.')),
                ('title', models.CharField(help_text='Default/Farsi title.', max_length=200)),
                ('title_en', models.CharField(blank=True, max_length=200)),
                ('title_ar', models.CharField(blank=True, max_length=200)),
                ('message', models.TextField(help_text='Default/Farsi SMS message.')),
                ('message_en', models.TextField(blank=True)),
                ('message_ar', models.TextField(blank=True)),
                ('send_sms', models.BooleanField(default=True)),
                ('is_active', models.BooleanField(default=True)),
                ('program', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='steps', to='followup.followupprogram')),
            ],
            options={'ordering': ('program', 'order'), 'constraints': [models.UniqueConstraint(fields=('program', 'order'), name='unique_follow_up_step_order')]},
        ),
        migrations.CreateModel(
            name='FollowUpReminder',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('kind', models.CharField(choices=[('pdf', 'PDF report'), ('step', 'Follow-up step'), ('manual', 'Manual SMS')], max_length=20)),
                ('scheduled_for', models.DateTimeField()),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('sent', 'Sent'), ('failed', 'Failed'), ('cancelled', 'Cancelled')], default='pending', max_length=20)),
                ('attempts', models.PositiveIntegerField(default=0)),
                ('sent_at', models.DateTimeField(blank=True, null=True)),
                ('provider_message_id', models.CharField(blank=True, max_length=100)),
                ('provider_status', models.PositiveIntegerField(blank=True, null=True)),
                ('last_error', models.TextField(blank=True)),
                ('message', models.TextField(blank=True, help_text='Rendered SMS body kept for delivery auditing.')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('plan', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='reminders', to='followup.followupplan')),
                ('step', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='reminders', to='followup.followupstep')),
            ],
            options={'ordering': ('status', 'scheduled_for'), 'constraints': [models.UniqueConstraint(fields=('plan', 'step', 'kind'), name='unique_follow_up_reminder_kind')]},
        ),
    ]
