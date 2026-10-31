import uuid
from django.db import models
from django.urls import reverse
from django.utils import timezone


class NewsletterSubscriber(models.Model):
    """
    Tracks newsletter subscribers with opt-in status,
    secure tokens for one-click unsubscribe, and subscription metrics.
    """
    email = models.EmailField('Email Address', unique=True)
    token = models.UUIDField('Security Token', default=uuid.uuid4, unique=True, editable=False)
    is_confirmed = models.BooleanField('Confirmed', default=True)
    is_active = models.BooleanField('Active Subscription', default=True)
    created_at = models.DateTimeField('Subscribed Date', auto_now_add=True)
    confirmed_at = models.DateTimeField('Confirmed At', null=True, blank=True)
    unsubscribed_at = models.DateTimeField('Unsubscribed At', null=True, blank=True)

    class Meta:
        verbose_name = 'Newsletter Subscriber'
        verbose_name_plural = 'Newsletter Subscribers'
        ordering = ['-created_at']

    def __str__(self):
        return self.email

    def get_unsubscribe_url(self):
        return reverse('newsletter:unsubscribe', kwargs={'token': str(self.token)})

    def unsubscribe(self):
        self.is_active = False
        self.unsubscribed_at = timezone.now()
        self.save(update_fields=['is_active', 'unsubscribed_at'])

    def confirm(self):
        self.is_confirmed = True
        self.confirmed_at = timezone.now()
        self.save(update_fields=['is_confirmed', 'confirmed_at'])
