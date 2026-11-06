"""
Base settings for news_project.
Shared across all environments (dev, prod, test).
"""

from pathlib import Path
from decouple import config
from django.templatetags.static import static
from django.urls import reverse_lazy

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY', default='django-insecure-dev-key-change-this-in-production-chronicle-news-2026!')

# Application definition
INSTALLED_APPS = [
    # Modern Admin Panel (must be before django.contrib.admin)
    'unfold',
    'unfold.contrib.filters',
    'unfold.contrib.forms',

    # Django Core Apps
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sitemaps',
    'django.contrib.humanize',

    # Third Party Apps
    'taggit',
    'django_ckeditor_5',

    # Project Apps
    'apps.core.apps.CoreConfig',
    'apps.articles.apps.ArticlesConfig',
    'apps.newsletter.apps.NewsletterConfig',
]

# Custom User Model
AUTH_USER_MODEL = 'core.CustomUser'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'news_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'apps.articles.context_processors.global_news_context',
            ],
        },
    },
]

WSGI_APPLICATION = 'news_project.wsgi.application'
ASGI_APPLICATION = 'news_project.asgi.application'

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 8,
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Media Files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Authentication URLs
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'articles:home'
LOGOUT_REDIRECT_URL = 'articles:home'

# Taggit Settings
TAGGIT_CASE_INSENSITIVE = True

# Site Pagination Defaults
ARTICLES_PER_PAGE = 9

# Cache Configuration (Redis support with automatic LocMem fallback)
REDIS_URL = config('REDIS_URL', default=None)
REDIS_HOST = config('REDIS_HOST', default=None)
REDIS_PORT = config('REDIS_PORT', default='6379')

if REDIS_URL:
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.redis.RedisCache',
            'LOCATION': REDIS_URL,
            'TIMEOUT': 600,
        }
    }
elif REDIS_HOST:
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.redis.RedisCache',
            'LOCATION': f'redis://{REDIS_HOST}:{REDIS_PORT}/1',
            'TIMEOUT': 600,
        }
    }
else:
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'LOCATION': 'chronicle-cache-unique',
            'TIMEOUT': 600,
        }
    }


# Django Unfold Configuration
UNFOLD = {
    "SITE_TITLE": "The Chronicle Admin",
    "SITE_HEADER": "The Chronicle",
    "SITE_SUBHEADER": "Editorial & Publication CMS",
    "SITE_URL": "/",
    "DASHBOARD_CALLBACK": "apps.core.admin_dashboard.dashboard_callback",
    "COLORS": {
        "primary": {
            "50": "248 250 252",
            "100": "241 245 249",
            "200": "226 232 240",
            "300": "203 213 225",
            "400": "148 163 184",
            "500": "15 23 42",      # Slate 900 editorial accent
            "600": "30 41 59",
            "700": "51 65 85",
            "800": "71 85 105",
            "900": "100 116 139",
            "950": "2 6 23",
        },
    },
    "SIDEBAR": {
        "show_search": True,
        "show_all_applications": True,
        "navigation": [
            {
                "title": "Editorial Management",
                "separator": True,
                "items": [
                    {
                        "title": "Articles",
                        "icon": "newspaper",
                        "link": reverse_lazy("admin:articles_article_changelist"),
                        "badge": "apps.articles.admin.article_badge",
                    },
                    {
                        "title": "Categories",
                        "icon": "category",
                        "link": reverse_lazy("admin:articles_category_changelist"),
                    },
                    {
                        "title": "Comments",
                        "icon": "chat_bubble",
                        "link": reverse_lazy("admin:articles_comment_changelist"),
                        "badge": "apps.articles.admin.comment_badge",
                    },
                    {
                        "title": "Tags",
                        "icon": "label",
                        "link": reverse_lazy("admin:taggit_tag_changelist"),
                    },
                ],
            },
            {
                "title": "Audience & Community",
                "separator": True,
                "items": [
                    {
                        "title": "Newsletter Subscribers",
                        "icon": "mail",
                        "link": reverse_lazy("admin:newsletter_newslettersubscriber_changelist"),
                    },
                ],
            },
            {
                "title": "Team & Access",
                "separator": True,
                "items": [
                    {
                        "title": "Staff & Users",
                        "icon": "group",
                        "link": reverse_lazy("admin:core_customuser_changelist"),
                    },
                ],
            },
        ],
    },
}

# Django CKEditor 5 Configuration
CKEDITOR_5_CONFIGS = {
    'default': {
        'toolbar': ['heading', '|', 'bold', 'italic', 'link', 'bulletedList', 'numberedList', 'blockQuote', 'imageUpload'],
    },
    'extends': {
        'blockToolbar': [
            'paragraph', 'heading1', 'heading2', 'heading3',
            '|',
            'bulletedList', 'numberedList',
            '|',
            'blockQuote', 'imageUpload'
        ],
        'toolbar': [
            'heading', '|', 'outdent', 'indent', '|', 'bold', 'italic', 'link', 'underline', 'strikethrough',
            'code', 'subscript', 'superscript', 'highlight', '|', 'codeBlock', 'imageUpload',
            'bulletedList', 'numberedList', 'todoList', '|',  'blockQuote', 'insertTable', '|',
            'fontSize', 'fontFamily', 'fontColor', 'fontBackgroundColor', 'mediaEmbed', 'removeFormat',
            'insertHorizontalRule'
        ],
        'image': {
            'toolbar': ['imageTextAlternative', '|', 'imageStyle:alignLeft', 'imageStyle:alignRight', 'imageStyle:alignCenter', 'imageStyle:side', '|'],
            'styles': [
                'full',
                'side',
                'alignLeft',
                'alignRight',
                'alignCenter',
            ]
        },
        'table': {
            'contentToolbar': ['tableColumn', 'tableRow', 'mergeTableCells', 'tableProperties', 'tableCellProperties'],
        },
        'heading': {
            'options': [
                {'model': 'paragraph', 'title': 'Paragraph', 'class': 'ck-heading_paragraph'},
                {'model': 'heading1', 'view': 'h1', 'title': 'Heading 1', 'class': 'ck-heading_heading1'},
                {'model': 'heading2', 'view': 'h2', 'title': 'Heading 2', 'class': 'ck-heading_heading2'},
                {'model': 'heading3', 'view': 'h3', 'title': 'Heading 3', 'class': 'ck-heading_heading3'}
            ]
        }
    }
}
CKEDITOR_5_FILE_STORAGE = "django.core.files.storage.FileSystemStorage"
