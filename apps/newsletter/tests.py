from django.test import TestCase, Client
from django.urls import reverse
from .models import NewsletterSubscriber


class NewsletterTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_newsletter_subscription(self):
        response = self.client.post(reverse('newsletter:subscribe'), {
            'email': 'subscriber1@example.com',
            'honeypot': '',
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(NewsletterSubscriber.objects.filter(email='subscriber1@example.com').exists())

    def test_newsletter_unsubscribe(self):
        sub = NewsletterSubscriber.objects.create(email='unsub@example.com', is_active=True)
        response = self.client.get(reverse('newsletter:unsubscribe', kwargs={'token': sub.token}))
        self.assertEqual(response.status_code, 200)
        sub.refresh_from_db()
        self.assertFalse(sub.is_active)
        self.assertIsNotNone(sub.unsubscribed_at)

    def test_send_newsletter_digest_command(self):
        from django.core.management import call_command
        from django.core import mail
        from django.utils import timezone
        from apps.core.models import CustomUser
        from apps.articles.models import Article, Category

        user = CustomUser.objects.create_user(email='author@example.com', username='digest_author', password='pw')
        cat = Category.objects.create(name='World', slug='world')
        Article.objects.create(
            title='Global Summit on Energy Stability',
            slug='global-summit-on-energy-stability',
            excerpt='World leaders agree on grid resilience.',
            body='<p>Full story.</p>',
            author=user,
            category=cat,
            status=Article.STATUS_PUBLISHED,
            published_at=timezone.now(),
        )

        NewsletterSubscriber.objects.create(email='reader100@example.com', is_active=True, is_confirmed=True)

        call_command('send_newsletter_digest', email='reader100@example.com')
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('The Chronicle Weekly Brief', mail.outbox[0].subject)
        self.assertIn('reader100@example.com', mail.outbox[0].to)


