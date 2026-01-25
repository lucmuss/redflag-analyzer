"""
Blog Models
SEO-optimiert mit Markdown Support
"""
from django.db import models
from django.conf import settings
from django.utils.text import slugify
from django.urls import reverse
import markdown


class BlogCategory(models.Model):
    """
    Blog-Kategorien für Content-Typen.
    """
    CATEGORY_TYPES = [
        ('article', 'Artikel'),
        ('video', 'Videos'),
        ('podcast', 'Podcasts'),
        ('case_study', 'Case Studies'),
    ]
    
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True, db_index=True)
    category_type = models.CharField(
        max_length=20,
        choices=CATEGORY_TYPES,
        default='article'
    )
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, default='📝', help_text="Emoji Icon")
    
    # SEO
    meta_description = models.CharField(max_length=160, blank=True)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'blog_categories'
        verbose_name = 'Blog Category'
        verbose_name_plural = 'Blog Categories'
        ordering = ['name']
    
    def __str__(self):
        return f"{self.icon} {self.name}"
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('blog:category', kwargs={'slug': self.slug})


class BlogPost(models.Model):
    """
    Blog Post mit Markdown & SEO.
    """
    STATUS_CHOICES = [
        ('draft', 'Entwurf'),
        ('published', 'Veröffentlicht'),
    ]
    
    # Content
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, db_index=True)
    category = models.ForeignKey(
        BlogCategory,
        on_delete=models.CASCADE,
        related_name='posts'
    )
    
    # Markdown Content
    content_markdown = models.TextField(
        help_text="Markdown-formatted content"
    )
    content_html = models.TextField(
        blank=True,
        help_text="Auto-generated HTML from Markdown"
    )
    
    # Excerpt
    excerpt = models.TextField(
        max_length=300,
        blank=True,
        help_text="Kurze Zusammenfassung (max 300 Zeichen)"
    )
    
    # Media für Videos/Podcasts
    featured_image = models.URLField(
        blank=True,
        help_text="URL zum Featured Image"
    )
    video_url = models.URLField(
        blank=True,
        help_text="YouTube/Vimeo URL (für Video-Posts)"
    )
    podcast_url = models.URLField(
        blank=True,
        help_text="Podcast Episode URL"
    )
    
    # Author
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='blog_posts'
    )
    author_name = models.CharField(
        max_length=100,
        blank=True,
        help_text="Angezeigter Author-Name (falls abweichend)"
    )
    
    # Publishing
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft'
    )
    published_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True
    )
    
    # SEO
    meta_title = models.CharField(
        max_length=60,
        blank=True,
        help_text="SEO Title (max 60 Zeichen)"
    )
    meta_description = models.CharField(
        max_length=160,
        blank=True,
        help_text="SEO Description (max 160 Zeichen)"
    )
    meta_keywords = models.CharField(
        max_length=255,
        blank=True,
        help_text="Komma-separierte Keywords"
    )
    
    # Analytics
    views_count = models.IntegerField(default=0)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'blog_posts'
        ordering = ['-published_at', '-created_at']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['status', '-published_at']),
            models.Index(fields=['category', 'status']),
        ]
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        # Auto-generate slug
        if not self.slug:
            self.slug = slugify(self.title)
        
        # Convert Markdown to HTML
        if self.content_markdown:
            self.content_html = markdown.markdown(
                self.content_markdown,
                extensions=[
                    'markdown.extensions.extra',
                    'markdown.extensions.codehilite',
                    'markdown.extensions.toc',
                    'markdown.extensions.nl2br',
                ]
            )
        
        # Auto-generate meta fields if empty
        if not self.meta_title:
            self.meta_title = self.title[:60]
        
        if not self.meta_description and self.excerpt:
            self.meta_description = self.excerpt[:160]
        
        # Set published_at on first publish
        if self.status == 'published' and not self.published_at:
            from django.utils import timezone
            self.published_at = timezone.now()
        
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('blog:detail', kwargs={'slug': self.slug})
    
    @property
    def reading_time(self):
        """Berechne geschätzte Lesezeit (Wörter / 200 WPM)."""
        word_count = len(self.content_markdown.split())
        minutes = max(1, word_count // 200)
        return f"{minutes} Min. Lesezeit"
    
    @property
    def display_author(self):
        """Zeige author_name oder username."""
        return self.author_name or (self.author.get_full_name() if self.author else 'RedFlag Team')
    
    def increment_views(self):
        """Erhöhe View Counter."""
        self.views_count += 1
        self.save(update_fields=['views_count'])


class BlogTag(models.Model):
    """
    Tags für Blog Posts.
    """
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True, db_index=True)
    posts = models.ManyToManyField(BlogPost, related_name='tags', blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'blog_tags'
        ordering = ['name']
    
    def __str__(self):
        return f"#{self.name}"
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('blog:tag', kwargs={'slug': self.slug})


class EmailSubscriber(models.Model):
    """
    Email-Capture für Landing Page & Newsletter.
    """
    email = models.EmailField(unique=True, db_index=True)
    name = models.CharField(max_length=100, blank=True)
    
    # Source Tracking
    source = models.CharField(
        max_length=50,
        default='landing_page',
        help_text="Wo hat sich der User angemeldet?"
    )
    
    # Status
    is_verified = models.BooleanField(default=False)
    is_subscribed = models.BooleanField(default=True)
    
    # Timestamps
    subscribed_at = models.DateTimeField(auto_now_add=True)
    verified_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'email_subscribers'
        ordering = ['-subscribed_at']
    
    def __str__(self):
        return self.email
