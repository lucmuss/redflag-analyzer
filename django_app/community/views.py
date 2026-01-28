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
    ).order_by('-created_at')
    
    return render(request, 'community/post_list.html', {
        'posts': posts,
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
