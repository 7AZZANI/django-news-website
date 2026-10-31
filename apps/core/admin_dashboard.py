from django.utils import timezone
from datetime import timedelta


def dashboard_callback(request, context):
    """
    Supplies real-time editorial metrics and KPI counters
    for the Django Unfold modern admin dashboard.
    """
    from apps.articles.models import Article, Comment, ArticleView
    from apps.newsletter.models import NewsletterSubscriber

    now = timezone.now()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)

    # Article statistics
    total_articles = Article.objects.count()
    published_articles = Article.objects.filter(status='published').count()
    review_articles = Article.objects.filter(status='review').count()
    draft_articles = Article.objects.filter(status='draft').count()

    # Views statistics
    views_today = ArticleView.objects.filter(viewed_at__gte=today_start).count()
    total_views = sum(Article.objects.values_list('views_count', flat=True)) or 0

    # Comments needing moderation
    comments_pending = Comment.objects.filter(status='pending').count()

    # Newsletter audience
    total_subscribers = NewsletterSubscriber.objects.filter(is_active=True).count()

    # Recent articles requiring attention or newly published
    recent_articles = Article.objects.select_related('author', 'category').order_by('-created_at')[:5]
    recent_pending_comments = Comment.objects.select_related('article').filter(status='pending').order_by('-created_at')[:5]

    context.update({
        'kpi_total_articles': total_articles,
        'kpi_published_articles': published_articles,
        'kpi_review_articles': review_articles,
        'kpi_draft_articles': draft_articles,
        'kpi_views_today': views_today,
        'kpi_total_views': total_views,
        'kpi_comments_pending': comments_pending,
        'kpi_total_subscribers': total_subscribers,
        'recent_articles': recent_articles,
        'recent_pending_comments': recent_pending_comments,
    })

    return context
