from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache

from .models import Article, Category, Comment
from .context_processors import GLOBAL_CONTEXT_CACHE_KEY


def invalidate_global_news_cache():
    """Invalidates the cached navigation and trending context processor data."""
    cache.delete(GLOBAL_CONTEXT_CACHE_KEY)


@receiver([post_save, post_delete], sender=Article)
def article_changed_handler(sender, instance, **kwargs):
    invalidate_global_news_cache()


@receiver([post_save, post_delete], sender=Category)
def category_changed_handler(sender, instance, **kwargs):
    invalidate_global_news_cache()


@receiver([post_save, post_delete], sender=Comment)
def comment_changed_handler(sender, instance, **kwargs):
    # Invalidate if comment status changes to approved or deleted
    invalidate_global_news_cache()
