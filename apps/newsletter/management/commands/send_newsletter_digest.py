from django.core.management.base import BaseCommand
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.utils import timezone
from decouple import config

from apps.newsletter.models import NewsletterSubscriber
from apps.articles.models import Article


class Command(BaseCommand):
    help = "Dispatches weekly editorial email digest to active confirmed newsletter subscribers."

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Simulate dispatch without sending actual emails.',
        )
        parser.add_argument(
            '--email',
            type=str,
            help='Send a test digest to a single target email address.',
        )
        parser.add_argument(
            '--limit',
            type=int,
            default=0,
            help='Maximum number of emails to dispatch (0 for all).',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        target_email = options['email']
        limit = options['limit']

        self.stdout.write(self.style.NOTICE("Initiating The Chronicle Weekly Editorial Digest dispatch..."))

        # Fetch top stories of the week
        since = timezone.now() - timezone.timedelta(days=7)
        top_articles = Article.objects.published().filter(
            published_at__gte=since
        ).order_by('-views_count', '-published_at')[:4]

        if not top_articles.exists():
            top_articles = Article.objects.published().order_by('-published_at')[:4]

        if not top_articles.exists():
            self.stdout.write(self.style.WARNING("No published articles found to compile into digest. Aborting."))
            return

        site_url = config('SITE_URL', default='http://localhost:8000').rstrip('/')

        # Determine target subscribers
        if target_email:
            subscribers = NewsletterSubscriber.objects.filter(email=target_email)
            if not subscribers.exists():
                # Create temporary mock subscriber for testing
                subscribers = [NewsletterSubscriber(email=target_email)]
        else:
            subscribers = NewsletterSubscriber.objects.filter(is_active=True, is_confirmed=True)
            if limit > 0:
                subscribers = subscribers[:limit]

        total_targets = len(subscribers)
        self.stdout.write(f"Targeting {total_targets} subscriber(s). Found {len(top_articles)} featured stories.")

        sent_count = 0
        from_email = config('DEFAULT_FROM_EMAIL', default='The Chronicle <editorial@thechronicle.internal>')
        subject = f"The Chronicle Weekly Brief: {top_articles[0].title[:55]}..."

        for sub in subscribers:
            context = {
                'subject': subject,
                'articles': top_articles,
                'subscriber': sub,
                'current_date': timezone.now(),
                'site_url': site_url,
            }

            html_content = render_to_string('newsletter/email_digest.html', context)
            text_content = strip_tags(html_content)

            if dry_run:
                self.stdout.write(f"[DRY-RUN] Would dispatch to: {sub.email}")
                sent_count += 1
            else:
                try:
                    msg = EmailMultiAlternatives(
                        subject=subject,
                        body=text_content,
                        from_email=from_email,
                        to=[sub.email],
                    )
                    msg.attach_alternative(html_content, "text/html")
                    msg.send(fail_silently=False)
                    sent_count += 1
                    self.stdout.write(f"Dispatched digest to: {sub.email}")
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"Failed sending to {sub.email}: {e}"))

        mode_label = "[DRY-RUN] Simulated" if dry_run else "Successfully dispatched"
        self.stdout.write(self.style.SUCCESS(f"{mode_label} {sent_count} newsletter digest(s)."))
