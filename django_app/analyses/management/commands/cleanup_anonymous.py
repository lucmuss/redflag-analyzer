from django.core.management.base import BaseCommand
from analyses.anonymous_models import AnonymousAnalysis


class Command(BaseCommand):
    help = 'Cleanup expired anonymous analyses (Privacy)'

    def handle(self, *args, **options):
        count = AnonymousAnalysis.cleanup_expired()
        self.stdout.write(
            self.style.SUCCESS(f'Successfully deleted {count} expired anonymous analyses')
        )
