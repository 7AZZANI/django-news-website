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
