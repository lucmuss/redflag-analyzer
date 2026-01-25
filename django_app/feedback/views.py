"""
Feedback Views
"""
from django.views.generic import CreateView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.contrib import messages
from .models import Feedback


class FeedbackCreateView(LoginRequiredMixin, CreateView):
    """
    View zum Erstellen von Feedback/Bug-Reports.
    """
    model = Feedback
    fields = ['feedback_type', 'subject', 'message']
    template_name = 'feedback/create.html'
    success_url = reverse_lazy('questionnaire:home')
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(
            self.request,
            'Vielen Dank für dein Feedback! Wir werden uns darum kümmern.'
        )
        return super().form_valid(form)


class FeedbackListView(LoginRequiredMixin, ListView):
    """
    View um eigene Feedbacks anzuzeigen.
    """
    model = Feedback
    template_name = 'feedback/list.html'
    context_object_name = 'feedbacks'
    paginate_by = 10
    
    def get_queryset(self):
        return Feedback.objects.filter(user=self.request.user)
