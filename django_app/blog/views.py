"""
Blog Views
Thin Views - Hauptsächlich Template Rendering
"""
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.contrib import messages
from django.db.models import Q
from .models import BlogPost, BlogCategory, EmailSubscriber


def blog_list(request):
    """Blog Übersicht - Alle veröffentlichten Posts"""
    posts = BlogPost.objects.filter(status='published').select_related('category', 'author')
    categories = BlogCategory.objects.all()
    
    # Optional: Search Funktion
    search_query = request.GET.get('q', '')
    if search_query:
        posts = posts.filter(
            Q(title__icontains=search_query) | 
            Q(excerpt__icontains=search_query) |
            Q(content_markdown__icontains=search_query)
        )
    
    context = {
        'posts': posts,
        'categories': categories,
        'search_query': search_query,
    }
    return render(request, 'blog/list.html', context)


def blog_detail(request, slug):
    """Blog Detailansicht mit SEO-Meta-Tags"""
    post = get_object_or_404(
        BlogPost.objects.select_related('category', 'author').prefetch_related('tags'),
        slug=slug,
        status='published'
    )
    
    # View Counter erhöhen
    post.view_count += 1
    post.save(update_fields=['view_count'])
    
    # Related Posts (gleiche Kategorie)
    related_posts = BlogPost.objects.filter(
        category=post.category,
        status='published'
    ).exclude(id=post.id)[:3]
    
    context = {
        'post': post,
        'related_posts': related_posts,
    }
    return render(request, 'blog/detail.html', context)


def blog_category(request, category_slug):
    """Blog Posts nach Kategorie gefiltert"""
    category = get_object_or_404(BlogCategory, slug=category_slug)
    posts = BlogPost.objects.filter(
        category=category,
        status='published'
    ).select_related('author')
    
    context = {
        'category': category,
        'posts': posts,
    }
    return render(request, 'blog/category.html', context)


def subscribe_email(request):
    """
    HTMX-gestützte Email Subscription
    POST-Only View
    """
    if request.method == 'POST':
        email = request.POST.get('email', '').strip().lower()
        source = request.POST.get('source', 'blog')
        
        if not email:
            if request.htmx:
                return HttpResponse(
                    '<p class="text-red-500 text-sm mt-2">Bitte gib eine E-Mail-Adresse ein.</p>',
                    status=400
                )
            messages.error(request, 'Bitte gib eine E-Mail-Adresse ein.')
            return render(request, 'blog/list.html')
        
        # Email Subscriber erstellen oder aktualisieren
        subscriber, created = EmailSubscriber.objects.get_or_create(
            email=email,
            defaults={'source': source}
        )
        
        if created:
            if request.htmx:
                return HttpResponse(
                    '<p class="text-green-600 text-sm mt-2">✅ Erfolgreich angemeldet! Check deine Inbox.</p>'
                )
            messages.success(request, 'Erfolgreich für den Newsletter angemeldet!')
        else:
            if request.htmx:
                return HttpResponse(
                    '<p class="text-yellow-600 text-sm mt-2">⚠️ Diese E-Mail ist bereits angemeldet.</p>'
                )
            messages.info(request, 'Diese E-Mail ist bereits angemeldet.')
        
        return render(request, 'blog/list.html')
    
    # GET Request -> Redirect to blog list
    return render(request, 'blog/list.html')


def landing_page(request):
    """
    Email-Capture Landing Page
    Einfache, fokussierte Seite nur für E-Mail-Erfassung
    """
    return render(request, 'blog/landing.html')
