"""
Blog Admin Panel Views
Nur für Staff/Superuser zugänglich
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import UserPassesTestMixin
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, TemplateView
from django.contrib import messages
from django.urls import reverse_lazy
from django.db.models import Count, Sum
from .models import BlogPost, BlogCategory, EmailSubscriber
from analyses.models import Analysis
from accounts.models import User


class StaffRequiredMixin(UserPassesTestMixin):
    """Mixin: Nur Staff/Superuser haben Zugriff"""
    def test_func(self):
        return self.request.user.is_staff or self.request.user.is_superuser
    
    def handle_no_permission(self):
        messages.error(self.request, '⛔ Kein Zugriff auf das Admin-Panel.')
        return redirect('questionnaire:home')


class AdminDashboardView(StaffRequiredMixin, TemplateView):
    """
    Admin Dashboard - Übersicht über wichtige Metriken
    """
    template_name = 'blog/admin/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Statistiken
        context['total_users'] = User.objects.count()
        context['total_analyses'] = Analysis.objects.count()
        context['total_blog_posts'] = BlogPost.objects.count()
        context['published_posts'] = BlogPost.objects.filter(status='published').count()
        context['draft_posts'] = BlogPost.objects.filter(status='draft').count()
        context['total_subscribers'] = EmailSubscriber.objects.filter(is_subscribed=True).count()
        
        # Neueste Blog Posts
        context['recent_posts'] = BlogPost.objects.select_related('author', 'category').order_by('-created_at')[:5]
        
        # Top Blog Posts (nach Views)
        context['top_posts'] = BlogPost.objects.filter(status='published').order_by('-views_count')[:5]
        
        # Neueste Subscriber
        context['recent_subscribers'] = EmailSubscriber.objects.filter(is_subscribed=True).order_by('-subscribed_at')[:5]
        
        return context


class BlogPostListView(StaffRequiredMixin, ListView):
    """Liste aller Blog Posts (inkl. Drafts)"""
    model = BlogPost
    template_name = 'blog/admin/post_list.html'
    context_object_name = 'posts'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = BlogPost.objects.select_related('author', 'category').order_by('-created_at')
        
        # Filter nach Status
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        
        # Suche
        search = self.request.GET.get('q')
        if search:
            queryset = queryset.filter(title__icontains=search)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_filter'] = self.request.GET.get('status', '')
        context['search_query'] = self.request.GET.get('q', '')
        return context


class BlogPostCreateView(StaffRequiredMixin, CreateView):
    """Neuen Blog Post erstellen"""
    model = BlogPost
    template_name = 'blog/admin/post_form.html'
    fields = ['title', 'slug', 'category', 'excerpt', 'content_markdown', 'featured_image', 
              'video_url', 'podcast_url', 'status', 'author_name', 'meta_title', 'meta_description', 'meta_keywords']
    success_url = reverse_lazy('blog:admin_posts')
    
    def form_valid(self, form):
        form.instance.author = self.request.user
        messages.success(self.request, f'✓ Blog Post "{form.instance.title}" wurde erstellt.')
        return super().form_valid(form)


class BlogPostUpdateView(StaffRequiredMixin, UpdateView):
    """Blog Post bearbeiten"""
    model = BlogPost
    template_name = 'blog/admin/post_form.html'
    fields = ['title', 'slug', 'category', 'excerpt', 'content_markdown', 'featured_image', 
              'video_url', 'podcast_url', 'status', 'author_name', 'meta_title', 'meta_description', 'meta_keywords']
    success_url = reverse_lazy('blog:admin_posts')
    
    def form_valid(self, form):
        messages.success(self.request, f'✓ Blog Post "{form.instance.title}" wurde aktualisiert.')
        return super().form_valid(form)


class BlogPostDeleteView(StaffRequiredMixin, DeleteView):
    """Blog Post löschen"""
    model = BlogPost
    template_name = 'blog/admin/post_confirm_delete.html'
    success_url = reverse_lazy('blog:admin_posts')
    
    def delete(self, request, *args, **kwargs):
        post = self.get_object()
        messages.success(request, f'✓ Blog Post "{post.title}" wurde gelöscht.')
        return super().delete(request, *args, **kwargs)


class CategoryListView(StaffRequiredMixin, ListView):
    """Liste aller Kategorien"""
    model = BlogCategory
    template_name = 'blog/admin/category_list.html'
    context_object_name = 'categories'
    
    def get_queryset(self):
        return BlogCategory.objects.annotate(post_count=Count('posts'))


class SubscriberListView(StaffRequiredMixin, ListView):
    """Liste aller Email Subscriber"""
    model = EmailSubscriber
    template_name = 'blog/admin/subscriber_list.html'
    context_object_name = 'subscribers'
    paginate_by = 50
    
    def get_queryset(self):
        queryset = EmailSubscriber.objects.order_by('-subscribed_at')
        
        # Filter nach Status
        status = self.request.GET.get('status')
        if status == 'active':
            queryset = queryset.filter(is_subscribed=True)
        elif status == 'inactive':
            queryset = queryset.filter(is_subscribed=False)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_filter'] = self.request.GET.get('status', '')
        context['total_active'] = EmailSubscriber.objects.filter(is_subscribed=True).count()
        context['total_inactive'] = EmailSubscriber.objects.filter(is_subscribed=False).count()
        return context


class SubscriberDeleteView(StaffRequiredMixin, DeleteView):
    """Email Subscriber löschen"""
    model = EmailSubscriber
    template_name = 'blog/admin/subscriber_confirm_delete.html'
    success_url = reverse_lazy('blog:admin_subscribers')
    
    def delete(self, request, *args, **kwargs):
        subscriber = self.get_object()
        messages.success(request, f'✓ Subscriber "{subscriber.email}" wurde gelöscht.')
        return super().delete(request, *args, **kwargs)
