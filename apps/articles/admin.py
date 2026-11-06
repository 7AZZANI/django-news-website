from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from unfold.admin import ModelAdmin, TabularInline
from unfold.decorators import action, display

from .models import Article, Category, Comment, ArticleView
from .ai_service import ai_assistant



def article_badge(request):
    """Badge for Unfold sidebar showing articles waiting in review."""
    count = Article.objects.filter(status='review').count()
    return f"{count} in review" if count > 0 else None


def comment_badge(request):
    """Badge for Unfold sidebar showing pending comments."""
    count = Comment.objects.filter(status='pending').count()
    return f"{count} pending" if count > 0 else None


class CommentInline(TabularInline):
    model = Comment
    extra = 0
    fields = ('author_display', 'content', 'status', 'created_at')
    readonly_fields = ('author_display', 'created_at')
    can_delete = True

    def author_display(self, obj):
        return obj.author_name
    author_display.short_description = "Commenter"


@admin.register(Category)
class CategoryAdmin(ModelAdmin):
    list_display = (
        'name',
        'slug',
        'parent',
        'display_color',
        'article_count',
        'order',
        'is_featured',
    )
    list_filter = ('is_featured', 'parent')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    ordering = ('order', 'name')

    @display(description="Badge Color")
    def display_color(self, obj):
        colors = {
            'blue': 'bg-blue-100 text-blue-800 border-blue-200',
            'red': 'bg-red-100 text-red-800 border-red-200',
            'emerald': 'bg-emerald-100 text-emerald-800 border-emerald-200',
            'amber': 'bg-amber-100 text-amber-800 border-amber-200',
            'purple': 'bg-purple-100 text-purple-800 border-purple-200',
            'indigo': 'bg-indigo-100 text-indigo-800 border-indigo-200',
        }
        cls = colors.get(obj.color, 'bg-slate-100 text-slate-800 border-slate-200')
        return format_html(
            '<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border {}">{}</span>',
            cls,
            obj.color.capitalize()
        )

    def article_count(self, obj):
        return obj.articles.count()
    article_count.short_description = "Articles"


@admin.register(Article)
class ArticleAdmin(ModelAdmin):
    list_display = (
        'display_thumbnail',
        'title',
        'category',
        'author',
        'display_status',
        'display_breaking',
        'display_featured',
        'reading_time_display',
        'views_count',
        'published_at',
    )
    list_display_links = ('display_thumbnail', 'title')
    list_filter = (
        'status',
        'category',
        'is_breaking',
        'is_featured',
        'is_editors_pick',
        'published_at',
    )
    search_fields = (
        'title',
        'excerpt',
        'body',
        'author__username',
        'author__email',
        'author__first_name',
        'author__last_name',
    )
    date_hierarchy = 'published_at'
    prepopulated_fields = {'slug': ('title',)}
    autocomplete_fields = ('author', 'category')
    filter_horizontal = ()
    inlines = [CommentInline]
    actions = [
        'mark_as_published',
        'submit_for_review',
        'revert_to_draft',
        'toggle_breaking_news',
        'toggle_featured_status',
        'generate_ai_summary_action',
        'generate_ai_seo_action',
    ]

    fieldsets = (
        ('Editorial Headline & Lead', {
            'fields': (
                'title',
                'slug',
                'excerpt',
                'category',
                'tags',
                'author',
            )
        }),
        ('Hero Imagery', {
            'fields': (
                'featured_image',
                'image_caption',
            )
        }),
        ('Article Content', {
            'fields': (
                'body',
            )
        }),
        ('Editorial AI Assistant & Summary', {
            'fields': (
                'ai_summary',
            )
        }),
        ('Publication Workflow & Flags', {
            'fields': (
                'status',
                'published_at',
                'is_breaking',
                'is_featured',
                'is_editors_pick',
            )
        }),
        ('SEO & Social Sharing', {
            'classes': ('collapse',),
            'fields': (
                'meta_title',
                'meta_description',
            )
        }),
        ('Analytics (Read Only)', {
            'classes': ('collapse',),
            'fields': (
                'views_count',
                'reading_time',
                'created_at',
                'updated_at',
            )
        }),
    )

    readonly_fields = ('views_count', 'reading_time', 'created_at', 'updated_at')

    @display(description="Image")
    def display_thumbnail(self, obj):
        if obj.featured_image:
            return format_html(
                '<img src="{}" class="w-12 h-9 rounded object-cover border border-slate-200 dark:border-zinc-700 shadow-sm" alt="{}" />',
                obj.featured_image.url,
                obj.title
            )
        return format_html('<span class="text-xs text-slate-400">No Image</span>')

    @display(description="Status", label={
        'published': 'success',
        'review': 'warning',
        'draft': 'info',
        'archived': 'danger',
    })
    def display_status(self, obj):
        return obj.status

    @display(description="Breaking", boolean=True)
    def display_breaking(self, obj):
        return obj.is_breaking

    @display(description="Lead Story", boolean=True)
    def display_featured(self, obj):
        return obj.is_featured

    @display(description="Read Time")
    def reading_time_display(self, obj):
        return f"{obj.reading_time} min"

    # Custom Workflow Actions
    @action(description="Publish selected articles")
    def mark_as_published(self, request, queryset):
        count = queryset.update(status='published', published_at=timezone.now())
        self.message_user(request, f"{count} article(s) successfully marked as Published.")

    @action(description="Submit selected articles for review")
    def submit_for_review(self, request, queryset):
        count = queryset.update(status='review')
        self.message_user(request, f"{count} article(s) submitted for Editorial Review.")

    @action(description="Revert selected articles to draft")
    def revert_to_draft(self, request, queryset):
        count = queryset.update(status='draft')
        self.message_user(request, f"{count} article(s) reverted to Draft.")

    @action(description="Toggle Breaking News flag")
    def toggle_breaking_news(self, request, queryset):
        for article in queryset:
            article.is_breaking = not article.is_breaking
            article.save(update_fields=['is_breaking'])
        self.message_user(request, f"Breaking news flag toggled for {queryset.count()} article(s).")

    @action(description="Toggle Featured Lead Story flag")
    def toggle_featured_status(self, request, queryset):
        for article in queryset:
            article.is_featured = not article.is_featured
            article.save(update_fields=['is_featured'])
        self.message_user(request, f"Featured status toggled for {queryset.count()} article(s).")

    @action(description="🤖 Generate AI Executive Summary (3 Key Bullets)")
    def generate_ai_summary_action(self, request, queryset):
        count = 0
        for article in queryset:
            summary = ai_assistant.generate_executive_summary(article)
            if summary:
                article.ai_summary = summary
                article.save(update_fields=['ai_summary'])
                count += 1
        self.message_user(
            request,
            f"Successfully generated AI executive summaries for {count} article(s)."
        )

    @action(description="🎯 Generate AI SEO Meta (Title, Description & Tags)")
    def generate_ai_seo_action(self, request, queryset):
        count = 0
        for article in queryset:
            seo_data = ai_assistant.generate_seo_metadata(article)
            article.meta_title = seo_data['meta_title']
            article.meta_description = seo_data['meta_description']
            article.save(update_fields=['meta_title', 'meta_description'])
            if seo_data.get('suggested_tags'):
                for t in seo_data['suggested_tags']:
                    article.tags.add(t)
            count += 1
        self.message_user(
            request,
            f"Successfully generated AI SEO metadata for {count} article(s)."
        )



