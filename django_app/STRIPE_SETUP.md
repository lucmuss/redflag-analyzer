# 💳 Stripe Payment Integration - Setup Guide

## 🚀 Quick Start

### 1. Stripe Account & API Keys

1. **Registriere auf Stripe:**
   - https://dashboard.stripe.com/register
   - Verifiziere Email-Adresse

2. **Hole API Keys:**
   - Dashboard → Developers → API keys
   - **Test Mode Keys** (für Development):
     - Publishable key: `pk_test_...`
     - Secret key: `sk_test_...`
   - **Live Mode Keys** (für Production):
     - Publishable key: `pk_live_...`
     - Secret key: `sk_live_...`

3. **`.env` File konfigurieren:**
```bash
# Stripe Configuration
STRIPE_PUBLIC_KEY=pk_test_your_publishable_key_here
STRIPE_SECRET_KEY=sk_test_your_secret_key_here
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret  # Optional für Webhooks
```

---

## 📦 Installation

```bash
cd django_app
pip install stripe==7.4.0
```

**Füge zu requirements.txt hinzu:**
```
stripe==7.4.0
```

---

## ⚙️ Django Settings

**`settings.py`:**
```python
# Stripe Configuration
STRIPE_PUBLIC_KEY = os.getenv('STRIPE_PUBLIC_KEY')
STRIPE_SECRET_KEY = os.getenv('STRIPE_SECRET_KEY')
STRIPE_WEBHOOK_SECRET = os.getenv('STRIPE_WEBHOOK_SECRET', '')

import stripe
stripe.api_key = STRIPE_SECRET_KEY
```

---

## 🏗️ Credit Packages (Product Setup)

### Option 1: Stripe Dashboard (Empfohlen für Start)

1. Dashboard → Products → "Add Product"
2. Erstelle 3 Produkte:
   - **Starter Pack:** 50 Credits - €4.99
   - **Popular Pack:** 250 Credits - €19.99 (Save 20%)
   - **Premium Pack:** 1000 Credits - €69.99 (Save 30%)

3. Kopiere Price IDs für `.env`:
```bash
STRIPE_PRICE_ID_50=price_1ABC...
STRIPE_PRICE_ID_250=price_1DEF...
STRIPE_PRICE_ID_1000=price_1GHI...
```

### Option 2: Programmatisch (für Automation)

```python
import stripe

# Erstelle Products & Prices
products = [
    {
        'name': '50 Credits - Starter Pack',
        'description': 'Perfekt für den Einstieg',
        'amount': 499,  # €4.99 in Cents
        'credits': 50,
    },
    {
        'name': '250 Credits - Popular Pack',
        'description': '20% Ersparnis - Beliebteste Option',
        'amount': 1999,  # €19.99
        'credits': 250,
    },
    {
        'name': '1000 Credits - Premium Pack',
        'description': '30% Ersparnis - Bester Wert',
        'amount': 6999,  # €69.99
        'credits': 1000,
    },
]

for product in products:
    stripe_product = stripe.Product.create(
        name=product['name'],
        description=product['description'],
        metadata={'credits': product['credits']},
    )
    
    stripe_price = stripe.Price.create(
        product=stripe_product.id,
        unit_amount=product['amount'],
        currency='eur',
    )
    
    print(f"Price ID: {stripe_price.id}")
```

---

## 🔧 Implementation

### 1. Credit Purchase View (`accounts/credit_views.py`)

