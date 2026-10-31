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
