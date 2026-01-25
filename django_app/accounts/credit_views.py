"""
Credit Purchase Views
"""
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.contrib import messages


class CreditPurchaseView(LoginRequiredMixin, TemplateView):
    """
    Credits kaufen Seite
    Zeigt verschiedene Credit-Pakete an
    """
    template_name = 'accounts/credit_purchase.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Credit Pakete definieren
        context['credit_packages'] = [
            {
                'credits': 1,
                'price': 2.99,
                'popular': False,
                'description': 'Perfekt zum Testen',
                'features': ['1 Analyse freischalten', 'Detaillierte Auswertung', 'Top Red Flags'],
            },
            {
                'credits': 5,
                'price': 12.99,
                'popular': True,
                'description': 'Beliebteste Option',
                'savings': '13%',
                'features': ['5 Analysen freischalten', 'Spare 13% gegenüber Einzelkauf', 'Detaillierte Auswertungen', 'Alle Features inklusive'],
            },
            {
                'credits': 10,
                'price': 22.99,
                'popular': False,
                'description': 'Bestes Preis-Leistungs-Verhältnis',
                'savings': '23%',
                'features': ['10 Analysen freischalten', 'Spare 23% gegenüber Einzelkauf', '30 Tage Gültigkeit', 'Priority Support'],
            },
            {
                'credits': 20,
                'price': 39.99,
                'popular': False,
                'description': 'Für Power-User',
                'savings': '33%',
                'features': ['20 Analysen freischalten', 'Spare 33% gegenüber Einzelkauf', '60 Tage Gültigkeit', 'VIP Support'],
            },
        ]
        
        context['user_credits'] = self.request.user.credits
        
        return context


def purchase_credits(request, package_id):
    """
    Placeholder für Credit-Kauf
    In der finalen Version integriert mit Zahlungsanbieter (Stripe, PayPal, etc.)
    """
    if not request.user.is_authenticated:
        messages.error(request, 'Bitte melde dich an, um Credits zu kaufen.')
        return redirect('account_login')
    
    # Pakete definieren (könnte später aus DB kommen)
    packages = {
        '1': {'credits': 1, 'price': 2.99},
        '5': {'credits': 5, 'price': 12.99},
        '10': {'credits': 10, 'price': 22.99},
        '20': {'credits': 20, 'price': 39.99},
    }
    
    package = packages.get(str(package_id))
    
    if not package:
        messages.error(request, 'Ungültiges Credit-Paket.')
        return redirect('accounts:credit_purchase')
    
    # TODO: Hier würde die Zahlungsintegration stattfinden
    # Für jetzt zeigen wir nur eine Info-Nachricht
    messages.info(
        request, 
        f'💳 Zahlungsprozess für {package["credits"]} Credits ({package["price"]}€) würde hier starten. '
        f'Zahlungsintegration (Stripe/PayPal) wird noch implementiert.'
    )
    
    return redirect('accounts:credit_purchase')
