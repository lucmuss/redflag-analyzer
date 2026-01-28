"""
Context Processor für Business/Company-Informationen
Macht .env Business-Variablen global in allen Templates verfügbar
"""
import os


def business_info(request):
    """
    Fügt Business/Company-Informationen zu jedem Template-Context hinzu
    """
    return {
        'BUSINESS': {
            'name': os.getenv('COMPANY_NAME', 'RedFlag Analyzer'),
            'legal_form': os.getenv('COMPANY_LEGAL_FORM', 'Einzelunternehmen'),
            'owner': os.getenv('COMPANY_OWNER', 'Max Mustermann'),
            'street': os.getenv('COMPANY_STREET', 'Musterstraße 123'),
            'zip': os.getenv('COMPANY_ZIP', '12345'),
            'city': os.getenv('COMPANY_CITY', 'Musterstadt'),
            'country': os.getenv('COMPANY_COUNTRY', 'Deutschland'),
            'email': os.getenv('COMPANY_EMAIL', 'info@redflag-analyzer.de'),
            'phone': os.getenv('COMPANY_PHONE', '+49 (0) 123 456789'),
            'support_email': os.getenv('COMPANY_SUPPORT_EMAIL', 'support@redflag-analyzer.de'),
            'website': os.getenv('COMPANY_WEBSITE', 'https://redflag-analyzer.de'),
            'twitter': os.getenv('COMPANY_TWITTER', ''),
            'instagram': os.getenv('COMPANY_INSTAGRAM', ''),
            'linkedin': os.getenv('COMPANY_LINKEDIN', ''),
        }
    }