**Aktualisiere für Stripe:**
```python
import stripe
from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.urls import reverse
import logging

logger = logging.getLogger(__name__)

CREDIT_PACKAGES = {
    50: {
        'name': 'Starter Pack',
        'price': 4.99,
        'price_id': settings.STRIPE_PRICE_ID_50,
    },
    250: {
        'name': 'Popular Pack',
        'price': 19.99,
        'price_id': settings.STRIPE_PRICE_ID_250,
        'discount': '20% sparen',
    },
    1000: {
        'name': 'Premium Pack',
        'price': 69.99,
        'price_id': settings.STRIPE_PRICE_ID_1000,
        'discount': '30% sparen',
    },
}

@login_required
def credit_purchase_view(request):
    """Zeige Credit Purchase Page mit Stripe."""
    return render(request, 'accounts/credit_purchase.html', {
        'packages': CREDIT_PACKAGES,
        'stripe_public_key': settings.STRIPE_PUBLIC_KEY,
    })

@login_required
@require_POST
def create_checkout_session(request, credits):
    """Erstelle Stripe Checkout Session."""
    try:
        package = CREDIT_PACKAGES.get(credits)
        if not package:
            return JsonResponse({'error': 'Invalid package'}, status=400)
        
        # Erstelle Stripe Checkout Session
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price': package['price_id'],
                'quantity': 1,
            }],
            mode='payment',
            success_url=request.build_absolute_uri(
                reverse('accounts:payment_success')
            ) + '?session_id={CHECKOUT_SESSION_ID}',
            cancel_url=request.build_absolute_uri(
                reverse('accounts:credit_purchase')
            ),
            client_reference_id=str(request.user.id),
            metadata={
                'credits': credits,
                'user_id': request.user.id,
            },
        )
        
        logger.info(f"Checkout session created: {checkout_session.id} for user {request.user.id}")
        
        return JsonResponse({'sessionId': checkout_session.id})
        
    except Exception as e:
        logger.error(f"Stripe checkout error: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)

@login_required
def payment_success_view(request):
    """Handle successful payment."""
    session_id = request.GET.get('session_id')
    
    if session_id:
        try:
            # Retrieve session von Stripe
            session = stripe.checkout.Session.retrieve(session_id)
            
            # Hole Metadaten
            credits = int(session.metadata.get('credits', 0))
            
            # WICHTIG: Füge Credits nur hinzu wenn Payment erfolgreich
            if session.payment_status == 'paid':
                request.user.add_credits(credits)
                logger.info(f"Credits added: {credits} for user {request.user.id}")
        
        except Exception as e:
            logger.error(f"Error retrieving session: {str(e)}")
    
    return render(request, 'accounts/payment_success.html', {
        'credits_added': credits if session_id else 0
    })
```

### 2. URLs aktualisieren (`accounts/urls.py`)

```python
from .credit_views import credit_purchase_view, create_checkout_session, payment_success_view

urlpatterns = [
    # ... existing URLs
    path('credits/buy/', credit_purchase_view, name='credit_purchase'),
    path('credits/checkout/<int:credits>/', create_checkout_session, name='create_checkout'),
    path('credits/success/', payment_success_view, name='payment_success'),
]
```

### 3. Template mit Stripe Checkout (`templates/accounts/credit_purchase.html`)

```html
{% extends 'base.html' %}

{% block title %}Credits kaufen - RedFlag Analyzer{% endblock %}

{% block content %}
<div class="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
    <h1 class="text-4xl font-bold text-center mb-12">💳 Credits kaufen</h1>
    
    <div class="grid md:grid-cols-3 gap-8 mb-12">
        {% for credits, package in packages.items %}
        <div class="bg-white rounded-lg shadow-xl p-8 {% if credits == 250 %}border-4 border-red-flag transform scale-105{% endif %}">
            {% if package.discount %}
            <div class="bg-red-flag text-white text-sm font-bold px-3 py-1 rounded-full inline-block mb-4">
                {{ package.discount }}
            </div>
            {% endif %}
            
            <h3 class="text-2xl font-bold mb-4">{{ package.name }}</h3>
            <div class="text-5xl font-bold text-red-flag mb-2">{{ credits }}</div>
            <div class="text-gray-600 mb-6">Credits</div>
            
            <div class="text-3xl font-bold mb-6">€{{ package.price }}</div>
            
            <button 
                onclick="checkout({{ credits }})"
                class="w-full bg-red-flag hover:bg-red-600 text-white font-bold py-3 px-6 rounded-lg transition transform hover:scale-105"
            >
                Jetzt kaufen
            </button>
        </div>
        {% endfor %}
    </div>
</div>

<script src="https://js.stripe.com/v3/"></script>
<script>
const stripe = Stripe('{{ stripe_public_key }}');

async function checkout(credits) {
    try {
        const response = await fetch(`/profile/credits/checkout/${credits}/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': '{{ csrf_token }}'
            }
        });
        
        const data = await response.json();
        
        if (data.error) {
            alert('Fehler: ' + data.error);
            return;
        }
        
        // Redirect zu Stripe Checkout
        const result = await stripe.redirectToCheckout({
            sessionId: data.sessionId
        });
        
        if (result.error) {
            alert(result.error.message);
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Ein Fehler ist aufgetreten.');
    }
}
</script>
{% endblock %}
```

---

## 🔔 Webhooks (Empfohlen für Production)

Webhooks sorgen dafür, dass Credits sicher hinzugefügt werden, auch wenn User Fenster schließt.

### 1. Webhook Endpoint erstellen

```python
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
import json

