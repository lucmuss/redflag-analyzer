"""
Analytics Context Processor
Stellt Analytics Settings in allen Templates zur Verfügung
"""
from .models import AnalyticsSettings


def analytics_settings(request):
    """
    Fügt Analytics Settings zu jedem Template Context hinzu.
    Ermöglicht einfachen Zugriff auf GA und Hotjar IDs in Templates.
    """
    try:
        settings = AnalyticsSettings.load()
        return {
            'analytics_settings': settings,
            'ga_enabled': settings.ga_enabled and settings.google_analytics_id,
            'hotjar_enabled': settings.hotjar_enabled and settings.hotjar_id,
        }
    except:
        return {
            'analytics_settings': None,
            'ga_enabled': False,
            'hotjar_enabled': False,
        }
