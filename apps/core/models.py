from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.urls import reverse


class CustomUserManager(BaseUserManager):
    """Custom user manager where email is the unique identifier for auth."""

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email address must be provided.")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'admin')

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractUser):
    """
    Modern Custom User model supporting email authentication,
    editorial roles (Reader, Staff Writer, Editor, Administrator),
    author profiles, and social media links.
    """

    ROLE_READER = 'reader'
    ROLE_WRITER = 'writer'
    ROLE_EDITOR = 'editor'
    ROLE_ADMIN = 'admin'

    ROLE_CHOICES = (
        (ROLE_READER, 'Reader'),
        (ROLE_WRITER, 'Staff Writer'),
        (ROLE_EDITOR, 'Editor'),
        (ROLE_ADMIN, 'Administrator'),
    )

    email = models.EmailField(
        'Email Address',
        unique=True,
        error_messages={
            'unique': 'A user with that email already exists.',
        }
    )
    username = models.CharField(
        'Username',
        max_length=150,
        unique=True,
        help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.'
    )
    role = models.CharField(
        'Editorial Role',
        max_length=20,
        choices=ROLE_CHOICES,
        default=ROLE_READER,
        help_text='Determines permissions across publishing workflows.'
    )
    job_title = models.CharField(
        'Job Title / Beat',
        max_length=120,
        blank=True,
        help_text='e.g., Senior Tech Correspondent, Chief Political Editor'
    )
    bio = models.TextField(
        'Author Biography',
        blank=True,
        help_text='Short editorial bio shown on articles and author profile page.'
    )
    avatar = models.ImageField(
        'Profile Picture',
        upload_to='avatars/',
        blank=True,
        null=True
    )
    twitter_handle = models.CharField(
        'X (Twitter) Handle',
        max_length=50,
        blank=True,
        help_text='e.g. @janedoe'
    )
    linkedin_url = models.URLField('LinkedIn Profile', blank=True)
    website_url = models.URLField('Personal Website', blank=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-date_joined']

    def __str__(self):
        return self.get_full_name() or self.username or self.email

    def get_full_name_or_username(self):
        full = self.get_full_name().strip()
        return full if full else self.username

    def get_absolute_url(self):
        return reverse('articles:author_detail', kwargs={'username': self.username})

    @property
    def is_writer(self):
        return self.role in [self.ROLE_WRITER, self.ROLE_EDITOR, self.ROLE_ADMIN] or self.is_superuser

    @property
    def is_editor(self):
        return self.role in [self.ROLE_EDITOR, self.ROLE_ADMIN] or self.is_superuser

    @property
    def avatar_url(self):
        if self.avatar and hasattr(self.avatar, 'url'):
            return self.avatar.url
        # Fallback to an elegant SVG avatar or initials placeholder
        initials = (self.first_name[:1] + self.last_name[:1]).upper() or self.username[:2].upper() or 'U'
        return f"https://ui-avatars.com/api/?name={initials}&background=0f172a&color=ffffff&bold=true&size=128"
