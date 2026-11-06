from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.articles.models import Article
from apps.articles.signals import invalidate_global_news_cache


class Command(BaseCommand):
    help = "Publishes scheduled articles that have reached their published_at timestamp."

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Report scheduled articles without altering status.',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        now = timezone.now()

        scheduled_articles = Article.objects.filter(
            status__in=[Article.STATUS_REVIEW, Article.STATUS_DRAFT],
            published_at__isnull=False,
            published_at__lte=now,
        )

        count = scheduled_articles.count()
        if count == 0:
            self.stdout.write(self.style.SUCCESS("No pending scheduled articles to publish."))
            return

        self.stdout.write(self.style.NOTICE(f"Found {count} scheduled article(s) ready for publication."))

        for article in scheduled_articles:
            if dry_run:
                self.stdout.write(f"[DRY-RUN] Would publish: '{article.title}' (scheduled: {article.published_at})")
            else:
                article.status = Article.STATUS_PUBLISHED
                article.save(update_fields=['status'])
                self.stdout.write(self.style.SUCCESS(f"Published: '{article.title}'"))

        if not dry_run:
            invalidate_global_news_cache()
            self.stdout.write(self.style.SUCCESS(f"Successfully published {count} scheduled article(s)."))
