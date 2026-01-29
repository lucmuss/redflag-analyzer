from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Q
from .models import CommunityPost, PostComment, PostVote, PostReport

@login_required
def post_list(request):
    posts = CommunityPost.objects.filter(is_published=True).annotate(
        vote_count=Count('votes', filter=Q(votes__vote=1)) - Count('votes', filter=Q(votes__vote=-1)),
        comment_count=Count('comments')
    )
    
    # Filter: Jahr
    year = request.GET.get('year')
    if year:
        posts = posts.filter(created_at__year=year)
    
    # Filter: Land
    country = request.GET.get('country')
    if country:
        posts = posts.filter(user__profile__country=country)
    
    # Sortierung
    sort_by = request.GET.get('sort', 'newest')
    if sort_by == 'newest':
        posts = posts.order_by('-created_at')
    elif sort_by == 'popular':
        posts = posts.order_by('-vote_count', '-created_at')
    elif sort_by == 'discussed':
        posts = posts.order_by('-comment_count', '-created_at')
    else:
        posts = posts.order_by('-created_at')
    
    # Jahre für Filter
    from django.utils import timezone
    current_year = timezone.now().year
    available_years = list(range(current_year, current_year - 5, -1))
    
    # Länder für Filter
    available_countries = CommunityPost.objects.filter(
        is_published=True,
        user__profile__country__isnull=False
    ).values_list('user__profile__country', flat=True).distinct()
    
    return render(request, 'community/post_list.html', {
        'posts': posts,
        'available_years': available_years,
        'available_countries': available_countries,
        'current_year': year,
        'current_country': country,
        'current_sort': sort_by,
    })

@login_required
def post_detail(request, post_id):
    post = get_object_or_404(CommunityPost, id=post_id, is_published=True)
    comments = post.comments.filter(parent__isnull=True).order_by('-created_at')
    
    if request.method == 'POST':
        content = request.POST.get('content', '').strip()
        if content:
            PostComment.objects.create(
                post=post,
                user=request.user,
                content=content
            )
            messages.success(request, 'Kommentar hinzugefügt!')
            return redirect('community:post_detail', post_id=post.id)
    
    return render(request, 'community/post_detail.html', {
        'post': post,
        'comments': comments,
    })

@login_required
def create_post(request):
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        content = request.POST.get('content', '').strip()
        
        if title and content:
            post = CommunityPost.objects.create(
                user=request.user,
                title=title,
                content=content,
                is_published=True
            )
            messages.success(request, 'Post erstellt!')
            return redirect('community:post_detail', post_id=post.id)
        else:
            messages.error(request, 'Titel und Inhalt sind erforderlich.')
    
    return render(request, 'community/create_post.html')

@login_required
def vote_post(request, post_id):
    if request.method == 'POST':
        post = get_object_or_404(CommunityPost, id=post_id)
        vote_type = request.POST.get('vote_type', 'up')
        vote_value = 1 if vote_type == 'up' else -1
        
        vote, created = PostVote.objects.get_or_create(
            post=post,
            user=request.user,
            defaults={'vote': vote_value}
        )
        
        if not created:
            if vote.vote == vote_value:
                vote.delete()
            else:
                vote.vote = vote_value
                vote.save()
    
    return redirect(request.META.get('HTTP_REFERER', 'community:post_list'))

@login_required
def report_post(request, post_id):
    if request.method == 'POST':
        post = get_object_or_404(CommunityPost, id=post_id)
        reason = request.POST.get('reason', '').strip()
        
        if reason:
            PostReport.objects.create(
                post=post,
                reporter=request.user,
                reason=reason
            )
            messages.success(request, 'Post gemeldet. Danke für dein Feedback!')
        
    return redirect(request.META.get('HTTP_REFERER', 'community:post_list'))

@login_required
def delete_post(request, post_id):
    """Admin-only: Post löschen"""
    if not (request.user.is_staff or request.user.is_superuser):
        messages.error(request, 'Keine Berechtigung.')
        return redirect('community:post_list')
    
    if request.method == 'POST':
        post = get_object_or_404(CommunityPost, id=post_id)
        post.delete()
        messages.success(request, 'Post erfolgreich gelöscht.')
    
    return redirect('community:post_list')
