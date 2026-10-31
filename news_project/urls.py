from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import include, path

from apps.articles.sitemaps import ArticleSitemap, CategorySitemap, StaticViewSitemap
from apps.core.views import UserLoginView, UserLogoutView, UserRegisterView, robots_txt

sitemaps = {
    'articles': ArticleSitemap,
    'categories': CategorySitemap,
    'static': StaticViewSitemap,
}

urlpatterns = [
    # Modern Admin Panel
    path('admin/', admin.site.urls),

    # Rich Text Editor (CKEditor 5)
    path('ckeditor5/', include('django_ckeditor_5.urls')),

    # Reader Authentication
    path('login/', UserLoginView.as_view(), name='login'),
    path('register/', UserRegisterView.as_view(), name='register'),
    path('logout/', UserLogoutView.as_view(), name='logout'),

    # Audience & Newsletter
    path('newsletter/', include('apps.newsletter.urls', namespace='newsletter')),

    # Editorial Policy & Informational Pages
    path('pages/', include('apps.core.urls', namespace='core')),

    # SEO & Syndication
    path('robots.txt', robots_txt, name='robots_txt'),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),

    # Articles & Editorial (Root)
    path('', include('apps.articles.urls', namespace='articles')),
]

# Custom HTTP Error Handlers
handler404 = 'apps.core.views.custom_404_view'
handler500 = 'apps.core.views.custom_500_view'
handler403 = 'apps.core.views.custom_403_view'

# Serve media and static files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
