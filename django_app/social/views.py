"""
Social Sharing Views
Virales Wachstum durch Share-Funktionalität
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.urls import reverse
from django.conf import settings
from .models import SharedAnalysis
from analyses.models import Analysis
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from django.core.files.base import ContentFile


@login_required
def create_share(request, analysis_id):
    """
    Erstelle Share-Link für eine Analyse.
    Generiert OG-Image und Share-URL.
    """
    analysis = get_object_or_404(Analysis, id=analysis_id, user=request.user)
    
    # Check if already shared
    existing_share = SharedAnalysis.objects.filter(
        analysis=analysis,
        user=request.user
    ).first()
    
    if existing_share:
        share = existing_share
    else:
        # Create new share
        share = SharedAnalysis.objects.create(
            analysis=analysis,
            user=request.user,
            shared_platform=request.POST.get('platform', 'link')
        )
        
        # Generate OG Image
        image = generate_share_image(analysis)
        share.share_image.save(f'share_{share.id}.png', ContentFile(image), save=True)
        
        # Set share URL
        share.share_url = request.build_absolute_uri(share.get_absolute_url())
        share.save()
    
    # Return share URL
    if request.htmx:
        return render(request, 'social/partials/share_success.html', {'share': share})
    
    return redirect('social:share_detail', uuid=share.id)


def share_detail(request, uuid):
    """
    Public Share-Seite mit OG-Tags.
    Tracking: Views, Clicks, Conversions.
    """
    share = get_object_or_404(SharedAnalysis, id=uuid)
    
    # Increment views
    share.increment_views()
    
    # Check if user came from share (UTM tracking)
    if request.GET.get('ref') == 'share':
        share.increment_clicks()
    
    context = {
        'share': share,
        'analysis': share.analysis,
        'can_view_details': request.user.is_authenticated,
    }
    
    return render(request, 'social/share_detail.html', context)


@login_required
def my_shares(request):
    """
    Übersicht aller Shares des Users mit Stats.
    """
    shares = SharedAnalysis.objects.filter(user=request.user).select_related('analysis')
    
    # Calculate total stats
    total_views = sum(s.views_count for s in shares)
    total_clicks = sum(s.clicks_count for s in shares)
    total_conversions = sum(s.conversions_count for s in shares)
    
    context = {
        'shares': shares,
        'total_views': total_views,
        'total_clicks': total_clicks,
        'total_conversions': total_conversions,
    }
    
    return render(request, 'social/my_shares.html', context)


def generate_share_image(analysis):
    """
    Generiert OG-Image mit Score und Branding.
    PIL/Pillow für Image-Generation.
    """
    # Image dimensions (optimal für Social Media)
    width, height = 1200, 630
    
    # Create image
    img = Image.new('RGB', (width, height), color='#1F2937')  # Tailwind gray-800
    draw = ImageDraw.Draw(img)
    
    # Try to load font, fallback to default
    try:
        title_font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 80)
        score_font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 120)
        subtitle_font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 40)
    except:
        title_font = ImageFont.load_default()
        score_font = ImageFont.load_default()
        subtitle_font = ImageFont.load_default()
    
    # Draw branding
    draw.text((60, 60), "=© RedFlag Analyzer", fill='#EF4444', font=title_font)
    
    # Draw score
    score = float(analysis.score_total)
    score_color = '#10B981' if score < 2.0 else '#EF4444' if score > 3.5 else '#F59E0B'
    draw.text((60, 200), f"{score:.1f}", fill=score_color, font=score_font)
    
    # Draw subtitle
    subtitle = "Red Flag Score"
    draw.text((60, 360), subtitle, fill='#9CA3AF', font=subtitle_font)
    
    # Draw CTA
    cta = "Analysiere deine Beziehung "
    draw.text((60, 500), cta, fill='#FFFFFF', font=subtitle_font)
    
    # Save to BytesIO
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    
    return buffer.getvalue()


@login_required
def delete_share(request, uuid):
    """
    Lösche einen Share.
    """
    share = get_object_or_404(SharedAnalysis, id=uuid, user=request.user)
    share.delete()
    
    if request.htmx:
        return HttpResponse()
    
    return redirect('social:my_shares')
