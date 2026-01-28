"""
Rankings Views - Benutzer-Leaderboard
"""
from django.shortcuts import render
from django.db.models import Avg, Count, Q
from accounts.models import User
from analyses.models import Analysis


def leaderboard(request):
    """
    Rankings/Leaderboard mit Top Usern nach durchschnittlichem RedFlag Score
    """
    # Base Query: Nur User mit mindestens 1 Analyse
    users = User.objects.annotate(
        total_analyses=Count('analyses'),
        avg_score=Avg('analyses__score_total')
    ).filter(total_analyses__gte=1)
    
    # Filter: Land
    country = request.GET.get('country')
    if country:
        users = users.filter(profile__country=country)
    
    # Filter: Stadt
    city = request.GET.get('city')
    if city:
        users = users.filter(profile__city__icontains=city)
    
    # Filter: Altersgruppe
    age_group = request.GET.get('age_group')
    if age_group:
        from datetime import date, timedelta
        age_ranges = {
            '18-22': (18, 22),
            '23-27': (23, 27),
            '28-32': (28, 32),
            '33-37': (33, 37),
            '38-42': (38, 42),
            '43-47': (43, 47),
            '48+': (48, 150),
        }
        if age_group in age_ranges:
            min_age, max_age = age_ranges[age_group]
            today = date.today()
            max_birthdate = today - timedelta(days=min_age*365)
            min_birthdate = today - timedelta(days=(max_age+1)*365)
            users = users.filter(profile__birthdate__range=(min_birthdate, max_birthdate))
    
    # Sortierung: Niedrigster avg_score = besser (weniger Red Flags)
    sort_by = request.GET.get('sort', 'best')
    if sort_by == 'best':
        users = users.order_by('avg_score')  # Niedrigster Score zuerst
    elif sort_by == 'worst':
        users = users.order_by('-avg_score')  # Höchster Score zuerst
    elif sort_by == 'most_analyses':
        users = users.order_by('-total_analyses')
    
    # Top 500 User
    users = users[:500]
    
    # Verfügbare Länder für Filter
    available_countries = User.objects.filter(
        analyses__isnull=False,
        profile__country__isnull=False
    ).values_list('profile__country', flat=True).distinct()
    
    context = {
        'users': users,
        'available_countries': available_countries,
        'current_country': country,
        'current_city': city,
        'current_age_group': age_group,
        'current_sort': sort_by,
        'age_groups': ['18-22', '23-27', '28-32', '33-37', '38-42', '43-47', '48+'],
    }
    
    return render(request, 'rankings/leaderboard.html', context)
