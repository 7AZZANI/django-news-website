from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from apps.core.models import CustomUser
from .models import Article, Category, Comment


class ArticleModelAndViewsTests(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            email='reporter@chronicle.com',
            username='reporter_bob',
            password='password123',
            role=CustomUser.ROLE_WRITER,
        )
        self.category = Category.objects.create(
            name='Technology',
            slug='technology',
            color='blue'
        )
        self.article = Article.objects.create(
            title='Autonomous Neural Inference Engines',
            slug='autonomous-neural-inference-engines',
            excerpt='Exploring multi-step theorem proving.',
            body='<p>Full content of the investigative article.</p>',
            category=self.category,
            author=self.user,
            status=Article.STATUS_PUBLISHED,
            published_at=timezone.now(),
        )
        self.client = Client()

    def test_reading_time_calculation(self):
        self.assertGreaterEqual(self.article.reading_time, 1)

    def test_article_detail_view(self):
        response = self.client.get(self.article.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Autonomous Neural Inference Engines')

    def test_comment_submission_pending_moderation(self):
        response = self.client.post(self.article.get_absolute_url(), {
            'name': 'Reader Person',
            'email': 'reader@example.com',
            'content': 'A well-reasoned perspective.',
            'honeypot': '',
        })
        self.assertEqual(response.status_code, 302)
        comment = Comment.objects.get(article=self.article, email='reader@example.com')
        self.assertEqual(comment.status, Comment.STATUS_PENDING)

    def test_honeypot_spam_trap(self):
        response = self.client.post(self.article.get_absolute_url(), {
            'name': 'Spambot',
            'email': 'bot@spam.com',
            'content': 'Buy cheap meds at spam.link',
            'honeypot': 'http://malicious.bot',
        })
        self.assertEqual(response.status_code, 200) # Form invalid, re-rendered
        self.assertFalse(Comment.objects.filter(email='bot@spam.com').exists())

    def test_ai_summary_and_seo_generation(self):
        from .ai_service import ai_assistant
        summary = ai_assistant.generate_executive_summary(self.article)
        self.assertTrue(len(summary) > 20)
        self.assertIn('• **', summary)

        seo = ai_assistant.generate_seo_metadata(self.article)
        self.assertTrue('meta_title' in seo)
        self.assertTrue('meta_description' in seo)
        self.assertTrue(len(seo['meta_title']) <= 65)

    def test_publish_scheduled_command(self):
        from django.core.management import call_command
        # Create an article scheduled in the past with review status
        scheduled_article = Article.objects.create(
            title='Future Breakthroughs in Supercomputing',
            slug='future-breakthroughs-in-supercomputing',
            excerpt='Quantum supremacy achieved.',
            body='<p>Full article body on supercomputing.</p>',
            category=self.category,
            author=self.user,
            status=Article.STATUS_REVIEW,
            published_at=timezone.now() - timezone.timedelta(minutes=10),
        )
        self.assertEqual(scheduled_article.status, Article.STATUS_REVIEW)

        call_command('publish_scheduled')

        scheduled_article.refresh_from_db()
        self.assertEqual(scheduled_article.status, Article.STATUS_PUBLISHED)

    def test_context_processor_caching_and_invalidation(self):
        from django.core.cache import cache
        from .context_processors import GLOBAL_CONTEXT_CACHE_KEY, get_cached_news_context

        cache.delete(GLOBAL_CONTEXT_CACHE_KEY)
        data = get_cached_news_context()
        self.assertIsNotNone(data)
        self.assertTrue(cache.get(GLOBAL_CONTEXT_CACHE_KEY) is not None)

        # Trigger signal invalidation by saving an article
        self.article.title = "Updated Title for Cache Test"
        self.article.save()
        self.assertIsNone(cache.get(GLOBAL_CONTEXT_CACHE_KEY))

