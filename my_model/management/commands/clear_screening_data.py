from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from my_model.models import MyModel


class Command(BaseCommand):
    help = 'Delete disposable screening test data while preserving accounts and organizations.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--confirm',
            action='store_true',
            help='Confirm deletion of all MyModel screening rows.',
        )

    def handle(self, *args, **options):
        if not settings.DEBUG:
            raise CommandError('This cleanup command is available only when DEBUG=True.')
        if not options['confirm']:
            raise CommandError(
                'Nothing was deleted. Re-run with --confirm after backing up the database.'
            )

        count = MyModel.objects.count()
        deleted, _ = MyModel.objects.all().delete()
        self.stdout.write(
            self.style.SUCCESS(
                f'Deleted {deleted} database objects ({count} screening records).'
            )
        )
