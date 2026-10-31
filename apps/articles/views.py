from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import F, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views import View
from django.views.generic import DetailView, ListView, TemplateView
from taggit.models import Tag

from apps.core.models import CustomUser
from .forms import CommentForm, SearchFilterForm
from .models import Article, ArticleView, Category, Comment


def get_client_ip(request):
    """Safely extracts client IP address accounting for reverse proxies."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


class HomeView(TemplateView):
    """
    Homepage editorial layout:
    - Hero lead article + secondary stories
    - Editors' curated picks
    - Category spotlights (Technology, Business, Politics)
    - Latest chronological feed with pagination
    """
    template_name = 'articles/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        all_published = Article.objects.published().select_related('author', 'category').prefetch_related('tags')

        # Hero lead story (prioritize is_featured, then latest)
        lead_story = all_published.filter(is_featured=True).first()
        if not lead_story:
            lead_story = all_published.first()

        # Secondary stories for hero grid (exclude lead story)
        hero_exclude_ids = [lead_story.id] if lead_story else []
        secondary_stories = all_published.exclude(id__in=hero_exclude_ids)[:4]
        hero_exclude_ids.extend([a.id for a in secondary_stories])

        # Editors' Picks
        editors_picks = all_published.filter(is_editors_pick=True).exclude(id__in=hero_exclude_ids)[:4]
        if not editors_picks.exists():
            editors_picks = all_published.exclude(id__in=hero_exclude_ids)[:4]

        # Latest feed (excluding hero lead stories to prevent repetition)
        feed_articles = all_published.exclude(id__in=hero_exclude_ids)
        paginator = Paginator(feed_articles, 6)
        page_number = self.request.GET.get('page', 1)
        latest_page = paginator.get_page(page_number)

        # Category Spotlights
        category_spotlights = []
        featured_cats = Category.objects.filter(parent__isnull=True, is_featured=True)[:3]
        for cat in featured_cats:
            cat_articles = all_published.filter(
                Q(category=cat) | Q(category__parent=cat)
            )[:4]
            if cat_articles.exists():
                category_spotlights.append({
                    'category': cat,
                    'articles': cat_articles,
                })

        context.update({
            'lead_story': lead_story,
            'secondary_stories': secondary_stories,
            'editors_picks': editors_picks,
            'latest_articles': latest_page,
            'category_spotlights': category_spotlights,
        })
        return context


class ArticleDetailView(View):
    """
    Full article reading experience with session-deduplicated view tracking,
    related story suggestions, and hybrid reader comments with anti-spam moderation.
    """
    template_name = 'articles/article_detail.html'

    def get(self, request, slug):
        article = get_object_or_404(
            Article.objects.select_related('author', 'category', 'category__parent').prefetch_related('tags'),
            slug=slug,
            status=Article.STATUS_PUBLISHED,
            published_at__lte=timezone.now()
        )

        # Track view impression (deduplicated by session)
        session_viewed = request.session.get('viewed_articles', [])
        if article.id not in session_viewed:
            ip = get_client_ip(request)
            session_key = request.session.session_key or ''
            ArticleView.objects.create(
                article=article,
                ip_address=ip,
                session_key=session_key
            )
            Article.objects.filter(id=article.id).update(views_count=F('views_count') + 1)
            article.refresh_from_db(fields=['views_count'])

            session_viewed.append(article.id)
            request.session['viewed_articles'] = session_viewed

        # Related articles (same category or shared tags)
        related_articles = Article.objects.published().filter(
            Q(category=article.category) | Q(tags__in=article.tags.all())
        ).exclude(id=article.id).distinct().select_related('author', 'category')[:3]

        if not related_articles.exists():
            related_articles = Article.objects.published().exclude(id=article.id).order_by('-published_at')[:3]

        # Approved reader comments
        comments = article.comments.approved().select_related('user').order_by('-created_at')

        # Comment form
        form = CommentForm(user=request.user)

        context = {
            'article': article,
            'related_articles': related_articles,
            'comments': comments,
            'comment_form': form,
        }
        return render(request, self.template_name, context)

    def post(self, request, slug):
        article = get_object_or_404(
            Article.objects.published(),
            slug=slug
        )

        form = CommentForm(request.POST, user=request.user)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.article = article
            comment.ip_address = get_client_ip(request)

            if request.user.is_authenticated:
                comment.user = request.user
                comment.name = request.user.get_full_name_or_username()
                comment.email = request.user.email

            comment.status = Comment.STATUS_PENDING
            comment.save()

            messages.success(
                request,
                "Thank you for your contribution! Your comment has been submitted and will appear once approved by our editorial moderators."
            )
            return redirect(f"{article.get_absolute_url()}#comments")
        else:
            # Re-render with form errors
            comments = article.comments.approved().select_related('user').order_by('-created_at')
            related_articles = Article.objects.published().filter(
                category=article.category
            ).exclude(id=article.id)[:3]

            context = {
                'article': article,
                'related_articles': related_articles,
                'comments': comments,
                'comment_form': form,
            }
            return render(request, self.template_name, context)


class CategoryDetailView(ListView):
    """
    Category archive view listing all articles within a primary category or subcategory,
    with pagination and subcategory pill filters.
    """
    template_name = 'articles/category_detail.html'
    context_object_name = 'articles'
    paginate_by = 9

    def get_queryset(self):
        self.category = get_object_or_404(Category, slug=self.kwargs['slug'])
        # Include articles belonging to this category or any of its subcategories
        cat_ids = [self.category.id] + list(self.category.subcategories.values_list('id', flat=True))
        return Article.objects.published().filter(
            category_id__in=cat_ids
        ).select_related('author', 'category').prefetch_related('tags')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        context['subcategories'] = self.category.subcategories.all()
        return context


class TagDetailView(ListView):
    """
    Tag archive listing articles associated with a specific tag.
    """
    template_name = 'articles/tag_detail.html'
    context_object_name = 'articles'
    paginate_by = 9

    def get_queryset(self):
        self.tag = get_object_or_404(Tag, slug=self.kwargs['slug'])
        return Article.objects.published().filter(
            tags__in=[self.tag]
        ).select_related('author', 'category').prefetch_related('tags')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tag'] = self.tag
        return context


class AuthorDetailView(ListView):
    """
    Author byline profile showing biography, beat, social links,
    and all articles authored by them.
    """
    template_name = 'articles/author_detail.html'
    context_object_name = 'articles'
    paginate_by = 9

    def get_queryset(self):
        self.author = get_object_or_404(CustomUser, username=self.kwargs['username'])
        return Article.objects.published().filter(
            author=self.author
        ).select_related('author', 'category').prefetch_related('tags')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['author'] = self.author
        return context


class SearchView(ListView):
    """
    Multi-faceted search and filtering across headlines, excerpts,
    body copy, categories, tags, and date ranges.
    """
    template_name = 'articles/search.html'
    context_object_name = 'articles'
    paginate_by = 9

    def get_queryset(self):
        queryset = Article.objects.published().select_related('author', 'category').prefetch_related('tags')
        form = SearchFilterForm(self.request.GET)
        self.form = form

        if form.is_valid():
            q = form.cleaned_data.get('q')
            category = form.cleaned_data.get('category')
            tag = form.cleaned_data.get('tag')
            date_range = form.cleaned_data.get('date_range')
            sort_by = form.cleaned_data.get('sort_by')

            if q:
                queryset = queryset.filter(
                    Q(title__icontains=q) |
                    Q(excerpt__icontains=q) |
                    Q(body__icontains=q) |
                    Q(author__first_name__icontains=q) |
                    Q(author__last_name__icontains=q)
                )

            if category:
                cat_ids = [category.id] + list(category.subcategories.values_list('id', flat=True))
                queryset = queryset.filter(category_id__in=cat_ids)

            if tag:
                queryset = queryset.filter(tags__name__iexact=tag)

            if date_range:
                now = timezone.now()
                if date_range == 'today':
                    queryset = queryset.filter(published_at__gte=now - timezone.timedelta(days=1))
                elif date_range == 'week':
                    queryset = queryset.filter(published_at__gte=now - timezone.timedelta(days=7))
                elif date_range == 'month':
                    queryset = queryset.filter(published_at__gte=now - timezone.timedelta(days=30))
                elif date_range == 'year':
                    queryset = queryset.filter(published_at__gte=now - timezone.timedelta(days=365))

            if sort_by == 'popular':
                queryset = queryset.order_by('-views_count', '-published_at')
            elif sort_by == 'latest':
                queryset = queryset.order_by('-published_at')
            # 'relevance' maintains search ordering

        return queryset.distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = self.form
        context['search_query'] = self.request.GET.get('q', '')
        return context