@admin.register(Comment)
class CommentAdmin(ModelAdmin):
    list_display = (
        'author_display',
        'email',
        'article_link',
        'short_content',
        'display_status',
        'created_at',
    )
    list_filter = ('status', 'created_at')
    search_fields = ('name', 'email', 'content', 'article__title')
    date_hierarchy = 'created_at'
    actions = ['approve_comments', 'reject_comments', 'mark_as_pending']

    fieldsets = (
        ('Article & Author', {
            'fields': (
                'article',
                'user',
                'name',
                'email',
                'ip_address',
            )
        }),
        ('Comment Details', {
            'fields': (
                'content',
                'status',
                'created_at',
            )
        }),
    )
    readonly_fields = ('created_at', 'ip_address')

    def author_display(self, obj):
        return obj.author_name
    author_display.short_description = "Author"

    @display(description="Article")
    def article_link(self, obj):
        return format_html(
            '<a href="{}" class="text-blue-600 dark:text-blue-400 hover:underline font-medium" target="_blank">{}</a>',
            obj.article.get_absolute_url(),
            obj.article.title[:45] + ('...' if len(obj.article.title) > 45 else '')
        )

    @display(description="Comment Excerpt")
    def short_content(self, obj):
        return obj.content[:75] + ('...' if len(obj.content) > 75 else '')

    @display(description="Status", label={
        'approved': 'success',
        'pending': 'warning',
        'rejected': 'danger',
    })
    def display_status(self, obj):
        return obj.status

    @action(description="Approve selected comments")
    def approve_comments(self, request, queryset):
        count = queryset.update(status='approved')
        self.message_user(request, f"{count} comment(s) approved and published.")

    @action(description="Reject selected comments")
    def reject_comments(self, request, queryset):
        count = queryset.update(status='rejected')
        self.message_user(request, f"{count} comment(s) rejected.")

    @action(description="Move back to pending queue")
    def mark_as_pending(self, request, queryset):
        count = queryset.update(status='pending')
        self.message_user(request, f"{count} comment(s) moved to pending queue.")


@admin.register(ArticleView)
class ArticleViewAdmin(ModelAdmin):
    list_display = ('article', 'ip_address', 'session_key', 'viewed_at')
    list_filter = ('viewed_at',)
    search_fields = ('article__title', 'ip_address', 'session_key')
    date_hierarchy = 'viewed_at'
    readonly_fields = ('article', 'ip_address', 'session_key', 'viewed_at')
