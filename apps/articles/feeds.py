from django.contrib.syndication.views import Feed
from django.urls import reverse
from django.utils.feedgenerator import Rss201rev2Feed
from .models import Article


class LatestArticlesFeed(Feed):
    feed_type = Rss201rev2Feed
    title = "The Chronicle — Latest News & Analysis"
    link = "/"
    description = "Authoritative, independent coverage of politics, technology, business, culture, and science."
    feed_copyright = "Copyright © The Chronicle. All rights reserved."

    def items(self):
        return Article.objects.published().select_related('author', 'category')[:25]

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return item.excerpt

    def item_pubdate(self, item):
        return item.published_at

    def item_author_name(self, item):
        return item.author.get_full_name_or_username()

    def item_categories(self, item):
        return [item.category.name]

    def item_link(self, item):
        return item.get_absolute_url()
