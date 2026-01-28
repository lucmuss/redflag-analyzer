from django.contrib import admin
from .models import CommunityPost, PostComment, PostVote, PostReport

@admin.register(CommunityPost)
class CommunityPostAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'score', 'is_published', 'created_at']
    list_filter = ['is_published', 'created_at']
    search_fields = ['title', 'content', 'user__email']
    readonly_fields = ['created_at', 'updated_at', 'views_count', 'comments_count']
    date_hierarchy = 'created_at'

@admin.register(PostComment)
class PostCommentAdmin(admin.ModelAdmin):
    list_display = ['post', 'user', 'content_preview', 'created_at']
    list_filter = ['created_at']
    search_fields = ['content', 'user__email']
    readonly_fields = ['created_at', 'updated_at']
    
    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Content'

@admin.register(PostVote)
class PostVoteAdmin(admin.ModelAdmin):
    list_display = ['post', 'user', 'vote', 'created_at']
    list_filter = ['vote', 'created_at']
    search_fields = ['post__title', 'user__email']

@admin.register(PostReport)
class PostReportAdmin(admin.ModelAdmin):
    list_display = ['post', 'reporter', 'reason_preview', 'is_resolved', 'created_at']
    list_filter = ['is_resolved', 'created_at']
    search_fields = ['post__title', 'reporter__email', 'reason']
    readonly_fields = ['created_at']
    actions = ['mark_as_resolved']
    
    def reason_preview(self, obj):
        return obj.reason[:50] + '...' if len(obj.reason) > 50 else obj.reason
    reason_preview.short_description = 'Reason'
    
    def mark_as_resolved(self, request, queryset):
        queryset.update(is_resolved=True)
    mark_as_resolved.short_description = 'Als gelöst markieren'