@csrf_exempt
def stripe_webhook(request):
    """Handle Stripe Webhooks."""
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError:
        return HttpResponse(status=400)
    
    # Handle specific events
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        
        # Hole User & Credits
        user_id = int(session['metadata']['user_id'])
        credits = int(session['metadata']['credits'])
        
        # Füge Credits hinzu (nur wenn paid!)
        if session['payment_status'] == 'paid':
            from accounts.models import User
            user = User.objects.get(id=user_id)
            user.add_credits(credits)
            logger.info(f"Webhook: Credits added {credits} for user {user_id}")
    
    return HttpResponse(status=200)
```

### 2. Webhook in Stripe Dashboard konfigurieren

1. Dashboard → Developers → Webhooks
2. "Add endpoint"
3. URL: `https://your-domain.com/webhooks/stripe/`
4. Events: `checkout.session.completed`
5. Kopiere Signing Secret → `.env` als `STRIPE_WEBHOOK_SECRET`

---

## 🧪 Testing

### Test Cards (Stripe Test Mode)

```
Erfolgreiche Zahlung: 4242 4242 4242 4242
Ablehnung: 4000 0000 0000 0002
3D Secure: 4000 0027 6000 3184
```

**Weitere Test-Infos:** https://stripe.com/docs/testing

### Manual Testing Checklist

- [ ] Credit Packages werden korrekt angezeigt
- [ ] Stripe Checkout öffnet sich
- [ ] Erfolgreicher Payment fügt Credits hinzu
- [ ] Abgebrochener Payment fügt keine Credits hinzu
- [ ] Webhook funktioniert (Test in Stripe Dashboard)
- [ ] Logging funktioniert

---

## 🚀 Production Deployment

1. **Wechsle zu Live Mode** in Stripe Dashboard
2. **Update `.env`** mit Live Keys:
```bash
STRIPE_PUBLIC_KEY=pk_live_...
STRIPE_SECRET_KEY=sk_live_...
```

3. **Aktiviere Live Webhooks**

4. **Business Verification** (für größere Volumina)

---

## 💡 Best Practices

1. **Niemals Secret Key im Frontend!** Nur Public Key
2. **Immer Webhooks nutzen** für Production (zuverlässiger)
3. **Idempotenz prüfen** - Credits nicht doppelt hinzufügen
4. **Logging aktivieren** für alle Transaktionen
5. **Test Mode verwenden** für Development
6. **Rate Limiting** für Checkout-Endpoints

---

## 🔒 Security Checklist

- [ ] Stripe Secret Key nur in .env (nie in Git!)
- [ ] Webhook Signature Verification aktiviert
- [ ] CSRF Protection für alle POST-Endpoints
- [ ] User Authentication für Credit Purchase
- [ ] Logging für alle Transaktionen
- [ ] SSL/HTTPS für Production

---

## 📊 Monitoring

**Wichtige Metriken in Stripe Dashboard:**
- Successful Payments
- Failed Payments
- Average Transaction Value
- Revenue
- Webhook Delivery Success Rate

**Django Logging:**
```python
# Check logs für Transaktionen
tail -f django_app/logs/django.log | grep "Checkout session"
```
