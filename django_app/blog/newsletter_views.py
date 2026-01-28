"""
Newsletter Views - E-Mail Versand an Subscriber
"""
from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
import markdown
from .admin_views import StaffRequiredMixin
from .models import EmailSubscriber
from django.views.generic import TemplateView, FormView
from django import forms


class NewsletterForm(forms.Form):
    """Form für Newsletter-Erstellung"""
    subject = forms.CharField(
        label='Betreff',
        max_length=200,
        widget=forms.TextInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg'})
    )
    content_markdown = forms.CharField(
        label='Inhalt (Markdown)',
        widget=forms.Textarea(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg font-mono',
            'rows': 15,
            'placeholder': '''# Überschrift

Hallo {{ subscriber.email }},

Dies ist ein **Newsletter** von RedFlag Analyzer.

## Was ist neu?
- Feature 1
- Feature 2

[Jetzt anmelden](https://redflag-analyzer.de)

Viele Grüße,
Dein RedFlag Team'''
        })
    )
    preview_email = forms.EmailField(
        label='Test-E-Mail (Optional)',
        required=False,
        widget=forms.EmailInput(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg',
            'placeholder': 'test@example.com'
        })
    )


class NewsletterComposeView(StaffRequiredMixin, FormView):
    """Newsletter erstellen und versenden"""
    template_name = 'blog/admin/newsletter_compose.html'
    form_class = NewsletterForm
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_subscribers'] = EmailSubscriber.objects.filter(is_subscribed=True).count()
        return context
    
    def form_valid(self, form):
        subject = form.cleaned_data['subject']
        content_markdown = form.cleaned_data['content_markdown']
        preview_email = form.cleaned_data.get('preview_email')
        
        # Markdown zu HTML konvertieren
        content_html = markdown.markdown(content_markdown, extensions=['extra', 'nl2br'])
        
        # Test-E-Mail versenden
        if preview_email:
            self.send_newsletter_email(
                email=preview_email,
                subject=f'[TEST] {subject}',
                content_html=content_html
            )
            messages.success(self.request, f'✓ Test-E-Mail wurde an {preview_email} gesendet.')
            return redirect('blog:newsletter_compose')
        
        # An alle Subscriber versenden
        if 'send_all' in self.request.POST:
            subscribers = EmailSubscriber.objects.filter(is_subscribed=True)
            sent_count = 0
            
            for subscriber in subscribers:
                try:
                    self.send_newsletter_email(
                        email=subscriber.email,
                        subject=subject,
                        content_html=content_html
                    )
                    sent_count += 1
                except Exception as e:
                    messages.warning(self.request, f'⚠️ Fehler bei {subscriber.email}: {str(e)}')
            
            messages.success(self.request, f'✓ Newsletter wurde an {sent_count} Subscriber versendet!')
            return redirect('blog:admin_dashboard')
        
        return redirect('blog:newsletter_compose')
    
    def send_newsletter_email(self, email, subject, content_html):
        """Einzelne Newsletter-E-Mail versenden"""
        html_message = render_to_string('emails/newsletter_email.html', {
            'subject': subject,
            'content_html': content_html,
            'subscriber_email': email,
        })
        
        send_mail(
            subject=subject,
            message=f'Newsletter von RedFlag Analyzer\n\n{content_html}',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            html_message=html_message,
            fail_silently=False,
        )
