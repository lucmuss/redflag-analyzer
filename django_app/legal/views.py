"""
Legal Views
Einfache Template Views für rechtliche Seiten
"""
from django.views.generic import TemplateView


class ImpressumView(TemplateView):
    """Impressum (§5 TMG erforderlich)"""
    template_name = 'legal/impressum.html'


class DatenschutzView(TemplateView):
    """Datenschutzerklärung (DSGVO Art. 13, 14)"""
    template_name = 'legal/datenschutz.html'


class AGBView(TemplateView):
    """Allgemeine Geschäftsbedingungen / Terms of Service"""
    template_name = 'legal/agb.html'


class DisclaimerView(TemplateView):
    """Haftungsausschluss"""
    template_name = 'legal/disclaimer.html'
