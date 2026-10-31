from django.db.models import Count
from django.utils import timezone
from taggit.models import Tag

from .models import Article, Category


def global_news_context(request):
    """
    Context processor making core navigation categories, breaking news,
    trending stories, and site metadata available across all templates.
    """
    now = timezone.now()

    # Primary navigation categories with their subcategories
    header_categories = Category.objects.filter(
        parent__isnull=True,
        is_featured=True
    ).prefetch_related('subcategories').order_by('order', 'name')[:8]

    # Breaking news ticker items (published only)
    breaking_news = Article.objects.breaking()[:6]

    # Top read / trending articles
    trending_articles = Article.objects.trending(days=7)[:5]

    # Popular tags cloud
    popular_tags = Tag.objects.annotate(
        article_count=Count('taggit_taggeditem_items')
    ).filter(article_count__gt=0).order_by('-article_count')[:15]

    return {
        'SITE_NAME': 'The Chronicle',
        'SITE_TAGLINE': 'Veritas & Lumen · Independent Global Journalism',
        'CURRENT_DATE': now,
        'HEADER_CATEGORIES': header_categories,
        'BREAKING_NEWS': breaking_news,
        'TRENDING_ARTICLES': trending_articles,
        'POPULAR_TAGS': popular_tags,
    }
