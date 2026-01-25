"""
Blog Admin Interface
Markdown Editor mit Preview
"""
from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Count
from .models import BlogCategory, BlogPost, BlogTag, EmailSubscriber


@admin.register(BlogCategory)
class BlogCategoryAdmin(admin.ModelAdmin):
    list_display = ['icon_display', 'name', 'category_type', 'post_count', 'is_active']
    list_filter = ['category_type', 'is_active']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    
    fieldsets = (
        ('Category Info', {
            'fields': ('name', 'slug', 'category_type', 'icon', 'description')
        }),
        ('SEO', {
            'fields': ('meta_description',)
        }),
        ('Status', {
            'fields': ('is_active',)
        })
    )
    
    def icon_display(self, obj):
        return obj.icon
    icon_display.short_description = 'Icon'
    
    def post_count(self, obj):
        count = obj.posts.filter(status='published').count()
        return format_html('<strong>{}</strong> Posts', count)
    post_count.short_description = 'Veröffentlichte Posts'


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'author_display', 'status', 'published_at', 'views_count']
    list_filter = ['status', 'category', 'published_at', 'created_at']
    search_fields = ['title', 'content_markdown', 'meta_keywords']
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'published_at'
    
    fieldsets = (
        ('Content', {
            'fields': ('title', 'slug', 'category', 'excerpt', 'content_markdown')
        }),
        ('Media', {
            'fields': ('featured_image', 'video_url', 'podcast_url'),
            'classes': ('collapse',)
        }),
        ('Author', {
            'fields': ('author', 'author_name')
        }),
        ('Publishing', {
            'fields': ('status', 'published_at')
        }),
        ('SEO', {
            'fields': ('meta_title', 'meta_description', 'meta_keywords'),
            'classes': ('collapse',)
        }),
        ('Analytics', {
            'fields': ('views_count',),
            'classes': ('collapse',)
        })
    )
    
    readonly_fields = ['views_count']
    
    def author_display(self, obj):
        return obj.display_author
    author_display.short_description = 'Author'
    
    def save_model(self, request, obj, form, change):
        if not obj.author:
            obj.author = request.user
        super().save_model(request, obj, form, change)
    
    class Media:
        css = {
            'all': ('https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.2/codemirror.min.css',)
        }
        js = (
            'https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.2/codemirror.min.js',
            'https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.2/mode/markdown/markdown.min.js',
        )


@admin.register(BlogTag)
class BlogTagAdmin(admin.ModelAdmin):
    list_display = ['name', 'post_count', 'created_at']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}
    
    def post_count(self, obj):
        return obj.posts.count()
    post_count.short_description = 'Posts'


@admin.register(EmailSubscriber)
class EmailSubscriberAdmin(admin.ModelAdmin):
    list_display = ['email', 'name', 'source', 'is_verified', 'is_subscribed', 'subscribed_at']
    list_filter = ['is_verified', 'is_subscribed', 'source', 'subscribed_at']
    search_fields = ['email', 'name']
    readonly_fields = ['subscribed_at', 'verified_at']
    
    fieldsets = (
        ('Subscriber Info', {
            'fields': ('email', 'name', 'source')
        }),
        ('Status', {
            'fields': ('is_verified', 'is_subscribed')
        }),
        ('Timestamps', {
            'fields': ('subscribed_at', 'verified_at'),
            'classes': ('collapse',)
        })
    )
    
    actions = ['mark_as_verified', 'mark_as_unsubscribed']
    
    def mark_as_verified(self, request, queryset):
        from django.utils import timezone
        queryset.update(is_verified=True, verified_at=timezone.now())
    mark_as_verified.short_description = "Als verifiziert markieren"
    
    def mark_as_unsubscribed(self, request, queryset):
        queryset.update(is_subscribed=False)
    mark_as_unsubscribed.short_description = "Abmelden"
