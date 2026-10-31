from django.urls import path
from .views import (
    HomeView,
    ArticleDetailView,
    CategoryDetailView,
    TagDetailView,
    AuthorDetailView,
    SearchView,
)
from .feeds import LatestArticlesFeed

app_name = 'articles'

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('article/<slug:slug>/', ArticleDetailView.as_view(), name='article_detail'),
    path('category/<slug:slug>/', CategoryDetailView.as_view(), name='category_detail'),
    path('tag/<slug:slug>/', TagDetailView.as_view(), name='tag_detail'),
    path('author/<str:username>/', AuthorDetailView.as_view(), name='author_detail'),
    path('search/', SearchView.as_view(), name='search'),
    path('feed/rss/', LatestArticlesFeed(), name='rss_feed'),
]
