"""
Community Forum Models
User Generated Content für Engagement
"""
from django.db import models
from django.conf import settings
from django.urls import reverse
from django.utils.text import slugify


class CommunityPost(models.Model):
    """
    User Story Posts - RedFlag Geschichten.
    Reddit-style voting system.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='community_posts'
    )
    
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, db_index=True)
    content = models.TextField(help_text="Story content")
    
    # Voting
    upvotes = models.IntegerField(default=0)
    downvotes = models.IntegerField(default=0)
    
    # Moderation
    is_anonymous = models.BooleanField(
        default=True,
        help_text="Zeige Username nicht an"
    )
    is_published = models.BooleanField(default=True)
    is_reported = models.BooleanField(default=False)
    report_count = models.IntegerField(default=0)
    
    # Stats
    views_count = models.IntegerField(default=0)
    comments_count = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'community_posts'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-upvotes']),
            models.Index(fields=['-created_at']),
            models.Index(fields=['is_published', '-upvotes']),
        ]
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)[:200] + f"-{self.pk or ''}"
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('community:post_detail', kwargs={'slug': self.slug})
    
    @property
    def score(self):
        """Reddit-style Score."""
        return self.upvotes - self.downvotes
    
    @property
    def display_username(self):
        """Zeige Username oder 'Anonym'."""
        if self.is_anonymous:
            return "Anonym"
        return self.user.username or self.user.email.split('@')[0]
    
    def increment_views(self):
        self.views_count += 1
        self.save(update_fields=['views_count'])


class PostVote(models.Model):
    """
    User Votes auf Community Posts.
    Verhindert doppeltes Voting.
    """
    VOTE_CHOICES = [
        (1, 'Upvote'),
        (-1, 'Downvote'),
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='post_votes'
    )
    post = models.ForeignKey(
        CommunityPost,
        on_delete=models.CASCADE,
        related_name='votes'
    )
    vote = models.SmallIntegerField(choices=VOTE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'post_votes'
        unique_together = [['user', 'post']]
        indexes = [
            models.Index(fields=['post', 'vote']),
        ]
    
    def __str__(self):
        vote_str = "Upvote" if self.vote == 1 else "Downvote"
        return f"{self.user.email} {vote_str} on {self.post.id}"


class PostComment(models.Model):
    """
    Kommentare auf Community Posts.
    """
    post = models.ForeignKey(
        CommunityPost,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='post_comments'
    )
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='replies',
        help_text="Für verschachtelte Kommentare"
    )
    
    content = models.TextField(max_length=1000)
    
    # Moderation
    is_published = models.BooleanField(default=True)
    is_reported = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'post_comments'
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['post', 'created_at']),
        ]
    
    def __str__(self):
        return f"Comment by {self.user.email} on {self.post.title}"


class PostReport(models.Model):
    """
    Report-System für problematische Posts/Comments.
    """
    REPORT_TYPES = [
        ('spam', 'Spam'),
        ('offensive', 'Beleidigend'),
        ('fake', 'Fake Story'),
        ('inappropriate', 'Unangemessen'),
        ('other', 'Sonstiges'),
    ]
    
    reporter = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reports_made'
    )
    post = models.ForeignKey(
        CommunityPost,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='reports'
    )
    comment = models.ForeignKey(
        PostComment,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='reports'
    )
    
    report_type = models.CharField(max_length=20, choices=REPORT_TYPES)
    reason = models.TextField(blank=True)
    
    is_resolved = models.BooleanField(default=False)
    resolved_at = models.DateTimeField(null=True, blank=True)
    resolved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reports_resolved'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'post_reports'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Report by {self.reporter.email} - {self.report_type}"
