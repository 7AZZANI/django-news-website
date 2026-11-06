from django.core.cache import cache
from django.db.models import Count
from django.utils import timezone
from taggit.models import Tag

from .models import Article, Category

GLOBAL_CONTEXT_CACHE_KEY = 'global_news_context_v2'


def get_cached_news_context():
    """
    Retrieves global news context from cache, or queries the database
    and stores the evaluated dataset for 10 minutes (600s).
    """
    data = cache.get(GLOBAL_CONTEXT_CACHE_KEY)
    if data is None:
        header_categories = list(
            Category.objects.filter(
                parent__isnull=True,
                is_featured=True
            ).prefetch_related('subcategories').order_by('order', 'name')[:8]
        )
        breaking_news = list(Article.objects.breaking()[:6])
        trending_articles = list(Article.objects.trending(days=7)[:5])
        popular_tags = list(
            Tag.objects.annotate(
                article_count=Count('taggit_taggeditem_items')
            ).filter(article_count__gt=0).order_by('-article_count')[:15]
        )
        data = {
            'HEADER_CATEGORIES': header_categories,
            'BREAKING_NEWS': breaking_news,
            'TRENDING_ARTICLES': trending_articles,
            'POPULAR_TAGS': popular_tags,
        }
        cache.set(GLOBAL_CONTEXT_CACHE_KEY, data, timeout=600)
    return data


def global_news_context(request):
    """
    Context processor making core navigation categories, breaking news,
    trending stories, and site metadata available across all templates.
    Combines cached query datasets with live dynamic clock timestamp.
    """
    context = get_cached_news_context().copy()
    context.update({
        'SITE_NAME': 'The Chronicle',
        'SITE_TAGLINE': 'Veritas & Lumen · Independent Global Journalism',
        'CURRENT_DATE': timezone.now(),
    })
    return context
