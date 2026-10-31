from django.test import TestCase
from django.contrib.auth import get_user_model

User = get_user_model()


class CustomUserTests(TestCase):
    def test_create_user_with_email(self):
        user = User.objects.create_user(
            email='reader@example.com',
            username='reader_jane',
            password='securepassword123',
            first_name='Jane',
            last_name='Doe'
        )
        self.assertEqual(user.email, 'reader@example.com')
        self.assertEqual(user.username, 'reader_jane')
        self.assertEqual(user.role, User.ROLE_READER)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        self.assertTrue(user.check_password('securepassword123'))

    def test_create_superuser(self):
        admin = User.objects.create_superuser(
            email='admin@example.com',
            username='super_admin',
            password='adminpassword123'
        )
        self.assertEqual(admin.email, 'admin@example.com')
        self.assertEqual(admin.role, User.ROLE_ADMIN)
        self.assertTrue(admin.is_staff)
        self.assertTrue(admin.is_superuser)
