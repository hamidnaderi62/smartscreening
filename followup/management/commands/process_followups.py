from django.core.management.base import BaseCommand

from followup.services import process_due_reminders


class Command(BaseCommand):
    help = 'Send due follow-up and PDF-report SMS reminders through Kavenegar.'

    def add_arguments(self, parser):
        parser.add_argument('--limit', type=int, default=100)
        parser.add_argument(
            '--retry-failed',
            action='store_true',
            help='Retry reminders previously marked as failed.',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='List due reminders without sending SMS.',
        )

    def handle(self, *args, **options):
        if options['dry_run']:
            from django.utils import timezone
            from followup.models import FollowUpReminder

            count = FollowUpReminder.objects.filter(
                status='failed' if options['retry_failed'] else 'pending',
                scheduled_for__lte=timezone.now(),
            ).count()
            self.stdout.write(self.style.WARNING(f'{count} reminder(s) are due.'))
            return

        reminders = process_due_reminders(
            limit=max(1, options['limit']),
            retry_failed=options['retry_failed'],
        )
        sent = sum(reminder.status == 'sent' for reminder in reminders)
        failed = len(reminders) - sent
        self.stdout.write(self.style.SUCCESS(f'Processed {len(reminders)} reminder(s): {sent} sent, {failed} failed.'))
