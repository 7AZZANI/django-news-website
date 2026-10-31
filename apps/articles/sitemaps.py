from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from .models import Article, Category


class ArticleSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.9

    def items(self):
        return Article.objects.published()

    def lastmod(self, obj):
        return obj.updated_at


class CategorySitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.7

    def items(self):
        return Category.objects.all()


class StaticViewSitemap(Sitemap):
    priority = 1.0
    changefreq = "daily"

    def items(self):
        return [
            'articles:home',
            'articles:search',
            'core:about',
            'core:ethics',
            'core:privacy',
            'core:terms',
            'core:contact',
        ]

    def location(self, item):
        return reverse(item)
