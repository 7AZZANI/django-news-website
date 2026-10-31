import math
import re
from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify
from django_ckeditor_5.fields import CKEditor5Field
from taggit.managers import TaggableManager


class Category(models.Model):
    """
    Hierarchical news category (e.g., Technology -> Artificial Intelligence).
    Supports subcategories, custom editorial badge colors, and display ordering.
    """
    name = models.CharField('Category Name', max_length=100, unique=True)
    slug = models.SlugField('Slug', max_length=120, unique=True)
    description = models.TextField('Description', blank=True)
    parent = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='subcategories',
        verbose_name='Parent Category'
    )
    color = models.CharField(
        'Accent Color',
        max_length=50,
        default='blue',
        help_text='Tailwind color identifier (e.g. red, blue, emerald, amber, purple, indigo)'
    )
    order = models.PositiveIntegerField('Display Order', default=0)
    is_featured = models.BooleanField('Feature in Top Nav', default=True)

    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
        ordering = ['order', 'name']

    def __str__(self):
        if self.parent:
            return f"{self.parent.name} → {self.name}"
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('articles:category_detail', kwargs={'slug': self.slug})

    @property
    def is_subcategory(self):
        return self.parent is not None


class ArticleQuerySet(models.QuerySet):
    def published(self):
        return self.filter(
            status=Article.STATUS_PUBLISHED,
            published_at__lte=timezone.now()
        )

    def breaking(self):
        return self.published().filter(is_breaking=True).order_by('-published_at')

    def featured(self):
        return self.published().filter(is_featured=True).order_by('-published_at')

    def editors_picks(self):
        return self.published().filter(is_editors_pick=True).order_by('-published_at')

    def trending(self, days=7):
        since = timezone.now() - timezone.timedelta(days=days)
        return self.published().filter(published_at__gte=since).order_by('-views_count', '-published_at')


class ArticleManager(models.Manager):
    def get_queryset(self):
        return ArticleQuerySet(self.model, using=self._db)

    def published(self):
        return self.get_queryset().published()

    def breaking(self):
        return self.get_queryset().breaking()

    def featured(self):
        return self.get_queryset().featured()

    def editors_picks(self):
        return self.get_queryset().editors_picks()

    def trending(self, days=7):
        return self.get_queryset().trending(days=days)


class Article(models.Model):
    """
    Core Article model representing editorial news stories with rich content,
    categorization, tags, view counts, reading time, and publishing workflow.
    """
    STATUS_DRAFT = 'draft'
    STATUS_REVIEW = 'review'
    STATUS_PUBLISHED = 'published'
    STATUS_ARCHIVED = 'archived'

    STATUS_CHOICES = (
        (STATUS_DRAFT, 'Draft'),
        (STATUS_REVIEW, 'Under Review'),
        (STATUS_PUBLISHED, 'Published'),
        (STATUS_ARCHIVED, 'Archived'),
    )

    title = models.CharField('Headline', max_length=255)
    slug = models.SlugField('Slug', max_length=280, unique=True)
    excerpt = models.TextField('Excerpt / Lead Deck', help_text='Summary deck for article cards, search results, and SEO metadata.')
    body = CKEditor5Field('Article Body', config_name='extends')
    featured_image = models.ImageField('Featured Image', upload_to='articles/%Y/%m/')
    image_caption = models.CharField('Image Caption / Credit', max_length=255, blank=True)

    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name='articles',
        verbose_name='Primary Category'
    )
    tags = TaggableManager(blank=True, verbose_name='Tags')
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='articles',
        verbose_name='Author'
    )

    status = models.CharField('Publishing Status', max_length=20, choices=STATUS_CHOICES, default=STATUS_DRAFT)
    is_breaking = models.BooleanField('Breaking News', default=False, help_text='Highlights in the top breaking news ticker.')
    is_featured = models.BooleanField('Hero / Lead Story', default=False, help_text='Prioritizes this article in the homepage hero grid.')
    is_editors_pick = models.BooleanField("Editor's Pick", default=False, help_text='Shows in curated recommendation modules.')

    views_count = models.PositiveIntegerField('Total Views', default=0)
    reading_time = models.PositiveIntegerField('Reading Time (mins)', default=1)

    # SEO & Social Metadata
    meta_title = models.CharField('Meta Title', max_length=255, blank=True, help_text='SEO title tag (falls back to headline).')
    meta_description = models.CharField('Meta Description', max_length=320, blank=True, help_text='SEO description (falls back to excerpt).')

    published_at = models.DateTimeField('Published Date', null=True, blank=True)
    created_at = models.DateTimeField('Created Date', auto_now_add=True)
    updated_at = models.DateTimeField('Last Updated', auto_now=True)

    objects = ArticleManager()

    class Meta:
        verbose_name = 'Article'
        verbose_name_plural = 'Articles'
        ordering = ['-published_at', '-created_at']
        indexes = [
            models.Index(fields=['status', '-published_at']),
            models.Index(fields=['is_breaking', '-published_at']),
            models.Index(fields=['is_featured', '-published_at']),
            models.Index(fields=['slug']),
        ]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('articles:article_detail', kwargs={'slug': self.slug})

    def get_meta_title(self):
        return self.meta_title or self.title

    def get_meta_description(self):
        return self.meta_description or self.excerpt

    def calculate_reading_time(self):
        """Calculates estimated reading time at standard 200 wpm."""
        clean_text = re.sub(r'<[^>]+>', ' ', self.body or '')
        words = len(clean_text.split())
        return max(1, math.ceil(words / 200))

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            while Article.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug

        # Update reading time automatically
        self.reading_time = self.calculate_reading_time()

        # Automatically assign published_at when transitioning to published status
        if self.status == self.STATUS_PUBLISHED and not self.published_at:
            self.published_at = timezone.now()

        super().save(*args, **kwargs)


class ArticleView(models.Model):
    """
    Log of individual page impressions used for daily metrics,
    trending calculations, and dashboard graphs.
    """
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='view_logs')
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    session_key = models.CharField(max_length=40, blank=True, null=True)
    viewed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Article Impression'
        verbose_name_plural = 'Article Impressions'
        indexes = [
            models.Index(fields=['article', 'viewed_at']),
            models.Index(fields=['viewed_at']),
        ]


class CommentQuerySet(models.QuerySet):
    def approved(self):
        return self.filter(status=Comment.STATUS_APPROVED)

    def pending(self):
        return self.filter(status=Comment.STATUS_PENDING)


class CommentManager(models.Manager):
    def get_queryset(self):
        return CommentQuerySet(self.model, using=self._db)

    def approved(self):
        return self.get_queryset().approved()

    def pending(self):
        return self.get_queryset().pending()


class Comment(models.Model):
    """
    Reader comments on articles, featuring a moderation queue (pending, approved, rejected),
    anti-spam honeypot support, and user/guest duality.
    """
    STATUS_PENDING = 'pending'
    STATUS_APPROVED = 'approved'
    STATUS_REJECTED = 'rejected'

    STATUS_CHOICES = (
        (STATUS_PENDING, 'Pending Approval'),
        (STATUS_APPROVED, 'Approved'),
        (STATUS_REJECTED, 'Rejected'),
    )

    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='comments'
    )
    name = models.CharField('Name', max_length=100, blank=True)
    email = models.EmailField('Email Address', blank=True)
    content = models.TextField('Comment')
    status = models.CharField('Moderation Status', max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField('Submitted On', auto_now_add=True)

    objects = CommentManager()

    class Meta:
        verbose_name = 'Comment'
        verbose_name_plural = 'Comments'
        ordering = ['-created_at']

    def __str__(self):
        return f"Comment by {self.author_name} on {self.article.title}"

    @property
    def author_name(self):
        if self.user:
            return self.user.get_full_name_or_username()
        return self.name or 'Anonymous Reader'

    @property
    def author_avatar(self):
        if self.user:
            return self.user.avatar_url
        initial = (self.name[:2] if self.name else 'AR').upper()
        return f"https://ui-avatars.com/api/?name={initial}&background=64748b&color=ffffff&bold=true&size=96"
